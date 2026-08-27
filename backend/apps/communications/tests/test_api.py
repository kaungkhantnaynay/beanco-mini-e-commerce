from typing import Any
from unittest.mock import patch

import pytest
from django.core import mail
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from apps.communications.models import NewsletterSubscription, PartnershipInquiry


def inquiry_payload() -> dict[str, object]:
    return {
        "name": "Arun Example",
        "email": " Arun@Example.TEST ",
        "phone": "+66 00 000 0000",
        "company": "Example Hotel",
        "inquiry_type": "hospitality",
        "requirements": "Coffee service for a fictional boutique hotel.",
        "consent": True,
        "website": "",
    }


@pytest.mark.django_db
def test_inquiry_is_validated_stored_and_notified(
    client: Client, django_capture_on_commit_callbacks: Any
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        response = client.post(
            reverse("inquiry-create"), inquiry_payload(), content_type="application/json"
        )

    assert response.status_code == 201
    inquiry = PartnershipInquiry.objects.get()
    assert inquiry.email == "arun@example.test"
    assert inquiry.consent_at is not None
    assert len(mail.outbox) == 2


@pytest.mark.django_db
def test_inquiry_rejects_missing_consent_and_honeypot(client: Client) -> None:
    payload = inquiry_payload()
    payload.update({"consent": False, "website": "spam.example"})

    response = client.post(reverse("inquiry-create"), payload, content_type="application/json")

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert set(response.json()["fields"]) == {"consent", "website"}
    assert not PartnershipInquiry.objects.exists()


@pytest.mark.django_db
def test_notification_failure_does_not_rollback_inquiry(
    client: Client, django_capture_on_commit_callbacks: Any
) -> None:
    with patch("apps.communications.notifications.send_mail", side_effect=RuntimeError("offline")):
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                reverse("inquiry-create"), inquiry_payload(), content_type="application/json"
            )

    assert response.status_code == 201
    assert PartnershipInquiry.objects.count() == 1


@pytest.mark.django_db
def test_newsletter_subscription_is_idempotent_and_privacy_safe(
    client: Client, django_capture_on_commit_callbacks: Any
) -> None:
    payload = {
        "email": " News@Example.TEST ",
        "consent": True,
        "consent_source": "storefront_footer",
        "website": "",
    }

    with django_capture_on_commit_callbacks(execute=True):
        first = client.post(
            reverse("newsletter-subscription-create"), payload, content_type="application/json"
        )
        second = client.post(
            reverse("newsletter-subscription-create"), payload, content_type="application/json"
        )

    assert first.status_code == second.status_code == 202
    assert first.json() == second.json() == {"detail": "If eligible, this address is subscribed."}
    assert NewsletterSubscription.objects.count() == 1
    assert NewsletterSubscription.objects.get().email == "news@example.test"
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_inquiry_is_throttled(client: Client) -> None:
    cache.clear()
    with patch.dict(
        "rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES", {"inquiries": "1/hour"}
    ):
        first = client.post(
            reverse("inquiry-create"), inquiry_payload(), content_type="application/json"
        )
        second = client.post(
            reverse("inquiry-create"), inquiry_payload(), content_type="application/json"
        )

    assert first.status_code == 201
    assert second.status_code == 429
    assert second.json()["code"] == "throttled"
    cache.clear()
