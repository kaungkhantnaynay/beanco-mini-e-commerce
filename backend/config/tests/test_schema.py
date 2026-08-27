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
    }.issubset(schema["paths"])
    assert (
        schema["components"]["schemas"]["ProductVariant"]["properties"]["price"]["type"] == "string"
    )
    starting_price = schema["components"]["schemas"]["ProductList"]["properties"]["starting_price"]
    assert starting_price["type"] == "string"
    assert starting_price.get("nullable") is not True
