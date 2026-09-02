from typing import Any, cast

from rest_framework import serializers

from apps.carts.serializers import ShippingAddressSerializer

from .models import Order, OrderItem


class OrderCreateSerializer(serializers.Serializer[dict[str, Any]]):
    customer_email = serializers.EmailField(max_length=254)
    shipping_address = ShippingAddressSerializer()
    shipping_method = serializers.ChoiceField(choices=("standard_th",))

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed."] for field in sorted(unknown)}
                )
        return cast(dict[str, Any], super().to_internal_value(data))


class OrderItemSerializer(serializers.ModelSerializer[OrderItem]):
    class Meta:
        model = OrderItem
        fields = (
            "product_name",
            "sku",
            "option_name",
            "weight_grams",
            "grind",
            "unit_price",
            "quantity",
            "line_subtotal",
            "discount_total",
            "tax_total",
            "line_total",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer[Order]):
    shipping_address = ShippingAddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "public_id",
            "status",
            "customer_email",
            "currency",
            "shipping_method",
            "shipping_method_name",
            "shipping_address",
            "items",
            "subtotal",
            "discount_total",
            "shipping_total",
            "tax_total",
            "total",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class OrderStatusSerializer(serializers.ModelSerializer[Order]):
    class Meta:
        model = Order
        fields = ("public_id", "status", "currency", "total", "created_at", "updated_at")
        read_only_fields = fields
