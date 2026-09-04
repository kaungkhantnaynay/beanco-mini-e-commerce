from datetime import timedelta
from typing import Any, cast
from urllib.parse import parse_qs, urlparse

import pytest
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode

from apps.accounts.factories import UserFactory
from apps.accounts.models import SavedAddress, User
from apps.carts.models import Cart, CartItem
from apps.carts.services import hash_cart_token
from apps.catalog.factories import ProductVariantFactory
from apps.catalog.models import ProductVariant
from apps.inventory.factories import InventoryRecordFactory

PASSWORD = "Strong-Password-456!"


def csrf_client() -> tuple[Client, str]:
    client = Client(enforce_csrf_checks=True)
    response = client.get(reverse("auth-csrf"))
    assert response.status_code == 200
    return client, client.cookies[settings.CSRF_COOKIE_NAME].value


def post_json(client: Client, name: str, payload: dict[str, str], token: str) -> Any:
    return client.post(
        reverse(name),
        payload,
        content_type="application/json",
        HTTP_X_CSRFTOKEN=token,
    )


def token_query(message_body: str) -> dict[str, list[str]]:
    link = next(line for line in message_body.splitlines() if line.startswith("http"))
    return parse_qs(urlparse(link).query)


@pytest.mark.django_db
def test_auth_mutations_require_csrf_and_return_api_error_shape() -> None:
    client = Client(enforce_csrf_checks=True)

    response = client.post(
        reverse("auth-login"),
        {"email": "customer@example.test", "password": PASSWORD},
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.json() == {
        "code": "permission_denied",
        "detail": "CSRF Failed: CSRF cookie not set.",
        "fields": {},
    }


@pytest.mark.django_db(transaction=True)
def test_registration_verification_login_account_and_logout_session_flow() -> None:
    client, csrf = csrf_client()

    registration = post_json(
        client,
        "auth-register",
        {
            "email": " Customer@Example.TEST ",
            "password": PASSWORD,
            "first_name": "Mali",
            "last_name": "Example",
        },
        csrf,
    )

    assert registration.status_code == 202
    user = User.objects.get(email="customer@example.test")
    assert user.is_active is False
    assert user.email_verified_at is None
    assert len(mail.outbox) == 1
    query = token_query(force_str(mail.outbox[0].body))

    verification = post_json(
        client,
        "auth-verify-email",
        {"uid": query["uid"][0], "token": query["token"][0]},
        csrf,
    )
    assert verification.status_code == 200
    user.refresh_from_db()
    assert user.is_active is True
    assert user.email_verified_at is not None

    signed_in = post_json(
        client,
        "auth-login",
        {"email": "CUSTOMER@example.test", "password": PASSWORD},
        csrf,
    )
    assert signed_in.status_code == 200
    assert signed_in.json() == {
        "email": "customer@example.test",
        "first_name": "Mali",
        "last_name": "Example",
        "email_verified": True,
    }
    session_cookie = client.cookies[settings.SESSION_COOKIE_NAME]
    assert session_cookie["httponly"] is True
    assert session_cookie["secure"] is True
    assert session_cookie["samesite"] == "Lax"

    account = client.get(reverse("account-current"))
    assert account.status_code == 200
    assert account.json()["email"] == "customer@example.test"

    rotated_csrf = client.cookies[settings.CSRF_COOKIE_NAME].value
    signed_out = post_json(client, "auth-logout", {}, rotated_csrf)
    assert signed_out.status_code == 200
    assert client.get(reverse("account-current")).status_code == 403


@pytest.mark.django_db(transaction=True)
def test_registration_does_not_disclose_existing_account() -> None:
    UserFactory(
        email="existing@example.test",
        email_verified_at=timezone.now(),
        is_active=True,
    )
    client, csrf = csrf_client()
    payload = {"password": PASSWORD, "first_name": "Mali", "last_name": "Example"}

    existing = post_json(
        client, "auth-register", {**payload, "email": "existing@example.test"}, csrf
    )
    missing = post_json(client, "auth-register", {**payload, "email": "new@example.test"}, csrf)

    assert existing.status_code == missing.status_code == 202
    assert existing.json() == missing.json()


@pytest.mark.django_db
def test_login_does_not_disclose_account_or_verification_state() -> None:
    UserFactory(
        email="verified@example.test",
        password=PASSWORD,
        email_verified_at=timezone.now(),
        is_active=True,
    )
    UserFactory(email="unverified@example.test", password=PASSWORD, is_active=False)
    client, csrf = csrf_client()

    unknown = post_json(
        client,
        "auth-login",
        {"email": "unknown@example.test", "password": PASSWORD},
        csrf,
    )
    unverified = post_json(
        client,
        "auth-login",
        {"email": "unverified@example.test", "password": PASSWORD},
        csrf,
    )
    incorrect = post_json(
        client,
        "auth-login",
        {"email": "verified@example.test", "password": "Incorrect-Password-789!"},
        csrf,
    )

    assert unknown.status_code == unverified.status_code == incorrect.status_code == 403
    assert unknown.json() == unverified.json() == incorrect.json()


@pytest.mark.django_db(transaction=True)
def test_password_reset_is_neutral_and_confirmation_invalidates_old_password() -> None:
    user = User.objects.create_user("verified@example.test", PASSWORD)
    user.email_verified_at = timezone.now()
    user.save(update_fields=("email_verified_at",))
    client, csrf = csrf_client()

    existing = post_json(client, "auth-password-reset", {"email": user.email}, csrf)
    missing = post_json(client, "auth-password-reset", {"email": "missing@example.test"}, csrf)

    assert existing.status_code == missing.status_code == 202
    assert existing.json() == missing.json()
    assert len(mail.outbox) == 1

    reset = post_json(
        client,
        "auth-password-reset-confirm",
        {
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
            "new_password": "Replacement-Password-789!",
        },
        csrf,
    )
    assert reset.status_code == 200, reset.json()
    user.refresh_from_db()
    assert user.check_password(PASSWORD) is False
    assert user.check_password("Replacement-Password-789!") is True


def saved_address_payload(**overrides: object) -> dict[str, object]:
    return {
        "label": "Home",
        "is_default": False,
        "full_name": "Mali Example",
        "phone": "081-234-5678",
        "address_line_1": "99 Fictional Coffee Lane",
        "address_line_2": "",
        "subdistrict": "Khlong Tan Nuea",
        "district": "Watthana",
        "province": "Bangkok",
        "postal_code": "10110",
        "country_code": "TH",
        **overrides,
    }


@pytest.mark.django_db
def test_customer_can_update_profile_and_manage_only_their_addresses(client: Client) -> None:
    user = User.objects.create_user("profile@example.test", PASSWORD)
    other = User.objects.create_user("other@example.test", PASSWORD)
    other_address = SavedAddress.objects.create(user=other, **saved_address_payload(label="Other"))
    client.force_login(user)

    profile = client.patch(
        reverse("account-current"),
        {"first_name": " Mali ", "last_name": "Customer"},
        content_type="application/json",
    )
    created = client.post(
        reverse("account-address-list"),
        saved_address_payload(),
        content_type="application/json",
    )

    assert profile.status_code == 200
    assert profile.json()["first_name"] == "Mali"
    assert created.status_code == 201
    assert created.json()["is_default"] is True
    address_id = created.json()["public_id"]

    updated = client.patch(
        reverse("account-address-detail", args=[address_id]),
        {"label": "Office", "phone": "+66 812345678"},
        content_type="application/json",
    )
    forbidden = client.patch(
        reverse("account-address-detail", args=[other_address.public_id]),
        {"label": "Stolen"},
        content_type="application/json",
    )
    listed = client.get(reverse("account-address-list"))

    assert updated.status_code == 200
    assert updated.json()["label"] == "Office"
    assert updated.json()["phone"] == "+66812345678"
    assert forbidden.status_code == 404
    assert [item["public_id"] for item in listed.json()] == [address_id]
    assert client.delete(reverse("account-address-detail", args=[address_id])).status_code == 204


@pytest.mark.django_db
def test_login_merges_guest_and_account_carts_without_exceeding_stock() -> None:
    user = User.objects.create_user("cart@example.test", PASSWORD)
    user.email_verified_at = timezone.now()
    user.save(update_fields=("email_verified_at",))
    variant = cast(ProductVariant, ProductVariantFactory(sku="MERGE-CART"))
    InventoryRecordFactory(variant=variant, available_quantity=3)
    previous = Cart.objects.create(
        user=user,
        token_hash=hash_cart_token("previous-secret"),
        expires_at=timezone.now() + timedelta(days=1),
    )
    CartItem.objects.create(cart=previous, variant=variant, quantity=2)
    client, csrf = csrf_client()
    assert (
        client.post(
            reverse("cart-item-create"),
            {"variant_sku": variant.sku, "quantity": 2},
            content_type="application/json",
        ).status_code
        == 201
    )

    signed_in = post_json(
        client,
        "auth-login",
        {"email": user.email, "password": PASSWORD},
        csrf,
    )

    assert signed_in.status_code == 200
    merged = client.get(reverse("cart-detail")).json()
    assert merged["items"][0]["quantity"] == 3
    assert Cart.objects.get(pk=previous.pk).status == Cart.Status.CONVERTED
    assert Cart.objects.get(public_id=merged["public_id"]).user == user
