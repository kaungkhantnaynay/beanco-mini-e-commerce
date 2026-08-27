import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client

from apps.accounts.factories import UserFactory


@pytest.mark.django_db
def test_user_manager_normalizes_email() -> None:
    user = get_user_model().objects.create_user(" Customer@Example.TEST ", "password")

    assert user.email == "customer@example.test"


@pytest.mark.django_db
def test_email_is_unique_after_normalization() -> None:
    UserFactory(email="customer@example.test")

    with pytest.raises(IntegrityError):
        get_user_model().objects.create_user("CUSTOMER@example.test", "password")


@pytest.mark.django_db
def test_superuser_can_sign_in_to_django_admin(client: Client) -> None:
    get_user_model().objects.create_superuser("admin@example.test", "strong-password")

    assert client.login(email="admin@example.test", password="strong-password")
    response = client.get("/admin/")

    assert response.status_code == 200
