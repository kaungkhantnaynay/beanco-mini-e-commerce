from collections.abc import Mapping
from datetime import timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.utils import timezone

from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord
from apps.orders.factories import OrderFactory, OrderItemFactory
from apps.orders.models import Order
from apps.payments.models import PaymentAttempt, WebhookEvent
from apps.payments.providers import CheckoutSessionResult
from apps.payments.services import create_checkout_session, process_webhook_event


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

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
        raise NotImplementedError


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
def test_paid_webhook_confirms_once_and_duplicate_event_is_a_noop() -> None:
    order = cast(Order, OrderFactory())
    PaymentAttempt.objects.create(
        order=order,
        idempotency_key_hash="a" * 64,
        provider_checkout_session_id="cs_test_fictional",
        amount=order.total,
        status=PaymentAttempt.Status.OPEN,
    )
    event = checkout_event("evt_paid_once", "checkout.session.completed", paid=True)

    assert process_webhook_event(event) is True
    assert process_webhook_event(event) is False
    order.refresh_from_db()
    attempt = PaymentAttempt.objects.get(order=order)
    assert order.status == Order.Status.CONFIRMED
    assert attempt.status == PaymentAttempt.Status.PAID
    assert attempt.provider_payment_intent_id == "pi_test_fictional"
    assert WebhookEvent.objects.count() == 1


@pytest.mark.django_db
def test_expired_session_cancels_order_and_restores_stock_once() -> None:
    order = cast(Order, OrderFactory())
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

    assert process_webhook_event(checkout_event("evt_expired", "checkout.session.expired"))
    order.refresh_from_db()
    inventory.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert order.stock_restored is True
    assert inventory.available_quantity == 5

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
