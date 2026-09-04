from decimal import Decimal
from types import SimpleNamespace
from typing import cast

import pytest
from django.core.exceptions import ValidationError
from django.test import override_settings

from apps.catalog.factories import ProductFactory, ProductImageFactory, ProductVariantFactory
from apps.catalog.models import Product, ProductVariant, validate_product_image_size


@pytest.mark.django_db
def test_coffee_variant_requires_approved_weight_and_grind() -> None:
    product = ProductFactory(product_type=Product.ProductType.COFFEE)
    variant = ProductVariantFactory.build(product=product, weight_grams=340, grind="")

    with pytest.raises(ValidationError) as error:
        variant.full_clean()

    assert "weight_grams" in error.value.message_dict
    assert "grind" in error.value.message_dict


@pytest.mark.django_db
def test_non_coffee_variant_rejects_coffee_options() -> None:
    product = ProductFactory(product_type=Product.ProductType.EQUIPMENT)
    variant = ProductVariantFactory.build(product=product, weight_grams=250)

    with pytest.raises(ValidationError):
        variant.full_clean()


@pytest.mark.django_db
def test_variant_price_uses_decimal() -> None:
    variant = cast(ProductVariant, ProductVariantFactory(price=Decimal("650.25")))

    variant.refresh_from_db()

    assert variant.price == Decimal("650.25")


@pytest.mark.django_db
def test_image_variant_must_belong_to_same_product() -> None:
    image = ProductImageFactory.build(
        product=ProductFactory(), variant=ProductVariantFactory(product=ProductFactory())
    )

    with pytest.raises(ValidationError):
        image.full_clean()


def test_product_image_size_is_limited() -> None:
    oversized_image = SimpleNamespace(size=10 * 1024 * 1024 + 1)

    with pytest.raises(ValidationError):
        validate_product_image_size(oversized_image)


@override_settings(PRODUCT_IMAGE_MAX_BYTES=1024 * 1024)
def test_product_image_size_uses_configured_limit() -> None:
    with pytest.raises(ValidationError, match="1 MB or smaller"):
        validate_product_image_size(SimpleNamespace(size=1024 * 1024 + 1))
