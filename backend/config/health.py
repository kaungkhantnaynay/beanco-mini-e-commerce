"""Liveness and readiness endpoints for platform health checks."""

from django.db import DatabaseError, connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live(_: object) -> JsonResponse:
    """Report that the application process can receive requests."""
    return JsonResponse({"status": "ok"})


@require_GET
def ready(_: object) -> JsonResponse:
    """Report database readiness without exposing connection details."""
    try:
        connections["default"].ensure_connection()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})
