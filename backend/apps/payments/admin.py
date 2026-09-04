from django.contrib import admin

from .models import PaymentAttempt, WebhookEvent


class ReadOnlyPaymentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    def has_add_permission(self, request: object) -> bool:
        return False

    def has_change_permission(self, request: object, obj: object | None = None) -> bool:
        return False

    def has_delete_permission(self, request: object, obj: object | None = None) -> bool:
        return False


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(ReadOnlyPaymentAdmin):
    list_display = (
        "public_id",
        "order",
        "status",
        "amount",
        "currency",
        "refunded_at",
        "created_at",
    )
    list_filter = ("status", "currency")
    search_fields = ("public_id", "order__public_id", "provider_checkout_session_id")
    exclude = ("checkout_url", "idempotency_key_hash")


@admin.register(WebhookEvent)
class WebhookEventAdmin(ReadOnlyPaymentAdmin):
    list_display = ("provider_event_id", "event_type", "livemode", "outcome", "processed_at")
    list_filter = ("event_type", "livemode", "outcome")
    search_fields = ("provider_event_id",)
