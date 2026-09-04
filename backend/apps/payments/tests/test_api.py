import hashlib
import hmac
import json
import time
from typing import cast

import pytest
from django.test import Client, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.orders.factories import OrderFactory
from apps.orders.models import Order
from apps.payments.models import PaymentAttempt, WebhookEvent


def stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed = f"{timestamp}.{payload.decode()}".encode()
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


@pytest.mark.django_db
@override_settings(STRIPE_SECRET_KEY="sk_test_fictional", STRIPE_WEBHOOK_SECRET="whsec_test")
def test_webhook_rejects_forgery_and_accepts_signed_raw_body(client: Client) -> None:
    event = {
        "id": "evt_signed_fictional",
        "object": "event",
        "type": "checkout.session.completed",
        "livemode": False,
        "data": {"object": {"id": "cs_unknown", "payment_status": "paid"}},
    }
    payload = json.dumps(event, separators=(",", ":")).encode()
    url = reverse("stripe-webhook")

    forged = client.post(
        url,
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="t=1,v1=forged",
    )
    assert forged.status_code == 400
    assert WebhookEvent.objects.count() == 0

    accepted = client.post(
        url,
        data=payload,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=stripe_signature(payload, "whsec_test"),
    )
    assert accepted.status_code == 200
    assert accepted.json() == {"received": True, "duplicate": False}
    assert WebhookEvent.objects.get().outcome == "ignored_unknown_session"


@pytest.mark.django_db
def test_payment_session_hides_orders_without_guest_or_account_ownership(client: Client) -> None:
    order = cast(Order, OrderFactory())
    client.cookies["beanco_cart"] = "not-the-order-cart-token"

    response = client.post(
        reverse("payment-session-create", args=[order.public_id]),
        HTTP_IDEMPOTENCY_KEY="payment-session-key-0001",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found."
    assert PaymentAttempt.objects.count() == 0


@pytest.mark.django_db
def test_customer_can_cancel_only_their_awaiting_payment_order(client: Client) -> None:
    owner = User.objects.create_user("owner@example.test", "Strong-Password-456!")
    other = User.objects.create_user("other@example.test", "Strong-Password-456!")
    order = cast(Order, OrderFactory(user=owner))
    url = reverse("account-order-cancel", args=[order.public_id])

    client.force_login(other)
    assert client.post(url).status_code == 404

    client.force_login(owner)
    response = client.post(url)

    assert response.status_code == 200
    assert response.json()["status"] == Order.Status.CANCELLED
