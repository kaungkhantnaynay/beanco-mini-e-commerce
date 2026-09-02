import hashlib
from collections.abc import Mapping
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.orders.models import Order
from apps.orders.services import transition_order, validate_idempotency_key

from .models import PaymentAttempt, WebhookEvent
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
            record.outcome = "paid"
    elif event_type in ("checkout.session.expired", "checkout.session.async_payment_failed"):
        attempt.status = (
            PaymentAttempt.Status.EXPIRED
            if event_type == "checkout.session.expired"
            else PaymentAttempt.Status.FAILED
        )
        attempt.save(update_fields=("status", "updated_at"))
        if attempt.order.status == Order.Status.AWAITING_PAYMENT:
            transition_order(order=attempt.order, target_status=Order.Status.CANCELLED)
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
