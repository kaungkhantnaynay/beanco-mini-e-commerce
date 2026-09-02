import json

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_openapi_schema_is_available(client: Client) -> None:
    response = client.get(reverse("openapi-schema"), {"format": "json"})

    assert response.status_code == 200
    schema = json.loads(response.content)
    assert "openapi" in schema
    assert {
        "/api/v1/categories/",
        "/api/v1/products/",
        "/api/v1/products/{slug}/",
        "/api/v1/inquiries/",
        "/api/v1/newsletter/subscriptions/",
        "/api/v1/cart/",
        "/api/v1/cart/items/",
        "/api/v1/cart/items/{public_id}/",
        "/api/v1/checkout/preview/",
        "/api/v1/orders/",
        "/api/v1/orders/{public_id}/status/",
    }.issubset(schema["paths"])
    assert (
        schema["components"]["schemas"]["ProductVariant"]["properties"]["price"]["type"] == "string"
    )
    starting_price = schema["components"]["schemas"]["ProductList"]["properties"]["starting_price"]
    assert starting_price["type"] == "string"
    assert starting_price.get("nullable") is not True
    cart_schema = schema["components"]["schemas"]["Cart"]["properties"]
    assert cart_schema["subtotal"]["type"] == "string"
    assert cart_schema["total"]["type"] == "string"
    preview_schema = schema["components"]["schemas"]["CheckoutPreview"]["properties"]
    assert preview_schema["shipping_method"]["allOf"][0]["$ref"].endswith("/ShippingMethod")
    order_schema = schema["components"]["schemas"]["Order"]["properties"]
    assert order_schema["total"]["type"] == "string"
    assert order_schema["public_id"]["format"] == "uuid"
