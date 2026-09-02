from typing import Any

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from .models import Address, Order, OrderItem
from .services import transition_order


class OrderItemInline(admin.TabularInline):  # type: ignore[type-arg]
    model = OrderItem
    extra = 0
    can_delete = False
    fields = (
        "product_name",
        "sku",
        "option_name",
        "unit_price",
        "quantity",
        "discount_total",
        "tax_total",
        "line_total",
    )
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = (
        "public_id",
        "customer_email",
        "status",
        "total",
        "currency",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("public_id", "customer_email", "items__sku", "items__product_name")
    date_hierarchy = "created_at"
    list_select_related = ("shipping_address", "user")
    inlines = (OrderItemInline,)
    actions = (
        "mark_confirmed",
        "mark_fulfilling",
        "mark_shipped",
        "mark_delivered",
        "mark_cancelled",
    )
    readonly_fields = (
        "public_id",
        "cart",
        "user",
        "address_link",
        "customer_email",
        "currency",
        "shipping_method",
        "shipping_method_name",
        "subtotal",
        "discount_total",
        "shipping_total",
        "tax_total",
        "total",
        "status",
        "stock_restored",
        "created_at",
        "updated_at",
    )

    @admin.display(description="Shipping address")
    def address_link(self, obj: Order) -> str:
        url = reverse("admin:orders_address_change", args=(obj.shipping_address_id,))
        return format_html('<a href="{}">{}</a>', url, obj.shipping_address)

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False

    def _transition(self, request: HttpRequest, queryset: Any, target: str) -> None:
        successes = 0
        for order in queryset:
            try:
                transition_order(order=order, target_status=target, actor=request.user)
                successes += 1
            except ValidationError as exc:
                self.message_user(request, f"{order}: {exc.message}", level=messages.ERROR)
        if successes:
            self.message_user(request, f"Updated {successes} order(s).", level=messages.SUCCESS)

    @admin.action(description="Mark selected orders confirmed")
    def mark_confirmed(self, request: HttpRequest, queryset: Any) -> None:
        self._transition(request, queryset, Order.Status.CONFIRMED)

    @admin.action(description="Mark selected orders fulfilling")
    def mark_fulfilling(self, request: HttpRequest, queryset: Any) -> None:
        self._transition(request, queryset, Order.Status.FULFILLING)

    @admin.action(description="Mark selected orders shipped")
    def mark_shipped(self, request: HttpRequest, queryset: Any) -> None:
        self._transition(request, queryset, Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders delivered")
    def mark_delivered(self, request: HttpRequest, queryset: Any) -> None:
        self._transition(request, queryset, Order.Status.DELIVERED)

    @admin.action(description="Cancel selected orders and restore stock")
    def mark_cancelled(self, request: HttpRequest, queryset: Any) -> None:
        self._transition(request, queryset, Order.Status.CANCELLED)


class ReadOnlySnapshotAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return bool(obj) and request.method in {"GET", "HEAD"}

    def has_delete_permission(self, request: HttpRequest, obj: object | None = None) -> bool:
        return False

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: object | None = None,
    ) -> tuple[str, ...]:
        return tuple(field.name for field in self.model._meta.fields)


@admin.register(Address)
class AddressAdmin(ReadOnlySnapshotAdmin):
    list_display = ("public_id", "full_name", "province", "postal_code", "created_at")
    search_fields = ("public_id", "full_name", "phone", "province", "postal_code")


@admin.register(OrderItem)
class OrderItemAdmin(ReadOnlySnapshotAdmin):
    list_display = ("order", "sku", "product_name", "quantity", "line_total")
    search_fields = ("order__public_id", "sku", "product_name")
    list_select_related = ("order", "variant")
