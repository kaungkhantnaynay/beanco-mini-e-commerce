from typing import Any, cast

from django.contrib import admin
from django.db import transaction
from django.http import HttpRequest

from .models import InventoryRecord, InventoryTransaction


@admin.register(InventoryRecord)
class InventoryRecordAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "variant",
        "available_quantity",
        "reserved_quantity",
        "available_to_sell",
        "stock_policy",
        "updated_at",
    )
    list_filter = ("stock_policy", "variant__product__product_type")
    search_fields = ("variant__sku", "variant__product__name")
    autocomplete_fields = ("variant",)
    list_select_related = ("variant", "variant__product")

    @transaction.atomic
    def save_model(
        self, request: HttpRequest, obj: InventoryRecord, form: Any, change: bool
    ) -> None:
        old_available = 0
        old_reserved = 0
        if change:
            previous = InventoryRecord.objects.select_for_update().get(pk=obj.pk)
            old_available = previous.available_quantity
            old_reserved = previous.reserved_quantity
        super().save_model(request, obj, form, change)
        quantity_change = obj.available_quantity - old_available
        reserved_change = obj.reserved_quantity - old_reserved
        if quantity_change or reserved_change:
            InventoryTransaction.objects.create(
                variant=obj.variant,
                quantity_change=quantity_change,
                reserved_change=reserved_change,
                reason=(
                    InventoryTransaction.Reason.ADJUSTMENT
                    if change
                    else InventoryTransaction.Reason.INITIAL
                ),
                reference="Django Admin inventory edit",
                actor=cast(Any, request.user) if request.user.is_authenticated else None,
            )


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "variant",
        "quantity_change",
        "reserved_change",
        "reason",
        "reference",
        "actor",
        "created_at",
    )
    list_filter = ("reason", "created_at")
    search_fields = ("variant__sku", "variant__product__name", "reference", "actor__email")
    list_select_related = ("variant", "variant__product", "actor")
    date_hierarchy = "created_at"

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False
