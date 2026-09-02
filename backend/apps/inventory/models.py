from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from apps.catalog.models import ProductVariant


class ImmutableInventoryTransactionQuerySet(models.QuerySet["InventoryTransaction"]):
    def update(self, **kwargs: Any) -> int:
        raise ValidationError("Inventory transactions are immutable.")

    def delete(self) -> tuple[int, dict[str, int]]:
        raise ValidationError("Inventory transactions are immutable.")


class InventoryRecord(models.Model):
    class StockPolicy(models.TextChoices):
        TRACKED = "tracked", "Tracked"
        INQUIRY_ONLY = "inquiry_only", "Inquiry only"

    variant = models.OneToOneField(
        ProductVariant, on_delete=models.CASCADE, related_name="inventory"
    )
    available_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    stock_policy = models.CharField(
        max_length=20, choices=StockPolicy.choices, default=StockPolicy.TRACKED
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(reserved_quantity__lte=F("available_quantity")),
                name="inventory_reserved_lte_available",
            )
        ]

    @property
    def available_to_sell(self) -> int:
        return self.available_quantity - self.reserved_quantity

    def __str__(self) -> str:
        return f"Inventory for {self.variant.sku}"


class InventoryTransaction(models.Model):
    objects = ImmutableInventoryTransactionQuerySet.as_manager()

    class Reason(models.TextChoices):
        INITIAL = "initial", "Initial stock"
        RECEIPT = "receipt", "Stock receipt"
        ADJUSTMENT = "adjustment", "Manual adjustment"
        RESERVATION = "reservation", "Reservation"
        RELEASE = "release", "Reservation release"
        SALE = "sale", "Sale"
        CANCELLATION = "cancellation", "Order cancellation"

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="inventory_transactions"
    )
    quantity_change = models.IntegerField()
    reserved_change = models.IntegerField(default=0)
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reference = models.CharField(max_length=160, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="inventory_transactions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.CheckConstraint(
                condition=~(Q(quantity_change=0) & Q(reserved_change=0)),
                name="inventory_transaction_has_change",
            )
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self.pk:
            raise ValidationError("Inventory transactions are immutable.")
        super().save(*args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Inventory transactions are immutable.")

    def __str__(self) -> str:
        return f"{self.variant.sku}: {self.quantity_change:+d}"
