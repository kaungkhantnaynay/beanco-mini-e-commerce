from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol, cast

import stripe
from django.conf import settings
from django.utils import timezone

from apps.orders.models import Order


@dataclass(frozen=True)
class CheckoutSessionResult:
    session_id: str
    url: str
    expires_at: datetime


@dataclass(frozen=True)
class ProviderPaymentState:
    session_id: str
    status: str
    payment_status: str
    payment_intent_id: str


class WebhookVerificationError(Exception):
    pass


class PaymentProvider(Protocol):
    def create_checkout_session(
        self, *, order: Order, attempt_id: str, idempotency_key: str
    ) -> CheckoutSessionResult: ...

    def construct_event(self, *, payload: bytes, signature: str) -> Mapping[str, Any]: ...

    def refund(self, *, payment_intent_id: str, amount_minor: int, idempotency_key: str) -> str: ...

    def expire_checkout_session(self, *, session_id: str) -> None: ...

    def retrieve_payment_state(self, *, session_id: str) -> ProviderPaymentState: ...


class StripePaymentProvider:
    def __init__(self) -> None:
        self.client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)

    def create_checkout_session(
        self, *, order: Order, attempt_id: str, idempotency_key: str
    ) -> CheckoutSessionResult:
        expires_at = int((timezone.now() + settings.STRIPE_CHECKOUT_TTL).timestamp())
        line_items = [
            {
                "price_data": {
                    "currency": "thb",
                    "product_data": {"name": item.product_name},
                    "unit_amount": int(item.unit_price * 100),
                },
                "quantity": item.quantity,
            }
            for item in order.items.all()
        ]
        session = self.client.v1.checkout.sessions.create(
            {  # type: ignore[arg-type]
                "mode": "payment",
                "payment_method_types": ["card", "promptpay"],
                "line_items": line_items,
                "customer_email": order.customer_email,
                "client_reference_id": str(order.public_id),
                "metadata": {"order_public_id": str(order.public_id), "attempt_id": attempt_id},
                "success_url": settings.STRIPE_SUCCESS_URL.replace(
                    "{order_id}", str(order.public_id)
                ),
                "cancel_url": settings.STRIPE_CANCEL_URL.replace(
                    "{order_id}", str(order.public_id)
                ),
                "expires_at": expires_at,
            },
            {"idempotency_key": idempotency_key},
        )
        if not session.url:
            raise RuntimeError("Stripe did not return a Checkout URL.")
        return CheckoutSessionResult(
            session_id=session.id,
            url=session.url,
            expires_at=datetime.fromtimestamp(session.expires_at, tz=UTC),
        )

    def construct_event(self, *, payload: bytes, signature: str) -> Mapping[str, Any]:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.SignatureVerificationError) as exc:
            raise WebhookVerificationError from exc
        return cast(Mapping[str, Any], event)

    def refund(self, *, payment_intent_id: str, amount_minor: int, idempotency_key: str) -> str:
        refund = self.client.v1.refunds.create(
            {"payment_intent": payment_intent_id, "amount": amount_minor},
            {"idempotency_key": idempotency_key},
        )
        return refund.id

    def expire_checkout_session(self, *, session_id: str) -> None:
        self.client.v1.checkout.sessions.expire(session_id)

    def retrieve_payment_state(self, *, session_id: str) -> ProviderPaymentState:
        session = self.client.v1.checkout.sessions.retrieve(session_id)
        payment_intent = session.payment_intent
        return ProviderPaymentState(
            session_id=session.id,
            status=session.status or "unknown",
            payment_status=session.payment_status or "unknown",
            payment_intent_id=(
                payment_intent
                if isinstance(payment_intent, str)
                else payment_intent.id
                if payment_intent is not None
                else ""
            ),
        )


def get_payment_provider() -> PaymentProvider:
    return StripePaymentProvider()
