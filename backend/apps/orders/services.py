import hashlib
import json
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from apps.carts.models import Cart
from apps.carts.services import STANDARD_SHIPPING_METHOD, ZERO_MONEY, money
from apps.inventory.models import InventoryRecord, InventoryTransaction

from .models import Address, Order, OrderItem


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_email(value: str) -> str:
    return value.strip().casefold()


def request_fingerprint(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hash_value(serialized)


def validate_idempotency_key(value: str | None) -> str:
    if value is None or len(value) < 16 or len(value) > 128:
        raise ValidationError(
            {"idempotency_key": ["Provide an Idempotency-Key header of 16 to 128 characters."]}
        )
    if not all(character.isalnum() or character in "._:-" for character in value):
        raise ValidationError(
            {
                "idempotency_key": [
                    "Use only letters, numbers, dots, underscores, colons, or hyphens."
                ]
            }
        )
    return value


def _existing_order(key_hash: str, fingerprint: str) -> Order | None:
    order = Order.objects.filter(idempotency_key_hash=key_hash).first()
    if order is not None and order.request_fingerprint != fingerprint:
        raise ValidationError(
            {"idempotency_key": ["This idempotency key was used for a different request."]}
        )
    return order


def _lock_inventory(variant_ids: list[int]) -> dict[int, InventoryRecord]:
    records = (
        InventoryRecord.objects.select_for_update()
        .filter(variant_id__in=sorted(variant_ids))
        .order_by("variant_id")
    )
    return {record.variant_id: record for record in records}


def create_order(
    *,
    cart: Cart,
    idempotency_key: str,
    customer_email: str,
    shipping_address: dict[str, Any],
    shipping_method: str,
) -> tuple[Order, bool]:
    normalized_payload = {
        "customer_email": normalize_email(customer_email),
        "shipping_address": dict(shipping_address),
        "shipping_method": shipping_method,
    }
    key_hash = hash_value(idempotency_key)
    fingerprint = request_fingerprint(normalized_payload)
    existing = _existing_order(key_hash, fingerprint)
    if existing is not None:
        return existing, False

    try:
        return _create_order_atomic(
            cart=cart,
            key_hash=key_hash,
            fingerprint=fingerprint,
            payload=normalized_payload,
        )
    except IntegrityError:
        existing = _existing_order(key_hash, fingerprint)
        if existing is None:
            raise
        return existing, False


@transaction.atomic
def _create_order_atomic(
    *,
    cart: Cart,
    key_hash: str,
    fingerprint: str,
    payload: dict[str, Any],
) -> tuple[Order, bool]:
    existing = Order.objects.select_for_update().filter(idempotency_key_hash=key_hash).first()
    if existing is not None:
        if existing.request_fingerprint != fingerprint:
            raise ValidationError(
                {"idempotency_key": ["This idempotency key was used for a different request."]}
            )
        return existing, False

    try:
        locked_cart = Cart.objects.select_for_update().get(pk=cart.pk, status=Cart.Status.ACTIVE)
    except Cart.DoesNotExist as exc:
        raise ValidationError({"cart": ["This cart is no longer available."]}) from exc

    cart_items = list(
        locked_cart.items.select_related("variant__product__category").order_by("variant_id")
    )
    if not cart_items:
        raise ValidationError({"cart": ["Add at least one item before creating an order."]})

    variant_ids = [item.variant_id for item in cart_items]
    inventory_by_variant = _lock_inventory(variant_ids)
    errors: list[str] = []
    for item in cart_items:
        variant = item.variant
        product = variant.product
        inventory = inventory_by_variant.get(variant.pk)
        if (
            not variant.is_active
            or not product.is_active
            or not product.category.is_active
            or inventory is None
        ):
            errors.append(f"{variant.sku}: This product is no longer available.")
        elif inventory.stock_policy != InventoryRecord.StockPolicy.TRACKED:
            errors.append(f"{variant.sku}: This product is not available for retail checkout.")
        elif item.quantity > inventory.available_to_sell:
            available = inventory.available_to_sell
            errors.append(f"{variant.sku}: Only {available} item(s) are currently available.")
    if errors:
        raise ValidationError({"items": errors})

    line_snapshots: list[dict[str, Any]] = []
    subtotal = ZERO_MONEY
    for item in cart_items:
        variant = item.variant
        line_total = money(variant.price * item.quantity)
        subtotal += line_total
        line_snapshots.append(
            {
                "variant": variant,
                "product_name": variant.product.name,
                "sku": variant.sku,
                "option_name": variant.option_name,
                "weight_grams": variant.weight_grams,
                "grind": variant.grind,
                "unit_price": variant.price,
                "quantity": item.quantity,
                "line_subtotal": line_total,
                "discount_total": ZERO_MONEY,
                "tax_total": ZERO_MONEY,
                "line_total": line_total,
            }
        )
    subtotal = money(subtotal)

    address = Address.objects.create(**payload["shipping_address"])
    order = Order.objects.create(
        cart=locked_cart,
        user=locked_cart.user,
        shipping_address=address,
        idempotency_key_hash=key_hash,
        request_fingerprint=fingerprint,
        customer_email=payload["customer_email"],
        shipping_method=STANDARD_SHIPPING_METHOD["code"],
        shipping_method_name=STANDARD_SHIPPING_METHOD["name"],
        subtotal=subtotal,
        discount_total=ZERO_MONEY,
        shipping_total=STANDARD_SHIPPING_METHOD["fee"],
        tax_total=ZERO_MONEY,
        total=subtotal,
    )
    OrderItem.objects.bulk_create(
        [OrderItem(order=order, **snapshot) for snapshot in line_snapshots]
    )

    for item in cart_items:
        inventory = inventory_by_variant[item.variant_id]
        inventory.available_quantity -= item.quantity
        inventory.save(update_fields=("available_quantity", "updated_at"))
        InventoryTransaction.objects.create(
            variant=item.variant,
            quantity_change=-item.quantity,
            reason=InventoryTransaction.Reason.SALE,
            reference=f"Order {order.public_id}",
        )

    locked_cart.status = Cart.Status.CONVERTED
    locked_cart.save(update_fields=("status", "updated_at"))
    return order, True


@transaction.atomic
def transition_order(*, order: Order, target_status: str, actor: object | None = None) -> Order:
    locked_order = (
        Order.objects.select_for_update().prefetch_related("items__variant").get(pk=order.pk)
    )
    allowed = Order.allowed_status_transitions()[locked_order.status]
    if target_status not in allowed:
        raise DjangoValidationError(
            f"Order cannot transition from {locked_order.status} to {target_status}."
        )

    if target_status == Order.Status.CANCELLED and not locked_order.stock_restored:
        items = [item for item in locked_order.items.all() if item.variant_id is not None]
        variant_ids = sorted(item.variant_id for item in items if item.variant_id is not None)
        inventories = _lock_inventory(variant_ids)
        user_model = get_user_model()
        valid_actor = actor if isinstance(actor, user_model) else None
        for item in items:
            if item.variant_id is None or item.variant is None:
                continue
            inventory = inventories[item.variant_id]
            inventory.available_quantity += item.quantity
            inventory.save(update_fields=("available_quantity", "updated_at"))
            InventoryTransaction.objects.create(
                variant=item.variant,
                quantity_change=item.quantity,
                reason=InventoryTransaction.Reason.CANCELLATION,
                reference=f"Order {locked_order.public_id}",
                actor=valid_actor,
            )
        locked_order.stock_restored = True

    locked_order.status = target_status
    locked_order.save(update_fields=("status", "stock_restored", "updated_at"))
    return locked_order
