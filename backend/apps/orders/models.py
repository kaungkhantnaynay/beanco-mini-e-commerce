import uuid
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Q

from apps.carts.models import Cart
from apps.catalog.models import ProductVariant


class ImmutableSnapshotQuerySet(models.QuerySet[Any]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("Order snapshots are immutable.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Order snapshots are immutable.")


class Address(models.Model):
    objects = ImmutableSnapshotQuerySet.as_manager()

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=120)
    phone = models.CharField(
        max_length=24,
        validators=[RegexValidator(r"^(?:\+66|0)\d{8,9}$", "Enter a valid Thai phone number.")],
    )
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    subdistrict = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(
        max_length=5,
        validators=[RegexValidator(r"^\d{5}$", "Enter a five-digit postal code.")],
    )
    country_code = models.CharField(max_length=2, default="TH")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk:
            raise ValidationError("Order addresses are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Order addresses are immutable.")

    def __str__(self) -> str:
        return f"{self.full_name}, {self.province} {self.postal_code}"


class OrderQuerySet(models.QuerySet["Order"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("Orders must be changed through the status transition service.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Orders cannot be deleted.")


class Order(models.Model):
    objects = OrderQuerySet.as_manager()

    class Status(models.TextChoices):
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting payment"
        CONFIRMED = "confirmed", "Confirmed"
        FULFILLING = "fulfilling", "Fulfilling"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    immutable_fields = (
        "public_id",
        "cart_id",
        "user_id",
        "shipping_address_id",
        "idempotency_key_hash",
        "request_fingerprint",
        "customer_email",
        "currency",
        "shipping_method",
        "shipping_method_name",
        "subtotal",
        "discount_total",
        "shipping_total",
        "tax_total",
        "total",
    )

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT, related_name="order")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    shipping_address = models.OneToOneField(
        Address,
        on_delete=models.PROTECT,
        related_name="order",
    )
    idempotency_key_hash = models.CharField(max_length=64, unique=True, editable=False)
    request_fingerprint = models.CharField(max_length=64, editable=False)
    customer_email = models.EmailField(max_length=254)
    currency = models.CharField(max_length=3, default="THB", editable=False)
    shipping_method = models.CharField(max_length=40)
    shipping_method_name = models.CharField(max_length=100)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.AWAITING_PAYMENT,
        db_index=True,
    )
    stock_restored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(subtotal__gte=0)
                    & Q(discount_total__gte=0)
                    & Q(shipping_total__gte=0)
                    & Q(tax_total__gte=0)
                    & Q(total__gte=0)
                ),
                name="orders_totals_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(
                    total=F("subtotal") - F("discount_total") + F("shipping_total") + F("tax_total")
                ),
                name="orders_total_matches_components",
            ),
            models.CheckConstraint(
                condition=Q(stock_restored=False) | Q(status="cancelled"),
                name="orders_restored_only_when_cancelled",
            ),
        ]

    @classmethod
    def allowed_status_transitions(cls) -> dict[str, set[str]]:
        return {
            cls.Status.AWAITING_PAYMENT: {cls.Status.CONFIRMED, cls.Status.CANCELLED},
            cls.Status.CONFIRMED: {cls.Status.FULFILLING, cls.Status.CANCELLED},
            cls.Status.FULFILLING: {cls.Status.SHIPPED, cls.Status.CANCELLED},
            cls.Status.SHIPPED: {cls.Status.DELIVERED},
            cls.Status.DELIVERED: set(),
            cls.Status.CANCELLED: set(),
        }

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk:
            previous = type(self).objects.only(*self.immutable_fields).get(pk=self.pk)
            if any(
                getattr(previous, field) != getattr(self, field) for field in self.immutable_fields
            ):
                raise ValidationError("Commercial order fields are immutable.")
            if (
                self.status != previous.status
                and self.status not in self.allowed_status_transitions()[previous.status]
            ):
                raise ValidationError(
                    f"Order cannot transition from {previous.status} to {self.status}."
                )
            if self.stock_restored != previous.stock_restored and not (
                self.stock_restored and self.status == self.Status.CANCELLED
            ):
                raise ValidationError("Stock restoration is valid only during cancellation.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Orders cannot be deleted.")

    def __str__(self) -> str:
        return f"Order {self.public_id}"


class OrderItem(models.Model):
    objects = ImmutableSnapshotQuerySet.as_manager()

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        related_name="order_items",
        null=True,
        blank=True,
    )
    product_name = models.CharField(max_length=180)
    sku = models.CharField(max_length=64)
    option_name = models.CharField(max_length=100, blank=True)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    grind = models.CharField(max_length=20, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=1), name="orders_item_quantity_gte_1"),
            models.CheckConstraint(
                condition=(
                    Q(unit_price__gte=0)
                    & Q(line_subtotal__gte=0)
                    & Q(discount_total__gte=0)
                    & Q(tax_total__gte=0)
                    & Q(line_total__gte=0)
                ),
                name="orders_item_totals_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(line_total=F("line_subtotal") - F("discount_total") + F("tax_total")),
                name="orders_item_total_matches_components",
            ),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk:
            raise ValidationError("Order item snapshots are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Order item snapshots are immutable.")

    def __str__(self) -> str:
        return f"{self.order.public_id}: {self.sku} × {self.quantity}"
