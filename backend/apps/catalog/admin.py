from django.contrib import admin

from .models import Category, Product, ProductImage, ProductVariant


class ProductVariantInline(admin.TabularInline):  # type: ignore[type-arg]
    model = ProductVariant
    extra = 0
    fields = ("sku", "option_name", "weight_grams", "grind", "price", "is_active")


class ProductImageInline(admin.TabularInline):  # type: ignore[type-arg]
    model = ProductImage
    extra = 0
    fields = ("variant", "image", "external_url", "alt_text", "display_order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "slug", "is_active", "display_order")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "category", "product_type", "is_featured", "is_active")
    list_filter = ("is_active", "is_featured", "product_type", "category")
    search_fields = ("name", "slug", "description", "profile", "variants__sku")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("category",)
    inlines = (ProductVariantInline, ProductImageInline)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("sku", "product", "weight_grams", "grind", "price", "is_active")
    list_filter = ("is_active", "grind", "product__product_type")
    search_fields = ("sku", "product__name")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("alt_text", "product", "variant", "display_order")
    search_fields = ("alt_text", "product__name", "variant__sku")
    autocomplete_fields = ("product", "variant")
    list_select_related = ("product", "variant")
