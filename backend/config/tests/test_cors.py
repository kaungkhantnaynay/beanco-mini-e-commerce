from django.conf import settings


def test_cors_allows_idempotent_order_header() -> None:
    assert "idempotency-key" in settings.CORS_ALLOW_HEADERS
    assert settings.CORS_ALLOW_CREDENTIALS is True
    assert "X-Request-ID" in settings.CORS_EXPOSE_HEADERS
