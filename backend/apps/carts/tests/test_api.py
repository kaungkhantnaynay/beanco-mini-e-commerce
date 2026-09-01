import hashlib
import uuid
from datetime import timedelta
from decimal import Decimal
from typing import cast

import pytest
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.throttling import ScopedRateThrottle

from apps.carts.models import Cart
from apps.catalog.factories import ProductVariantFactory
from apps.catalog.models import ProductVariant
from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord


def fictional_shipping_address() -> dict[str, str]:
    return {
        "full_name": "Mali Example",
        "phone": "081-234-5678",
        "address_line_1": "99 Fictional Coffee Lane",
        "address_line_2": "Unit 4B",
        "subdistrict": "Khlong Tan Nuea",
        "district": "Watthana",
        "province": "Bangkok",
        "postal_code": "10110",
        "country_code": "TH",
    }


def checkout_payload() -> dict[str, object]:
    return {
        "shipping_address": fictional_shipping_address(),
        "shipping_method": "standard_th",
    }


def add_available_variant(*, available_quantity: int = 10, **kwargs: object) -> ProductVariant:
    variant = cast(ProductVariant, ProductVariantFactory(**kwargs))
    InventoryRecordFactory(variant=variant, available_quantity=available_quantity)
    return variant


@pytest.mark.django_db
def test_get_cart_sets_secret_http_only_cookie_and_returns_public_uuid(client: Client) -> None:
    response = client.get(reverse("cart-detail"))

    assert response.status_code == 200
    body = response.json()
    uuid.UUID(body["public_id"])
    assert "id" not in body
    assert body == {
        "public_id": body["public_id"],
        "currency": "THB",
        "items": [],
        "subtotal": "0.00",
        "discount_total": "0.00",
        "shipping_total": "0.00",
        "tax_total": "0.00",
        "total": "0.00",
        "expires_at": body["expires_at"],
    }
    cookie = response.cookies["beanco_cart"]
    assert cookie["httponly"] is True
    assert cookie["secure"] is True
    assert cookie["samesite"] == "Lax"
    assert cookie["path"] == "/api/v1/"
    cart = Cart.objects.get(public_id=body["public_id"])
    assert cart.token_hash == hashlib.sha256(cookie.value.encode()).hexdigest()
    assert cart.token_hash != cookie.value


@pytest.mark.django_db
def test_cookie_retrieves_only_its_cart_and_unknown_token_creates_another(client: Client) -> None:
    first_response = client.get(reverse("cart-detail"))
    first = first_response.json()["public_id"]
    original_expiry = Cart.objects.get(public_id=first).expires_at
    retrieved = client.get(reverse("cart-detail"))
    assert retrieved.json()["public_id"] == first
    assert retrieved.cookies["beanco_cart"].value == first_response.cookies["beanco_cart"].value
    assert Cart.objects.get(public_id=first).expires_at >= original_expiry

    other = Client()
    other.cookies["beanco_cart"] = "invalid-cart-token"
    second_response = other.get(reverse("cart-detail"))

    assert second_response.status_code == 200
    assert second_response.json()["public_id"] != first
    assert Cart.objects.count() == 2


@pytest.mark.django_db
def test_expired_cart_token_is_replaced(client: Client) -> None:
    first_response = client.get(reverse("cart-detail"))
    old_id = first_response.json()["public_id"]
    Cart.objects.filter(public_id=old_id).update(expires_at=timezone.now() - timedelta(seconds=1))

    replacement = client.get(reverse("cart-detail"))

    assert replacement.json()["public_id"] != old_id
    assert replacement.cookies["beanco_cart"].value
    assert Cart.objects.get(public_id=old_id).status == Cart.Status.EXPIRED


@pytest.mark.django_db
def test_add_item_uses_server_price_and_computes_totals(client: Client) -> None:
    variant = add_available_variant(price=Decimal("125.50"), sku="SERVER-PRICE")

    response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 2},
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    item = body["items"][0]
    uuid.UUID(item["public_id"])
    assert "id" not in item
    assert item["variant_sku"] == "SERVER-PRICE"
    assert item["unit_price"] == "125.50"
    assert item["line_total"] == "251.00"
    assert body["subtotal"] == "251.00"
    assert body["discount_total"] == "0.00"
    assert body["shipping_total"] == "0.00"
    assert body["tax_total"] == "0.00"
    assert body["total"] == "251.00"


@pytest.mark.django_db
def test_add_rejects_price_tampering_and_does_not_mutate_cart(client: Client) -> None:
    variant = add_available_variant(sku="NO-TAMPERING")

    response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1, "unit_price": "0.01"},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "validation_error",
        "detail": "One or more fields are invalid.",
        "fields": {"unit_price": ["This field is not allowed."]},
    }
    assert Cart.objects.get().items.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("quantity", [0, 100])
def test_add_rejects_quantity_outside_policy(client: Client, quantity: int) -> None:
    variant = add_available_variant(sku=f"QTY-{quantity}", available_quantity=200)

    response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": quantity},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "quantity" in response.json()["fields"]


@pytest.mark.django_db
def test_add_rejects_unavailable_or_hidden_variant(client: Client) -> None:
    unavailable = ProductVariantFactory(sku="OUT-OF-STOCK")
    InventoryRecordFactory(variant=unavailable, available_quantity=1, reserved_quantity=1)
    hidden = ProductVariantFactory(sku="HIDDEN", product__is_active=False)
    InventoryRecordFactory(variant=hidden, available_quantity=10)

    unavailable_response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": unavailable.sku, "quantity": 1},
        content_type="application/json",
    )
    hidden_response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": hidden.sku, "quantity": 1},
        content_type="application/json",
    )

    assert unavailable_response.status_code == 400
    assert unavailable_response.json()["fields"] == {
        "quantity": ["The requested quantity is not available."]
    }
    assert hidden_response.status_code == 400
    assert hidden_response.json()["fields"] == {
        "variant_sku": ["Select an available product variant."]
    }


@pytest.mark.django_db
def test_adding_same_variant_increments_and_revalidates_total_quantity(client: Client) -> None:
    variant = ProductVariantFactory(sku="INCREMENT")
    InventoryRecordFactory(variant=variant, available_quantity=3)
    url = reverse("cart-item-create")

    first = client.post(
        url, {"variant_sku": variant.sku, "quantity": 2}, content_type="application/json"
    )
    second = client.post(
        url, {"variant_sku": variant.sku, "quantity": 1}, content_type="application/json"
    )
    rejected = client.post(
        url, {"variant_sku": variant.sku, "quantity": 1}, content_type="application/json"
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["items"][0]["quantity"] == 3
    assert rejected.status_code == 400
    assert client.get(reverse("cart-detail")).json()["items"][0]["quantity"] == 3


@pytest.mark.django_db
def test_patch_revalidates_visibility_stock_and_current_price(client: Client) -> None:
    variant = cast(
        ProductVariant,
        ProductVariantFactory(sku="PATCH-ME", price=Decimal("100.00")),
    )
    inventory = cast(
        InventoryRecord,
        InventoryRecordFactory(variant=variant, available_quantity=5),
    )
    created = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )
    item_id = created.json()["items"][0]["public_id"]
    variant.price = Decimal("120.00")
    variant.save(update_fields=("price",))

    updated = client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"quantity": 2},
        content_type="application/json",
    )
    inventory.available_quantity = 1
    inventory.save(update_fields=("available_quantity",))
    rejected = client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"quantity": 2},
        content_type="application/json",
    )
    variant.is_active = False
    variant.save(update_fields=("is_active",))
    hidden = client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"quantity": 1},
        content_type="application/json",
    )

    assert updated.status_code == 200
    assert updated.json()["items"][0]["unit_price"] == "120.00"
    assert updated.json()["total"] == "240.00"
    assert rejected.status_code == 400
    assert hidden.status_code == 400


@pytest.mark.django_db
def test_patch_and_delete_cannot_access_another_cart_item(client: Client) -> None:
    variant = add_available_variant(sku="ISOLATED")
    owner = Client()
    created = owner.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )
    item_id = created.json()["items"][0]["public_id"]

    patch_response = client.patch(
        reverse("cart-item-detail", args=[item_id]),
        {"quantity": 2},
        content_type="application/json",
    )
    delete_response = client.delete(reverse("cart-item-detail", args=[item_id]))

    assert patch_response.status_code == 404
    assert patch_response.json()["code"] == "not_found"
    assert delete_response.status_code == 404
    assert owner.get(reverse("cart-detail")).json()["items"][0]["quantity"] == 1


@pytest.mark.django_db
def test_delete_removes_item(client: Client) -> None:
    variant = add_available_variant(sku="REMOVE-ME")
    created = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )
    item_id = created.json()["items"][0]["public_id"]

    response = client.delete(reverse("cart-item-detail", args=[item_id]))

    assert response.status_code == 204
    assert client.get(reverse("cart-detail")).json()["items"] == []


@pytest.mark.django_db
def test_cart_requests_are_throttled_with_stable_error(
    client: Client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "carts", "1/hour")
    url = reverse("cart-detail")

    assert client.get(url, REMOTE_ADDR="203.0.113.9").status_code == 200
    response = client.get(url, REMOTE_ADDR="203.0.113.9")

    assert response.status_code == 429
    assert response.json()["code"] == "throttled"
    assert response.json()["fields"] == {}


@pytest.mark.django_db
def test_checkout_preview_validates_address_and_uses_authoritative_totals(client: Client) -> None:
    variant = add_available_variant(sku="PREVIEW", price=Decimal("275.25"))
    client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 2},
        content_type="application/json",
    )

    response = client.post(
        reverse("checkout-preview"),
        checkout_payload(),
        content_type="application/json",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["cart"]["subtotal"] == "550.50"
    assert body["cart"]["shipping_total"] == "0.00"
    assert body["cart"]["tax_total"] == "0.00"
    assert body["cart"]["total"] == "550.50"
    assert body["shipping_address"] == {
        **fictional_shipping_address(),
        "phone": "0812345678",
    }
    assert body["shipping_method"] == {
        "code": "standard_th",
        "name": "Standard delivery",
        "fee": "0.00",
        "minimum_business_days": 3,
        "maximum_business_days": 5,
    }


@pytest.mark.django_db
def test_checkout_preview_rejects_empty_cart_without_persisting_address(client: Client) -> None:
    response = client.post(
        reverse("checkout-preview"),
        checkout_payload(),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["fields"] == {"cart": ["Add at least one item before checkout."]}
    assert Cart.objects.count() == 1
    assert set(field.name for field in Cart._meta.fields).isdisjoint(
        {"full_name", "phone", "address_line_1", "postal_code"}
    )


@pytest.mark.django_db
def test_checkout_preview_rejects_invalid_thai_address_and_shipping_method(
    client: Client,
) -> None:
    variant = add_available_variant(sku="ADDRESS-VALIDATION")
    client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )
    payload = checkout_payload()
    payload["shipping_address"] = {
        **fictional_shipping_address(),
        "phone": "123",
        "postal_code": "ABCDE",
        "country_code": "US",
    }
    payload["shipping_method"] = "express_worldwide"

    response = client.post(reverse("checkout-preview"), payload, content_type="application/json")

    assert response.status_code == 400
    fields = response.json()["fields"]
    assert "phone" in fields["shipping_address"]
    assert "postal_code" in fields["shipping_address"]
    assert "country_code" in fields["shipping_address"]
    assert "shipping_method" in fields


@pytest.mark.django_db
def test_checkout_preview_rejects_client_totals(client: Client) -> None:
    variant = add_available_variant(sku="PREVIEW-TAMPER")
    client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )
    payload = checkout_payload()
    payload["total"] = "0.01"

    response = client.post(reverse("checkout-preview"), payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["fields"] == {"total": ["This field is not allowed."]}


@pytest.mark.django_db
def test_checkout_preview_revalidates_stock_visibility_and_current_price(client: Client) -> None:
    variant = add_available_variant(sku="PREVIEW-REVALIDATE", price=Decimal("100.00"))
    inventory = variant.inventory
    client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 2},
        content_type="application/json",
    )
    inventory.available_quantity = 1
    inventory.save(update_fields=("available_quantity",))

    insufficient = client.post(
        reverse("checkout-preview"), checkout_payload(), content_type="application/json"
    )

    assert insufficient.status_code == 400
    assert insufficient.json()["fields"] == {
        "items": ["PREVIEW-REVALIDATE: Only 1 item(s) are currently available."]
    }

    inventory.available_quantity = 2
    inventory.save(update_fields=("available_quantity",))
    variant.price = Decimal("125.00")
    variant.save(update_fields=("price",))
    current = client.post(
        reverse("checkout-preview"), checkout_payload(), content_type="application/json"
    )
    assert current.status_code == 200
    assert current.json()["cart"]["total"] == "250.00"

    variant.product.is_active = False
    variant.product.save(update_fields=("is_active",))
    hidden = client.post(
        reverse("checkout-preview"), checkout_payload(), content_type="application/json"
    )
    assert hidden.status_code == 400
    assert hidden.json()["fields"] == {
        "items": ["PREVIEW-REVALIDATE: This product is no longer available."]
    }


@pytest.mark.django_db
def test_checkout_preview_uses_only_cookie_owners_cart(client: Client) -> None:
    variant = add_available_variant(sku="PREVIEW-ISOLATED")
    owner = Client()
    owner.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": 1},
        content_type="application/json",
    )

    response = client.post(
        reverse("checkout-preview"), checkout_payload(), content_type="application/json"
    )

    assert response.status_code == 400
    assert response.json()["fields"] == {"cart": ["Add at least one item before checkout."]}


@pytest.mark.django_db
def test_checkout_preview_is_throttled(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "checkout", "1/hour")
    url = reverse("checkout-preview")

    client.post(
        url,
        checkout_payload(),
        content_type="application/json",
        REMOTE_ADDR="203.0.113.10",
    )
    response = client.post(
        url,
        checkout_payload(),
        content_type="application/json",
        REMOTE_ADDR="203.0.113.10",
    )

    assert response.status_code == 429
    assert response.json()["code"] == "throttled"
