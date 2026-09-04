"""Request correlation and privacy-safe access logging."""

import logging
from collections.abc import Callable
from time import monotonic
from uuid import UUID, uuid4

from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("beanco.request")


def _request_id(value: str | None) -> str:
    if value:
        try:
            return str(UUID(value))
        except ValueError:
            pass
    return str(uuid4())


class RequestCorrelationMiddleware:
    """Attach a safe request ID and log only approved request metadata."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = _request_id(request.headers.get("X-Request-ID"))
        request.request_id = request_id  # type: ignore[attr-defined]
        started_at = monotonic()
        metadata = {
            "request_id": request_id,
            "method": request.method,
            "path": request.path,
        }

        try:
            response = self.get_response(request)
        except Exception as exc:
            logger.error(
                "request_failed",
                extra={**metadata, "exception_type": type(exc).__name__},
            )
            raise

        response["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                **metadata,
                "status_code": response.status_code,
                "duration_ms": round((monotonic() - started_at) * 1000, 2),
            },
        )
        return response
