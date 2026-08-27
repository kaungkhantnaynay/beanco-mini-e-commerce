from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import Q


def validate_product_image_size(image: object) -> None:
    size = getattr(image, "size", 0)
    if size > 10 * 1024 * 1024:
        raise ValidationError("Product images must be 10 MB or smaller.")


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "name")
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class ProductType(models.TextChoices):
        COFFEE = "coffee", "Coffee"
        EQUIPMENT = "equipment", "Equipment"
        DRINKWARE = "drinkware", "Drinkware"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    description = models.TextField()
    profile = models.CharField(max_length=240, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ProductVariant(models.Model):
    class Grind(models.TextChoices):
        WHOLE_BEAN = "whole_bean", "Whole bean"
        ESPRESSO = "espresso", "Espresso"
        FILTER = "filter", "Filter"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    option_name = models.CharField(max_length=100, blank=True)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    grind = models.CharField(max_length=20, choices=Grind.choices, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("price", "sku")
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name="catalog_variant_price_gte_0"),
            models.CheckConstraint(
                condition=Q(weight_grams__isnull=True) | Q(weight_grams__gt=0),
                name="catalog_variant_weight_gt_0",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.product_id and self.product.product_type == Product.ProductType.COFFEE:
            errors: dict[str, str] = {}
            if self.weight_grams not in {250, 500, 1000}:
                errors["weight_grams"] = "Coffee weight must be 250, 500, or 1000 g."
            if not self.grind:
                errors["grind"] = "Coffee variants require a grind option."
            if errors:
                raise ValidationError(errors)
        elif self.weight_grams is not None or self.grind:
            raise ValidationError("Weight and grind options are only valid for coffee products.")

    def __str__(self) -> str:
        return f"{self.product.name} — {self.sku}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="images",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        upload_to="products/%Y/%m/",
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=("jpg", "jpeg", "png", "webp")),
            validate_product_image_size,
        ],
    )
    external_url = models.URLField(max_length=1000, blank=True)
    alt_text = models.CharField(max_length=240)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("display_order", "id")
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(image__gt="") & Q(external_url="")) | (Q(image="") & Q(external_url__gt=""))
                ),
                name="catalog_image_has_one_source",
            )
        ]

    def clean(self) -> None:
        super().clean()
        if bool(self.image) == bool(self.external_url):
            raise ValidationError("Provide exactly one managed image or external URL.")
        variant = self.variant
        if self.variant_id and variant is not None and variant.product_id != self.product_id:
            raise ValidationError({"variant": "The variant must belong to this product."})

    def __str__(self) -> str:
        return self.alt_text
