import re
from typing import Any, cast

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Cart, CartItem
from .services import ZERO_MONEY, money


class StrictInputSerializer(serializers.Serializer[Any]):
    def to_internal_value(self, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            unknown = set(data) - set(self.fields)
            if unknown:
                raise serializers.ValidationError(
                    {field: ["This field is not allowed."] for field in sorted(unknown)}
                )
        return cast(dict[str, Any], super().to_internal_value(data))


class AddCartItemSerializer(StrictInputSerializer):
    variant_sku = serializers.CharField(max_length=64)
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class UpdateCartItemSerializer(StrictInputSerializer):
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class ShippingAddressSerializer(StrictInputSerializer):
    full_name = serializers.CharField(min_length=2, max_length=120)
    phone = serializers.CharField(min_length=9, max_length=24)
    address_line_1 = serializers.CharField(min_length=3, max_length=200)
    address_line_2 = serializers.CharField(max_length=200, required=False, allow_blank=True)
    subdistrict = serializers.CharField(min_length=2, max_length=100)
    district = serializers.CharField(min_length=2, max_length=100)
    province = serializers.CharField(min_length=2, max_length=100)
    postal_code = serializers.RegexField(r"^\d{5}$")
    country_code = serializers.ChoiceField(choices=("TH",), default="TH")

    def validate_phone(self, value: str) -> str:
        normalized = re.sub(r"[\s\-()]", "", value)
        if not re.fullmatch(r"(?:\+66|0)\d{8,9}", normalized):
            raise serializers.ValidationError("Enter a valid Thai phone number.")
        return normalized

    def validate_country_code(self, value: str) -> str:
        return value.upper()


class CheckoutPreviewInputSerializer(StrictInputSerializer):
    shipping_address = ShippingAddressSerializer()
    shipping_method = serializers.ChoiceField(choices=("standard_th",))


class ShippingMethodSerializer(serializers.Serializer[dict[str, Any]]):
    code = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    fee = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    minimum_business_days = serializers.IntegerField(read_only=True)
    maximum_business_days = serializers.IntegerField(read_only=True)


class CartItemSerializer(serializers.ModelSerializer[CartItem]):
    variant_sku = serializers.CharField(source="variant.sku", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    option_name = serializers.CharField(source="variant.option_name", read_only=True)
    unit_price = serializers.DecimalField(
        source="variant.price", max_digits=10, decimal_places=2, read_only=True
    )
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "public_id",
            "variant_sku",
            "product_name",
            "option_name",
            "quantity",
            "unit_price",
            "line_total",
        )
        read_only_fields = fields

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_line_total(self, obj: CartItem) -> str:
        return format(money(obj.variant.price * obj.quantity), ".2f")


class CartSerializer(serializers.ModelSerializer[Cart]):
    currency = serializers.CharField(default="THB", read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    discount_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=ZERO_MONEY, read_only=True
    )
    shipping_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=ZERO_MONEY, read_only=True
    )
    tax_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, default=ZERO_MONEY, read_only=True
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "public_id",
            "currency",
            "items",
            "subtotal",
            "discount_total",
            "shipping_total",
            "tax_total",
            "total",
            "expires_at",
        )
        read_only_fields = fields

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_subtotal(self, obj: Cart) -> str:
        subtotal = sum(
            (item.variant.price * item.quantity for item in obj.items.all()),
            ZERO_MONEY,
        )
        return format(money(subtotal), ".2f")

    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total(self, obj: Cart) -> str:
        return self.get_subtotal(obj)


class CheckoutPreviewSerializer(serializers.Serializer[dict[str, Any]]):
    cart = CartSerializer(read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)
