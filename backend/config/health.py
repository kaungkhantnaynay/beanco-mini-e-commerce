"""Liveness and readiness endpoints for platform health checks."""

from django.db import DatabaseError, connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def live(_: object) -> JsonResponse:
    """Report that the application process can receive requests."""
    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response


@require_GET
def ready(_: object) -> JsonResponse:
    """Report database readiness without exposing connection details."""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        response = JsonResponse({"status": "unavailable"}, status=503)
        response["Cache-Control"] = "no-store"
        return response
    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response
