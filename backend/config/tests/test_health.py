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


@pytest.mark.django_db
def test_ready_health_endpoint_checks_database(client: Client) -> None:
    with patch("config.health.connections") as connections:
        connections.__getitem__.return_value.ensure_connection = Mock()
        response = client.get(reverse("health-ready"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_ready_health_endpoint_reports_database_failure(client: Client) -> None:
    with patch("config.health.connections") as connections:
        connections.__getitem__.return_value.ensure_connection.side_effect = DatabaseError
        response = client.get(reverse("health-ready"))

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
