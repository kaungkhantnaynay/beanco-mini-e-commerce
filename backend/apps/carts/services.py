import hashlib
import secrets
from dataclasses import dataclass
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, TypedDict

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.catalog.models import ProductVariant
from apps.inventory.models import InventoryRecord

from .models import Cart, CartItem

CART_LIFETIME = timedelta(days=30)
MONEY_QUANTUM = Decimal("0.01")
ZERO_MONEY = Decimal("0.00")


class ShippingMethod(TypedDict):
    code: str
    name: str
    fee: Decimal
    minimum_business_days: int
    maximum_business_days: int


STANDARD_SHIPPING_METHOD: ShippingMethod = {
    "code": "standard_th",
    "name": "Standard delivery",
    "fee": ZERO_MONEY,
    "minimum_business_days": 3,
    "maximum_business_days": 5,
}


@dataclass(frozen=True)
class CartAccess:
    cart: Cart
    token: str
    set_cookie: bool


def hash_cart_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_or_create_cart(token: str | None, user: object | None = None) -> CartAccess:
    now = timezone.now()
    user_model = get_user_model()
    authenticated_user = user if isinstance(user, user_model) else None
    if token:
        cart = (
            Cart.objects.filter(
                token_hash=hash_cart_token(token),
                status=Cart.Status.ACTIVE,
            )
            .prefetch_related("items__variant__product", "items__variant__inventory")
            .first()
        )
        if cart is not None:
            if cart.expires_at > now and (
                cart.user_id is None
                or authenticated_user is None
                or cart.user_id == authenticated_user.pk
            ):
                if authenticated_user is not None and cart.user_id is None:
                    cart.user = authenticated_user
                    cart.save(update_fields=("user", "updated_at"))
                touch_cart(cart)
                return CartAccess(cart=cart, token=token, set_cookie=True)
            if cart.expires_at <= now:
                cart.status = Cart.Status.EXPIRED
                cart.save(update_fields=("status", "updated_at"))

    if authenticated_user is not None:
        existing = (
            Cart.objects.filter(
                user=authenticated_user,
                status=Cart.Status.ACTIVE,
                expires_at__gt=now,
            )
            .prefetch_related("items__variant__product", "items__variant__inventory")
            .first()
        )
        if existing is not None:
            new_token = secrets.token_urlsafe(32)
            existing.token_hash = hash_cart_token(new_token)
            existing.expires_at = now + CART_LIFETIME
            existing.save(update_fields=("token_hash", "expires_at", "updated_at"))
            return CartAccess(cart=existing, token=new_token, set_cookie=True)

    new_token = secrets.token_urlsafe(32)
    cart = Cart.objects.create(
        token_hash=hash_cart_token(new_token),
        user=authenticated_user,
        expires_at=now + CART_LIFETIME,
    )
    return CartAccess(cart=cart, token=new_token, set_cookie=True)


@transaction.atomic
def merge_guest_cart(*, user: object, token: str | None) -> Cart | None:
    """Attach the browser cart and merge older account carts without exceeding stock."""

    user_model = get_user_model()
    if not isinstance(user, user_model) or not token:
        return None
    guest = (
        Cart.objects.select_for_update()
        .filter(
            token_hash=hash_cart_token(token),
            status=Cart.Status.ACTIVE,
            expires_at__gt=timezone.now(),
        )
        .first()
    )
    if guest is None or (guest.user_id is not None and guest.user_id != user.pk):
        return None

    guest.user = user
    guest.save(update_fields=("user", "updated_at"))
    previous_carts = list(
        Cart.objects.select_for_update()
        .filter(user=user, status=Cart.Status.ACTIVE)
        .exclude(pk=guest.pk)
        .order_by("pk")
    )
    for previous in previous_carts:
        for source in previous.items.select_related("variant__inventory").all():
            destination = CartItem.objects.filter(cart=guest, variant=source.variant).first()
            current = destination.quantity if destination else 0
            available = source.variant.inventory.available_to_sell
            merged_quantity = min(current + source.quantity, available, 99)
            if merged_quantity < 1:
                continue
            if destination:
                destination.quantity = merged_quantity
                destination.save(update_fields=("quantity", "updated_at"))
            else:
                source.cart = guest
                source.quantity = merged_quantity
                source.save(update_fields=("cart", "quantity", "updated_at"))
        previous.status = Cart.Status.CONVERTED
        previous.save(update_fields=("status", "updated_at"))
    touch_cart(guest)
    return guest


def touch_cart(cart: Cart) -> None:
    cart.expires_at = timezone.now() + CART_LIFETIME
    cart.save(update_fields=("expires_at", "updated_at"))


def _locked_available_variant(sku: str) -> tuple[ProductVariant, InventoryRecord]:
    try:
        variant = ProductVariant.objects.select_related("product__category").get(
            sku=sku,
            is_active=True,
            product__is_active=True,
            product__category__is_active=True,
        )
        inventory = InventoryRecord.objects.select_for_update().get(variant=variant)
    except (ProductVariant.DoesNotExist, InventoryRecord.DoesNotExist) as exc:
        raise ValidationError({"variant_sku": ["Select an available product variant."]}) from exc
    if inventory.stock_policy != InventoryRecord.StockPolicy.TRACKED:
        raise ValidationError({"variant_sku": ["Select an available product variant."]})
    return variant, inventory


def _validate_quantity(quantity: int, inventory: InventoryRecord) -> None:
    if quantity < 1 or quantity > 99:
        raise ValidationError({"quantity": ["Enter a whole number from 1 through 99."]})
    if quantity > inventory.available_to_sell:
        raise ValidationError({"quantity": ["The requested quantity is not available."]})


@transaction.atomic
def add_cart_item(*, cart: Cart, variant_sku: str, quantity: int) -> tuple[CartItem, bool]:
    locked_cart = Cart.objects.select_for_update().get(pk=cart.pk, status=Cart.Status.ACTIVE)
    variant, inventory = _locked_available_variant(variant_sku)
    item = CartItem.objects.filter(cart=locked_cart, variant=variant).first()
    requested_quantity = quantity + item.quantity if item else quantity
    _validate_quantity(requested_quantity, inventory)
    if item:
        item.quantity = requested_quantity
        item.save(update_fields=("quantity", "updated_at"))
        created = False
    else:
        item = CartItem.objects.create(cart=locked_cart, variant=variant, quantity=quantity)
        created = True
    touch_cart(locked_cart)
    return item, created


@transaction.atomic
def update_cart_item(*, cart: Cart, public_id: str, quantity: int) -> CartItem:
    locked_cart = Cart.objects.select_for_update().get(pk=cart.pk, status=Cart.Status.ACTIVE)
    try:
        item = CartItem.objects.select_related("variant").get(
            cart=locked_cart,
            public_id=public_id,
        )
    except (CartItem.DoesNotExist, ValueError) as exc:
        raise NotFound("Cart item not found.") from exc
    variant, inventory = _locked_available_variant(item.variant.sku)
    _validate_quantity(quantity, inventory)
    item.variant = variant
    item.quantity = quantity
    item.save(update_fields=("quantity", "updated_at"))
    touch_cart(locked_cart)
    return item


@transaction.atomic
def remove_cart_item(*, cart: Cart, public_id: str) -> None:
    locked_cart = Cart.objects.select_for_update().get(pk=cart.pk, status=Cart.Status.ACTIVE)
    try:
        item = CartItem.objects.get(cart=locked_cart, public_id=public_id)
    except (CartItem.DoesNotExist, ValueError) as exc:
        raise NotFound("Cart item not found.") from exc
    item.delete()
    touch_cart(locked_cart)


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def validate_cart_for_checkout(cart: Cart) -> Cart:
    current_cart = (
        Cart.objects.filter(pk=cart.pk, status=Cart.Status.ACTIVE)
        .prefetch_related(
            "items__variant__product__category",
            "items__variant__inventory",
        )
        .first()
    )
    if current_cart is None:
        raise ValidationError({"cart": ["This cart is no longer available."]})

    items = list(current_cart.items.all())
    if not items:
        raise ValidationError({"cart": ["Add at least one item before checkout."]})

    errors: list[str] = []
    for item in items:
        variant = item.variant
        product = variant.product
        if not variant.is_active or not product.is_active or not product.category.is_active:
            errors.append(f"{variant.sku}: This product is no longer available.")
            continue
        try:
            inventory = variant.inventory
        except ProductVariant.inventory.RelatedObjectDoesNotExist:
            errors.append(f"{variant.sku}: This product is no longer available.")
            continue
        if inventory.stock_policy != InventoryRecord.StockPolicy.TRACKED:
            errors.append(f"{variant.sku}: This product is not available for retail checkout.")
        elif item.quantity > inventory.available_to_sell:
            available = inventory.available_to_sell
            errors.append(f"{variant.sku}: Only {available} item(s) are currently available.")

    if errors:
        raise ValidationError({"items": errors})
    return current_cart


def build_checkout_preview(*, cart: Cart, shipping_address: dict[str, Any]) -> dict[str, Any]:
    current_cart = validate_cart_for_checkout(cart)
    return {
        "cart": current_cart,
        "shipping_address": shipping_address,
        "shipping_method": STANDARD_SHIPPING_METHOD,
    }
