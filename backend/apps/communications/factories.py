import factory
from django.utils import timezone

from .models import NewsletterSubscription, PartnershipInquiry


class PartnershipInquiryFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = PartnershipInquiry

    name = factory.Sequence(lambda number: f"Contact {number}")
    email = factory.Sequence(lambda number: f"contact{number}@example.test")
    company = "Example Hospitality"
    inquiry_type = PartnershipInquiry.InquiryType.HOSPITALITY
    requirements = "Coffee service for a fictional twenty-room hotel."
    consent = True
    consent_at = factory.LazyFunction(timezone.now)


class NewsletterSubscriptionFactory(factory.django.DjangoModelFactory):  # type: ignore[type-arg]
    class Meta:
        model = NewsletterSubscription

    email = factory.Sequence(lambda number: f"subscriber{number}@example.test")
    consent_source = "test"
    consent_at = factory.LazyFunction(timezone.now)
