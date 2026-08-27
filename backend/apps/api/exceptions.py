from collections.abc import Mapping
from typing import Any

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.response import Response
from rest_framework.views import exception_handler


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    response = exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if response.status_code == status.HTTP_400_BAD_REQUEST and isinstance(data, Mapping):
        response.data = {
            "code": "validation_error",
            "detail": "One or more fields are invalid.",
            "fields": data,
        }
        return response

    detail = data.get("detail") if isinstance(data, Mapping) else data
    code = detail.code if isinstance(detail, ErrorDetail) else "request_error"
    response.data = {"code": code, "detail": str(detail), "fields": {}}
    return response
