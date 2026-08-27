from typing import Any

from django.conf import settings
from django.db import models
from django.db.models.functions import Lower


class PartnershipInquiry(models.Model):
    class InquiryType(models.TextChoices):
        HOSPITALITY = "hospitality", "Hospitality"
        OFFICE = "office", "Office"
        EVENT = "event", "Event"
        WHOLESALE = "wholesale", "Wholesale"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        CLOSED = "closed", "Closed"
        SPAM = "spam", "Spam"

    name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=180, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=InquiryType.choices)
    requirements = models.TextField()
    consent = models.BooleanField()
    consent_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_partnership_inquiries",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} — {self.get_inquiry_type_display()}"


class NewsletterSubscription(models.Model):
    class Status(models.TextChoices):
        SUBSCRIBED = "subscribed", "Subscribed"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"

    email = models.EmailField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBSCRIBED)
    consent_source = models.CharField(max_length=120)
    consent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(Lower("email"), name="communications_newsletter_email_ci")
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
