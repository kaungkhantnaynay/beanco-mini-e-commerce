import hashlib
import uuid
from decimal import Decimal
from typing import Any, cast

import pytest
from django.test import Client
from django.urls import reverse
from rest_framework.throttling import ScopedRateThrottle

from apps.carts.models import Cart
from apps.catalog.factories import ProductVariantFactory
from apps.catalog.models import ProductVariant
from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord, InventoryTransaction
from apps.orders.models import Address, Order, OrderItem


def fictional_address() -> dict[str, str]:
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


def order_payload() -> dict[str, object]:
    return {
        "customer_email": "MALI.EXAMPLE@EXAMPLE.TEST",
        "shipping_address": fictional_address(),
        "shipping_method": "standard_th",
    }


def add_cart_item(
    client: Client,
    *,
    sku: str = "ORDER-VARIANT",
    price: Decimal = Decimal("125.50"),
    quantity: int = 2,
    available_quantity: int = 10,
) -> tuple[ProductVariant, InventoryRecord]:
    variant = cast(ProductVariant, ProductVariantFactory(sku=sku, price=price))
    inventory = cast(
        InventoryRecord,
        InventoryRecordFactory(variant=variant, available_quantity=available_quantity),
    )
    response = client.post(
        reverse("cart-item-create"),
        {"variant_sku": variant.sku, "quantity": quantity},
        content_type="application/json",
    )
    assert response.status_code == 201
    return variant, inventory


def post_order(client: Client, key: str, payload: dict[str, object] | None = None) -> Any:
    fictional_host = int(hashlib.sha256(key.encode()).hexdigest()[:2], 16)
    return client.post(
        reverse("order-create"),
        payload or order_payload(),
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY=key,
        REMOTE_ADDR=f"198.51.100.{fictional_host}",
    )


@pytest.mark.django_db
def test_create_order_snapshots_commercial_data_and_deducts_stock(client: Client) -> None:
    variant, inventory = add_cart_item(client)
    raw_key = "fictional-order-key-0001"

    response = post_order(client, raw_key)

    assert response.status_code == 201
    body = response.json()
    uuid.UUID(body["public_id"])
    assert "id" not in body
    assert body["status"] == "awaiting_payment"
    assert body["customer_email"] == "mali.example@example.test"
    assert body["subtotal"] == "251.00"
    assert body["shipping_total"] == "0.00"
    assert body["tax_total"] == "0.00"
    assert body["total"] == "251.00"
    assert body["shipping_address"]["phone"] == "0812345678"
    assert body["items"] == [
        {
            "product_name": variant.product.name,
            "sku": variant.sku,
            "option_name": variant.option_name,
            "weight_grams": 250,
            "grind": "whole_bean",
            "unit_price": "125.50",
            "quantity": 2,
            "line_subtotal": "251.00",
            "discount_total": "0.00",
            "tax_total": "0.00",
            "line_total": "251.00",
        }
    ]
    order = Order.objects.get(public_id=body["public_id"])
    assert order.idempotency_key_hash == hashlib.sha256(raw_key.encode()).hexdigest()
    assert raw_key not in order.idempotency_key_hash
    inventory.refresh_from_db()
    assert inventory.available_quantity == 8
    transaction = InventoryTransaction.objects.get(reason=InventoryTransaction.Reason.SALE)
    assert transaction.quantity_change == -2
    assert str(order.public_id) in transaction.reference
    assert Cart.objects.get(pk=order.cart_id).status == Cart.Status.CONVERTED


@pytest.mark.django_db
def test_repeated_idempotency_key_returns_same_order_without_second_deduction(
    client: Client,
) -> None:
    _, inventory = add_cart_item(client, quantity=1)
    key = "fictional-retry-key-0001"

    first = post_order(client, key)
    second = post_order(client, key)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["public_id"] == first.json()["public_id"]
    assert Order.objects.count() == 1
    assert InventoryTransaction.objects.filter(reason=InventoryTransaction.Reason.SALE).count() == 1
    inventory.refresh_from_db()
    assert inventory.available_quantity == 9


@pytest.mark.django_db
def test_reusing_idempotency_key_for_different_request_is_rejected(client: Client) -> None:
    add_cart_item(client, quantity=1)
    key = "fictional-conflict-key-01"
    assert post_order(client, key).status_code == 201
    changed = order_payload()
    changed["customer_email"] = "different@example.test"

    response = post_order(client, key, changed)

    assert response.status_code == 400
    assert response.json()["fields"] == {
        "idempotency_key": ["This idempotency key was used for a different request."]
    }
    assert Order.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("key", [None, "short", "invalid key with spaces"])
def test_order_requires_valid_idempotency_key(client: Client, key: str | None) -> None:
    add_cart_item(client, quantity=1)
    if key is None:
        response = client.post(
            reverse("order-create"),
            order_payload(),
            content_type="application/json",
        )
    else:
        response = client.post(
            reverse("order-create"),
            order_payload(),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
        )

    assert response.status_code == 400
    assert "idempotency_key" in response.json()["fields"]
    assert Order.objects.count() == 0
    assert InventoryTransaction.objects.count() == 0


@pytest.mark.django_db
def test_order_rejects_client_totals_without_mutation(client: Client) -> None:
    _, inventory = add_cart_item(client, quantity=1)
    payload = order_payload()
    payload["total"] = "0.01"

    response = post_order(client, "fictional-tamper-key-001", payload)

    assert response.status_code == 400
    assert response.json()["fields"] == {"total": ["This field is not allowed."]}
    assert Order.objects.count() == 0
    inventory.refresh_from_db()
    assert inventory.available_quantity == 10


@pytest.mark.django_db
def test_order_revalidates_stock_and_leaves_cart_consistent_on_failure(client: Client) -> None:
    _, inventory = add_cart_item(client, quantity=2, available_quantity=2)
    cart = Cart.objects.get()
    inventory.available_quantity = 1
    inventory.save(update_fields=("available_quantity",))

    response = post_order(client, "fictional-stock-key-0001")

    assert response.status_code == 400
    assert response.json()["fields"] == {
        "items": ["ORDER-VARIANT: Only 1 item(s) are currently available."]
    }
    assert Order.objects.count() == 0
    assert Address.objects.count() == 0
    cart.refresh_from_db()
    assert cart.status == Cart.Status.ACTIVE
    assert cart.items.get().quantity == 2
    inventory.refresh_from_db()
    assert inventory.available_quantity == 1


@pytest.mark.django_db
def test_order_uses_current_price_then_remains_historically_stable(client: Client) -> None:
    variant, _ = add_cart_item(client, price=Decimal("100.00"), quantity=2)
    original_name = variant.product.name
    variant.price = Decimal("125.00")
    variant.save(update_fields=("price",))

    response = post_order(client, "fictional-snapshot-key-01")

    assert response.status_code == 201
    assert response.json()["total"] == "250.00"
    item = OrderItem.objects.get()
    variant.price = Decimal("999.00")
    variant.save(update_fields=("price",))
    variant.product.name = "Renamed after purchase"
    variant.product.save(update_fields=("name",))
    item.refresh_from_db()
    assert item.product_name == original_name
    assert item.unit_price == Decimal("125.00")
    assert item.line_total == Decimal("250.00")


@pytest.mark.django_db
def test_unexpected_inventory_failure_rolls_back_order_address_stock_and_cart(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _, inventory = add_cart_item(client, quantity=1)
    cart = Cart.objects.get()

    def fail_transaction(**kwargs: object) -> None:
        raise RuntimeError("fictional inventory write failure")

    monkeypatch.setattr(InventoryTransaction.objects, "create", fail_transaction)

    with pytest.raises(RuntimeError, match="fictional inventory write failure"):
        post_order(client, "fictional-rollback-key-01")

    assert Order.objects.count() == 0
    assert OrderItem.objects.count() == 0
    assert Address.objects.count() == 0
    inventory.refresh_from_db()
    cart.refresh_from_db()
    assert inventory.available_quantity == 10
    assert cart.status == Cart.Status.ACTIVE


@pytest.mark.django_db
def test_public_order_status_uses_uuid_and_does_not_expose_personal_data(client: Client) -> None:
    add_cart_item(client, quantity=1)
    created = post_order(client, "fictional-status-key-001")
    public_id = created.json()["public_id"]

    response = client.get(reverse("order-status", args=[public_id]))
    missing = client.get(reverse("order-status", args=[uuid.uuid4()]))

    assert response.status_code == 200
    assert response.json()["public_id"] == public_id
    assert response.json()["status"] == "awaiting_payment"
    assert "customer_email" not in response.json()
    assert "shipping_address" not in response.json()
    assert "id" not in response.json()
    assert missing.status_code == 404
    assert missing.json()["code"] == "not_found"


@pytest.mark.django_db
def test_order_creation_is_throttled(client: Client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(ScopedRateThrottle.THROTTLE_RATES, "orders", "1/hour")
    url = reverse("order-create")

    client.post(
        url,
        order_payload(),
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="fictional-throttle-key-01",
        REMOTE_ADDR="203.0.113.20",
    )
    response = client.post(
        url,
        order_payload(),
        content_type="application/json",
        HTTP_IDEMPOTENCY_KEY="fictional-throttle-key-01",
        REMOTE_ADDR="203.0.113.20",
    )

    assert response.status_code == 429
    assert response.json()["code"] == "throttled"
