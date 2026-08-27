from decimal import Decimal

import factory

from .models import Category, Product, ProductImage, ProductVariant


class CategoryFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = Category

    name = factory.Sequence(lambda number: f"Category {number}")
    slug = factory.Sequence(lambda number: f"category-{number}")


class ProductFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda number: f"Product {number}")
    slug = factory.Sequence(lambda number: f"product-{number}")
    product_type = Product.ProductType.COFFEE
    description = "A fictional BeanCo test product."
    profile = "Cocoa, citrus"


class ProductVariantFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda number: f"TEST-{number:04d}")
    weight_grams = 250
    grind = ProductVariant.Grind.WHOLE_BEAN
    price = Decimal("850.00")


class ProductImageFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    external_url = factory.Sequence(lambda number: f"https://example.test/product-{number}.jpg")
    alt_text = "Fictional product image"
