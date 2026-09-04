import json
import logging
import sys
from uuid import UUID, uuid4

import pytest
from django.http import HttpRequest, HttpResponse

from config.logging import JsonFormatter
from config.middleware import RequestCorrelationMiddleware


def test_request_middleware_preserves_valid_id_and_logs_safe_metadata(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request_id = str(uuid4())
    request = HttpRequest()
    request.method = "GET"
    request.path = "/health/live/"
    request.META["HTTP_X_REQUEST_ID"] = request_id
    request.META["QUERY_STRING"] = "token=must-not-be-logged"
    middleware = RequestCorrelationMiddleware(lambda _: HttpResponse(status=204))

    with caplog.at_level(logging.INFO, logger="beanco.request"):
        response = middleware(request)

    record = next(record for record in caplog.records if record.message == "request_completed")
    assert response.headers["X-Request-ID"] == request_id
    assert record.__dict__["request_id"] == request_id
    assert record.__dict__["method"] == "GET"
    assert record.__dict__["path"] == "/health/live/"
    assert record.__dict__["status_code"] == 204
    assert "token" not in record.getMessage()


def test_request_middleware_replaces_invalid_request_id() -> None:
    request = HttpRequest()
    request.method = "GET"
    request.path = "/"
    request.META["HTTP_X_REQUEST_ID"] = "unsafe\nvalue"

    response = RequestCorrelationMiddleware(lambda _: HttpResponse())(request)

    assert str(UUID(response.headers["X-Request-ID"])) == response.headers["X-Request-ID"]


def test_json_formatter_excludes_secrets_and_exception_messages() -> None:
    try:
        raise RuntimeError("secret exception detail")
    except RuntimeError:
        record = logging.LogRecord(
            name="beanco.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="request_failed",
            args=(),
            exc_info=sys.exc_info(),
        )
    request_id = str(uuid4())
    record.__dict__["password"] = "secret password"
    record.__dict__["request_id"] = request_id

    payload = json.loads(JsonFormatter().format(record))

    assert payload["message"] == "request_failed"
    assert payload["exception_type"] == "RuntimeError"
    assert payload["request_id"] == request_id
    assert "password" not in payload
    assert "secret" not in json.dumps(payload)
