from collections.abc import Mapping
from datetime import timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.core import mail
from django.utils import timezone

from apps.accounts.factories import UserFactory
from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.orders.models import Order
from apps.payments.models import PaymentAttempt, WebhookEvent
from apps.payments.providers import CheckoutSessionResult, ProviderPaymentState
from apps.payments.services import (
    cancel_customer_order,
    create_checkout_session,
    process_webhook_event,
    reconcile_payment_attempt,
)


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0
        self.expired_sessions: list[str] = []
        self.refund_calls: list[tuple[str, int, str]] = []
        self.state = ProviderPaymentState(
            session_id="cs_test_fictional",
            status="open",
            payment_status="unpaid",
            payment_intent_id="",
        )

    def create_checkout_session(
        self, *, order: Order, attempt_id: str, idempotency_key: str
    ) -> CheckoutSessionResult:
        self.calls += 1
        return CheckoutSessionResult(
            session_id="cs_test_fictional",
            url="https://checkout.stripe.com/c/pay/cs_test_fictional",
            expires_at=timezone.now() + timedelta(minutes=30),
        )

    def construct_event(self, *, payload: bytes, signature: str) -> Mapping[str, Any]:
        raise NotImplementedError

    def refund(self, *, payment_intent_id: str, amount_minor: int, idempotency_key: str) -> str:
        self.refund_calls.append((payment_intent_id, amount_minor, idempotency_key))
        return "re_test_fictional"

    def expire_checkout_session(self, *, session_id: str) -> None:
        self.expired_sessions.append(session_id)

    def retrieve_payment_state(self, *, session_id: str) -> ProviderPaymentState:
        return self.state


def checkout_event(event_id: str, event_type: str, *, paid: bool = False) -> dict[str, Any]:
    return {
        "id": event_id,
        "type": event_type,
        "livemode": False,
        "data": {
            "object": {
                "id": "cs_test_fictional",
                "payment_status": "paid" if paid else "unpaid",
                "payment_intent": "pi_test_fictional" if paid else None,
            }
        },
    }


@pytest.mark.django_db
def test_checkout_session_creation_is_locally_and_provider_idempotent() -> None:
    order = cast(Order, OrderFactory())
    provider = FakeProvider()

    first, created = create_checkout_session(
        order=order, idempotency_key="checkout-key-0001", provider=provider
    )
    second, created_again = create_checkout_session(
        order=order, idempotency_key="checkout-key-0001", provider=provider
    )

    assert created is True
    assert created_again is False
    assert first.pk == second.pk
    assert first.status == PaymentAttempt.Status.OPEN
    assert provider.calls == 1

    resumed, resumed_created = create_checkout_session(
        order=order, idempotency_key="different-key-0002", provider=provider
    )
    assert resumed.pk == first.pk
    assert resumed_created is False
    assert provider.calls == 1


@pytest.mark.django_db
def test_paid_webhook_confirms_once_and_duplicate_event_is_a_noop(
    django_capture_on_commit_callbacks: Any,
) -> None:
    order = cast(Order, OrderFactory(customer_email="paid@example.test"))
    PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="a" * 64,
        provider_checkout_session_id="cs_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.OPEN,
    )
    event = checkout_event("evt_paid_once", "checkout.session.completed", paid=True)

    with django_capture_on_commit_callbacks(execute=True):
        assert process_webhook_event(event) is True
        assert process_webhook_event(event) is False
    order.refresh_from_db()
    attempt = PaymentAttempt.objects.get(order=order)
    assert order.status == Order.Status.CONFIRMED
    assert attempt.status == PaymentAttempt.Status.PAID
    assert attempt.provider_payment_intent_id == "pi_test_fictional"
    assert WebhookEvent.objects.count() == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["paid@example.test"]


@pytest.mark.django_db
def test_expired_session_cancels_order_and_restores_stock_once(
    django_capture_on_commit_callbacks: Any,
) -> None:
    order = cast(Order, OrderFactory(customer_email="failed@example.test"))
    item = OrderItemFactory(
        order=order,
        quantity=2,
        line_subtotal=Decimal("1700.00"),
        line_total=Decimal("1700.00"),
    )
    inventory = cast(
        InventoryRecord,
        InventoryRecordFactory(variant=item.variant, available_quantity=3),
    )
    PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="b" * 64,
        provider_checkout_session_id="cs_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.OPEN,
    )

    with django_capture_on_commit_callbacks(execute=True):
        assert process_webhook_event(checkout_event("evt_expired", "checkout.session.expired"))
    order.refresh_from_db()
    inventory.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert order.stock_restored is True
    assert inventory.available_quantity == 5
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["failed@example.test"]

    assert process_webhook_event(
        checkout_event("evt_late_paid", "checkout.session.completed", paid=True)
    )
    order.refresh_from_db()
    inventory.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert inventory.available_quantity == 5
    assert WebhookEvent.objects.get(provider_event_id="evt_late_paid").outcome == (
        "manual_review_paid_cancelled_order"
    )


@pytest.mark.django_db
def test_failure_event_after_payment_does_not_downgrade_paid_order() -> None:
    order = cast(Order, OrderFactory())
    attempt = PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="c" * 64,
        provider_checkout_session_id="cs_test_fictional",
        provider_payment_intent_id="pi_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.PAID,
    )
    order.status = Order.Status.CONFIRMED
    order.save(update_fields=("status", "updated_at"))

    assert process_webhook_event(
        checkout_event("evt_out_of_order_failure", "checkout.session.async_payment_failed")
    )

    attempt.refresh_from_db()
    order.refresh_from_db()
    assert attempt.status == PaymentAttempt.Status.PAID
    assert order.status == Order.Status.CONFIRMED
    assert (
        WebhookEvent.objects.get(provider_event_id="evt_out_of_order_failure").outcome
        == "ignored_failure_after_payment"
    )


@pytest.mark.django_db
def test_confirmed_customer_cancellation_refunds_before_releasing_stock(
    django_capture_on_commit_callbacks: Any,
) -> None:
    user = UserFactory()
    order = cast(Order, OrderFactory(user=user, status=Order.Status.CONFIRMED))
    item = OrderItemFactory(order=order, quantity=2)
    inventory = cast(
        InventoryRecord,
        InventoryRecordFactory(variant=item.variant, available_quantity=3),
    )
    attempt = PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="d" * 64,
        provider_checkout_session_id="cs_test_fictional",
        provider_payment_intent_id="pi_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.PAID,
    )
    provider = FakeProvider()

    with django_capture_on_commit_callbacks(execute=True):
        cancelled = cancel_customer_order(order=order, actor=user, provider=provider)

    attempt.refresh_from_db()
    inventory.refresh_from_db()
    assert cancelled.status == Order.Status.CANCELLED
    assert cancelled.stock_restored is True
    assert inventory.available_quantity == 5
    assert attempt.status == PaymentAttempt.Status.REFUNDED
    assert attempt.provider_refund_id == "re_test_fictional"
    assert provider.refund_calls == [
        ("pi_test_fictional", int(order.total * 100), f"refund-{attempt.public_id}")
    ]
    assert len(mail.outbox) == 1
    assert "refund issued" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_reconciliation_repairs_paid_order_and_sends_confirmation(
    django_capture_on_commit_callbacks: Any,
) -> None:
    order = cast(Order, OrderFactory(customer_email="buyer@example.test"))
    attempt = PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="e" * 64,
        provider_checkout_session_id="cs_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.OPEN,
    )
    provider = FakeProvider()
    provider.state = ProviderPaymentState(
        session_id="cs_test_fictional",
        status="complete",
        payment_status="paid",
        payment_intent_id="pi_reconciled",
    )

    with django_capture_on_commit_callbacks(execute=True):
        outcome = reconcile_payment_attempt(attempt=attempt, provider=provider)

    order.refresh_from_db()
    attempt.refresh_from_db()
    assert outcome == "confirmed_paid_order"
    assert order.status == Order.Status.CONFIRMED
    assert attempt.status == PaymentAttempt.Status.PAID
    assert attempt.provider_payment_intent_id == "pi_reconciled"
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["buyer@example.test"]
