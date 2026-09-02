import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.orders.models import Order


class PaymentAttempt(models.Model):
    class Status(models.TextChoices):
        CREATING = "creating", "Creating"
        OPEN = "open", "Open"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        REFUNDED = "refunded", "Refunded"

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payment_attempts")
    provider = models.CharField(max_length=20, default="stripe", editable=False)
    idempotency_key_hash = models.CharField(max_length=64, unique=True, editable=False)
    provider_checkout_session_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True, editable=False
    )
    provider_payment_intent_id = models.CharField(
        max_length=255, blank=True, db_index=True, editable=False
    )
    checkout_url = models.URLField(max_length=1000, blank=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    currency = models.CharField(max_length=3, default="THB", editable=False)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CREATING)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_error_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0), name="payments_amount_non_negative"),
            models.UniqueConstraint(
                fields=("order",),
                condition=Q(status__in=("creating", "open")),
                name="payments_one_open_attempt_per_order",
            ),
        ]

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Payment attempts cannot be deleted.")


class WebhookEvent(models.Model):
    provider_event_id = models.CharField(max_length=255, unique=True, editable=False)
    event_type = models.CharField(max_length=120, db_index=True, editable=False)
    livemode = models.BooleanField(editable=False)
    processed_at = models.DateTimeField(null=True, blank=True, editable=False)
    outcome = models.CharField(max_length=120, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        raise ValidationError("Webhook event records cannot be deleted.")
