import pytest
from django.db import IntegrityError

from apps.communications.factories import NewsletterSubscriptionFactory, PartnershipInquiryFactory


@pytest.mark.django_db
def test_communication_emails_are_normalized() -> None:
    inquiry = PartnershipInquiryFactory(email=" Contact@Example.TEST ")
    subscription = NewsletterSubscriptionFactory(email=" News@Example.TEST ")

    assert inquiry.email == "contact@example.test"
    assert subscription.email == "news@example.test"


@pytest.mark.django_db(transaction=True)
def test_newsletter_email_is_case_insensitively_unique() -> None:
    NewsletterSubscriptionFactory(email="news@example.test")

    with pytest.raises(IntegrityError):
        NewsletterSubscriptionFactory(email="NEWS@example.test")
