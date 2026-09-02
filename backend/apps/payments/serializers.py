from rest_framework import serializers

from .models import PaymentAttempt


class CheckoutSessionSerializer(serializers.ModelSerializer[PaymentAttempt]):
    class Meta:
        model = PaymentAttempt
        fields = ("public_id", "status", "checkout_url", "amount", "currency", "expires_at")
        read_only_fields = fields


class WebhookResponseSerializer(serializers.Serializer[dict[str, object]]):
    received = serializers.BooleanField()
    duplicate = serializers.BooleanField()
