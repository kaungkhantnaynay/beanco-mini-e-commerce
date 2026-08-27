from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer[Category]):
    class Meta:
        model = Category
        fields = ("name", "slug", "description", "display_order")


class ProductImageSerializer(serializers.ModelSerializer[ProductImage]):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("url", "alt_text", "display_order")

    def get_url(self, obj: ProductImage) -> str:
        if obj.external_url:
            return obj.external_url
        if not obj.image:
            return ""
        request = self.context.get("request")
        url = str(obj.image.url)
        return str(request.build_absolute_uri(url)) if request else url


class ProductVariantSerializer(serializers.ModelSerializer[ProductVariant]):
    available = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "sku",
            "option_name",
            "weight_grams",
            "grind",
            "price",
            "available",
            "available_quantity",
        )

    def _inventory(self, obj: ProductVariant) -> Any:
        try:
            return obj.inventory
        except ProductVariant.inventory.RelatedObjectDoesNotExist:
            return None

    def get_available(self, obj: ProductVariant) -> bool:
        inventory = self._inventory(obj)
        return bool(inventory and inventory.available_to_sell > 0)

    def get_available_quantity(self, obj: ProductVariant) -> int:
        inventory = self._inventory(obj)
        return inventory.available_to_sell if inventory else 0


class ProductListSerializer(serializers.ModelSerializer[Product]):
    category = CategorySerializer(read_only=True)
    starting_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    available = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "name",
            "slug",
            "product_type",
            "description",
            "profile",
            "is_featured",
            "category",
            "starting_price",
            "available",
            "primary_image",
        )

    @extend_schema_field(ProductImageSerializer(allow_null=True))
    def get_primary_image(self, obj: Product) -> dict[str, Any] | None:
        image = next(iter(obj.images.all()), None)
        return ProductImageSerializer(image, context=self.context).data if image else None


class ProductDetailSerializer(ProductListSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = (  # type: ignore[assignment]
            "name",
            "slug",
            "product_type",
            "description",
            "profile",
            "is_featured",
            "category",
            "starting_price",
            "available",
            "primary_image",
            "seo_title",
            "seo_description",
            "variants",
            "images",
        )
