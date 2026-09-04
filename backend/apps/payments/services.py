import hashlib
from collections.abc import Mapping
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.orders.models import Order
from apps.orders.services import transition_order, validate_idempotency_key

from .models import PaymentAttempt, WebhookEvent
from .notifications import send_order_confirmation, send_payment_failure, send_refund_confirmation
from .providers import PaymentProvider


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def create_checkout_session(
    *, order: Order, idempotency_key: str, provider: PaymentProvider
) -> tuple[PaymentAttempt, bool]:
    key = validate_idempotency_key(idempotency_key)
    key_hash = _hash(key)
    existing = PaymentAttempt.objects.filter(idempotency_key_hash=key_hash).first()
    if existing:
        if existing.order_id != order.pk:
            raise ValidationError({"idempotency_key": ["This key belongs to another order."]})
        if existing.status == PaymentAttempt.Status.OPEN:
            return existing, False
        if existing.status == PaymentAttempt.Status.CREATING:
            raise ValidationError({"payment": ["Payment checkout creation is already running."]})
        if existing.status != PaymentAttempt.Status.FAILED:
            raise ValidationError({"order": ["This order is not awaiting payment."]})
        existing.status = PaymentAttempt.Status.CREATING
        existing.last_error_code = ""
        existing.save(update_fields=("status", "last_error_code", "updated_at"))
        attempt = existing
    else:
        open_attempt = PaymentAttempt.objects.filter(
            order=order, status=PaymentAttempt.Status.OPEN
        ).first()
        if open_attempt is not None:
            return open_attempt, False
        if order.status != Order.Status.AWAITING_PAYMENT:
            raise ValidationError({"order": ["This order is not awaiting payment."]})
        try:
            attempt = PaymentAttempt.objects.create(
                order=order,
                idempotency_key_hash=key_hash,
                amount=order.total,
                currency=order.currency,
            )
        except IntegrityError as exc:
            raise ValidationError(
                {"order": ["This order already has an open payment attempt."]}
            ) from exc
    try:
        result = provider.create_checkout_session(
            order=order, attempt_id=str(attempt.public_id), idempotency_key=str(attempt.public_id)
        )
    except Exception as exc:
        attempt.status = PaymentAttempt.Status.FAILED
        attempt.last_error_code = "provider_error"
        attempt.save(update_fields=("status", "last_error_code", "updated_at"))
        raise ValidationError(
            {"payment": ["Payment checkout is temporarily unavailable."]}
        ) from exc
    attempt.provider_checkout_session_id = result.session_id
    attempt.checkout_url = result.url
    attempt.expires_at = result.expires_at
    attempt.status = PaymentAttempt.Status.OPEN
    attempt.save(
        update_fields=(
            "provider_checkout_session_id",
            "checkout_url",
            "expires_at",
            "status",
            "updated_at",
        )
    )
    return attempt, existing is None


@transaction.atomic
def process_webhook_event(event: Mapping[str, Any]) -> bool:
    event_id = str(event["id"])
    record, created = WebhookEvent.objects.get_or_create(
        provider_event_id=event_id,
        defaults={
            "event_type": str(event["type"]),
            "livemode": bool(event.get("livemode", False)),
        },
    )
    if not created:
        return False

    event_type = record.event_type
    obj = event.get("data", {}).get("object", {})
    session_id = str(obj.get("id", ""))
    attempt = (
        PaymentAttempt.objects.select_for_update()
        .filter(provider_checkout_session_id=session_id)
        .first()
    )
    if attempt is None:
        record.outcome = "ignored_unknown_session"
    elif event_type in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        if obj.get("payment_status") != "paid":
            record.outcome = "ignored_unpaid_completion"
        elif attempt.order.status == Order.Status.CANCELLED:
            record.outcome = "manual_review_paid_cancelled_order"
        else:
            attempt.provider_payment_intent_id = str(obj.get("payment_intent") or "")
            attempt.status = PaymentAttempt.Status.PAID
            attempt.save(update_fields=("provider_payment_intent_id", "status", "updated_at"))
            if attempt.order.status == Order.Status.AWAITING_PAYMENT:
                transition_order(order=attempt.order, target_status=Order.Status.CONFIRMED)
                transaction.on_commit(lambda: send_order_confirmation(attempt.order), robust=True)
            record.outcome = "paid"
    elif event_type in ("checkout.session.expired", "checkout.session.async_payment_failed"):
        if attempt.status in (PaymentAttempt.Status.PAID, PaymentAttempt.Status.REFUNDED):
            record.outcome = "ignored_failure_after_payment"
        else:
            attempt.status = (
                PaymentAttempt.Status.EXPIRED
                if event_type == "checkout.session.expired"
                else PaymentAttempt.Status.FAILED
            )
            attempt.save(update_fields=("status", "updated_at"))
            if attempt.order.status == Order.Status.AWAITING_PAYMENT:
                transition_order(order=attempt.order, target_status=Order.Status.CANCELLED)
                transaction.on_commit(lambda: send_payment_failure(attempt.order), robust=True)
            record.outcome = "unpaid_stock_released"
    else:
        record.outcome = "ignored_event_type"
    record.processed_at = timezone.now()
    record.save(update_fields=("outcome", "processed_at"))
    return True


def get_order_for_payment(
    *, public_id: str, cart_token_hash: str | None, user_id: int | None
) -> Order:
    order = (
        Order.objects.select_related("cart")
        .prefetch_related("items")
        .filter(public_id=public_id)
        .first()
    )
    if order is None:
        raise NotFound("Order not found.")
    owns_account_order = user_id is not None and order.user_id == user_id
    owns_guest_order = cart_token_hash is not None and order.cart.token_hash == cart_token_hash
    if not owns_account_order and not owns_guest_order:
        raise NotFound("Order not found.")
    return order


@transaction.atomic
def cancel_customer_order(*, order: Order, actor: object, provider: PaymentProvider) -> Order:
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    if locked_order.status == Order.Status.AWAITING_PAYMENT:
        open_attempt = (
            PaymentAttempt.objects.select_for_update()
            .filter(order=locked_order, status=PaymentAttempt.Status.OPEN)
            .first()
        )
        if open_attempt and open_attempt.provider_checkout_session_id:
            try:
                provider.expire_checkout_session(
                    session_id=open_attempt.provider_checkout_session_id
                )
            except Exception as exc:
                raise ValidationError(
                    {"payment": ["The active payment session could not be cancelled. Try again."]}
                ) from exc
            open_attempt.status = PaymentAttempt.Status.EXPIRED
            open_attempt.save(update_fields=("status", "updated_at"))
        return transition_order(
            order=locked_order, target_status=Order.Status.CANCELLED, actor=actor
        )

    if locked_order.status != Order.Status.CONFIRMED:
        raise ValidationError(
            {"order": ["Only awaiting-payment or confirmed orders can be cancelled."]}
        )
    attempt = (
        PaymentAttempt.objects.select_for_update()
        .filter(order=locked_order, status=PaymentAttempt.Status.PAID)
        .first()
    )
    if attempt is None or not attempt.provider_payment_intent_id:
        raise ValidationError({"payment": ["This order has no refundable payment."]})
    try:
        refund_id = provider.refund(
            payment_intent_id=attempt.provider_payment_intent_id,
            amount_minor=int(attempt.amount * 100),
            idempotency_key=f"refund-{attempt.public_id}",
        )
    except Exception as exc:
        raise ValidationError(
            {"payment": ["The refund could not be issued. The order was not cancelled."]}
        ) from exc
    attempt.provider_refund_id = refund_id
    attempt.refunded_at = timezone.now()
    attempt.status = PaymentAttempt.Status.REFUNDED
    attempt.save(update_fields=("provider_refund_id", "refunded_at", "status", "updated_at"))
    cancelled = transition_order(
        order=locked_order, target_status=Order.Status.CANCELLED, actor=actor
    )
    transaction.on_commit(lambda: send_refund_confirmation(cancelled), robust=True)
    return cancelled


def reconcile_payment_attempt(*, attempt: PaymentAttempt, provider: PaymentProvider) -> str:
    if not attempt.provider_checkout_session_id:
        return "skipped_missing_session"
    state = provider.retrieve_payment_state(session_id=attempt.provider_checkout_session_id)
    with transaction.atomic():
        locked = (
            PaymentAttempt.objects.select_for_update().select_related("order").get(pk=attempt.pk)
        )
        if locked.status == PaymentAttempt.Status.REFUNDED:
            return "already_refunded"
        if state.payment_status == "paid":
            if locked.order.status == Order.Status.CANCELLED:
                return "manual_review_paid_cancelled_order"
            locked.provider_payment_intent_id = state.payment_intent_id
            locked.status = PaymentAttempt.Status.PAID
            locked.save(update_fields=("provider_payment_intent_id", "status", "updated_at"))
            if locked.order.status == Order.Status.AWAITING_PAYMENT:
                transition_order(order=locked.order, target_status=Order.Status.CONFIRMED)
                transaction.on_commit(lambda: send_order_confirmation(locked.order), robust=True)
                return "confirmed_paid_order"
            return "already_paid"
        if state.status == "expired" and locked.status in (
            PaymentAttempt.Status.CREATING,
            PaymentAttempt.Status.OPEN,
        ):
            locked.status = PaymentAttempt.Status.EXPIRED
            locked.save(update_fields=("status", "updated_at"))
            if locked.order.status == Order.Status.AWAITING_PAYMENT:
                transition_order(order=locked.order, target_status=Order.Status.CANCELLED)
                transaction.on_commit(lambda: send_payment_failure(locked.order), robust=True)
                return "cancelled_expired_order"
        return "in_sync"
