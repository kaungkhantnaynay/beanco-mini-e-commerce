from decimal import Decimal
from typing import cast

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.catalog.factories import CategoryFactory, ProductFactory, ProductImageFactory
from apps.catalog.models import Product
from apps.inventory.factories import InventoryRecordFactory
from apps.inventory.models import InventoryRecord


@pytest.mark.django_db
def test_anonymous_catalog_lists_only_active_records(client: Client) -> None:
    active_product = ProductFactory(name="Available Coffee", slug="available-coffee")
    InventoryRecordFactory(variant__product=active_product, available_quantity=5)
    ProductFactory(name="Hidden Product", is_active=False)
    ProductFactory(name="Hidden Category Product", category=CategoryFactory(is_active=False))

    response = client.get(reverse("product-list"))

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["results"]] == ["available-coffee"]
    assert response.json()["results"][0]["starting_price"] == "850.00"


@pytest.mark.django_db
def test_product_detail_uses_slug_and_hides_inactive_variants(client: Client) -> None:
    product = ProductFactory(slug="detail-coffee")
    available = cast(
        InventoryRecord,
        InventoryRecordFactory(variant__product=product, available_quantity=3),
    )
    InventoryRecordFactory(variant__product=product, variant__is_active=False)
    ProductImageFactory(product=product)

    response = client.get(reverse("product-detail", args=[product.slug]))

    assert response.status_code == 200
    assert response.json()["variants"] == [
        {
            "sku": available.variant.sku,
            "option_name": "",
            "weight_grams": 250,
            "grind": "whole_bean",
            "price": "850.00",
            "available": True,
            "available_quantity": 3,
        }
    ]
    assert client.get(reverse("product-detail", args=["missing"])).status_code == 404


@pytest.mark.django_db
def test_product_filters_search_price_availability_and_ordering(client: Client) -> None:
    category = CategoryFactory(slug="coffee")
    first = ProductFactory(
        category=category,
        name="Alpha Coffee",
        slug="alpha",
        is_featured=True,
        profile="floral",
    )
    InventoryRecordFactory(variant__product=first, variant__price=Decimal("650.00"))
    second = ProductFactory(category=category, name="Beta Coffee", slug="beta")
    InventoryRecordFactory(
        variant__product=second,
        variant__price=Decimal("900.00"),
        available_quantity=0,
    )

    response = client.get(
        reverse("product-list"),
        {
            "category": "coffee",
            "type": Product.ProductType.COFFEE,
            "featured": "true",
            "availability": "true",
            "search": "floral",
            "minimum_price": "600.00",
            "maximum_price": "700.00",
            "ordering": "-price",
        },
    )

    assert response.status_code == 200
    assert [item["slug"] for item in response.json()["results"]] == ["alpha"]


@pytest.mark.django_db
def test_invalid_product_filter_uses_stable_error_shape(client: Client) -> None:
    response = client.get(reverse("product-list"), {"minimum_price": "not-money"})

    assert response.status_code == 400
    assert response.json() == {
        "code": "validation_error",
        "detail": "One or more fields are invalid.",
        "fields": {"minimum_price": ["Enter a valid decimal amount."]},
    }


@pytest.mark.django_db
def test_product_list_query_count_is_bounded(client: Client) -> None:
    for number in range(6):
        product = ProductFactory(name=f"Coffee {number}")
        InventoryRecordFactory(variant__product=product)
        ProductImageFactory(product=product)

    with CaptureQueriesContext(connection) as queries:
        response = client.get(reverse("product-list"))

    assert response.status_code == 200
    assert len(queries) <= 5
