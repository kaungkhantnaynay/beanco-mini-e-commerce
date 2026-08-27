from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from .models import NewsletterSubscription, PartnershipInquiry


class PartnershipInquirySerializer(serializers.ModelSerializer[PartnershipInquiry]):
    website = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = PartnershipInquiry
        fields = (
            "name",
            "email",
            "phone",
            "company",
            "inquiry_type",
            "requirements",
            "consent",
            "website",
            "created_at",
        )
        read_only_fields = ("created_at",)

    def validate_website(self, value: str) -> str:
        if value:
            raise serializers.ValidationError("Unable to accept this submission.")
        return value

    def validate_consent(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError("Consent is required.")
        return value

    def validate_requirements(self, value: str) -> str:
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError("Please provide at least 20 characters.")
        return value

    def create(self, validated_data: dict[str, object]) -> PartnershipInquiry:
        validated_data.pop("website", None)
        validated_data["consent_at"] = timezone.now()
        return PartnershipInquiry.objects.create(**validated_data)


class NewsletterSubscriptionSerializer(serializers.Serializer[NewsletterSubscription]):
    email = serializers.EmailField()
    consent = serializers.BooleanField(write_only=True)
    consent_source = serializers.CharField(max_length=120, default="storefront_footer")
    website = serializers.CharField(write_only=True, required=False, allow_blank=True)
    should_notify = False

    def validate_consent(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError("Consent is required.")
        return value

    def validate_website(self, value: str) -> str:
        if value:
            raise serializers.ValidationError("Unable to accept this submission.")
        return value

    def create(self, validated_data: dict[str, object]) -> NewsletterSubscription:
        email = str(validated_data["email"]).strip().lower()
        consent_source = str(validated_data["consent_source"])
        now = timezone.now()
        try:
            with transaction.atomic():
                subscription = (
                    NewsletterSubscription.objects.select_for_update()
                    .filter(email__iexact=email)
                    .first()
                )
                self.should_notify = (
                    subscription is None
                    or subscription.status != NewsletterSubscription.Status.SUBSCRIBED
                )
                if subscription is None:
                    subscription = NewsletterSubscription.objects.create(
                        email=email,
                        status=NewsletterSubscription.Status.SUBSCRIBED,
                        consent_source=consent_source,
                        consent_at=now,
                    )
                else:
                    subscription.email = email
                    subscription.status = NewsletterSubscription.Status.SUBSCRIBED
                    subscription.consent_source = consent_source
                    subscription.consent_at = now
                    subscription.save(
                        update_fields=(
                            "email",
                            "status",
                            "consent_source",
                            "consent_at",
                            "updated_at",
                        )
                    )
        except IntegrityError:
            subscription = NewsletterSubscription.objects.get(email__iexact=email)
            self.should_notify = False
        return subscription


class SubmissionResponseSerializer(serializers.Serializer[dict[str, str]]):
    detail = serializers.CharField()
