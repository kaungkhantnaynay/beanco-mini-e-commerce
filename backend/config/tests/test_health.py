from unittest.mock import Mock, patch

import pytest
from django.db import DatabaseError
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_live_health_endpoint(client: Client) -> None:
    response = client.get(reverse("health-live"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.django_db
def test_ready_health_endpoint_checks_database(client: Client) -> None:
    with patch("config.health.connections") as connections:
        cursor = Mock()
        connections.__getitem__.return_value.cursor.return_value.__enter__.return_value = cursor
        response = client.get(reverse("health-ready"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    cursor.execute.assert_called_once_with("SELECT 1")
    assert response.headers["Cache-Control"] == "no-store"


@pytest.mark.django_db
def test_ready_health_endpoint_reports_database_failure(client: Client) -> None:
    with patch("config.health.connections") as connections:
        connections.__getitem__.return_value.cursor.side_effect = DatabaseError
        response = client.get(reverse("health-ready"))

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert response.headers["Cache-Control"] == "no-store"
