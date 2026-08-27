from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import NewsletterSubscription, PartnershipInquiry


@admin.action(description="Mark selected inquiries in progress")
def mark_in_progress(
    modeladmin: admin.ModelAdmin,  # type: ignore[type-arg]
    request: HttpRequest,
    queryset: QuerySet[PartnershipInquiry],
) -> None:
    queryset.update(status=PartnershipInquiry.Status.IN_PROGRESS)


@admin.action(description="Close selected inquiries")
def close_inquiries(
    modeladmin: admin.ModelAdmin,  # type: ignore[type-arg]
    request: HttpRequest,
    queryset: QuerySet[PartnershipInquiry],
) -> None:
    queryset.update(status=PartnershipInquiry.Status.CLOSED)


@admin.register(PartnershipInquiry)
class PartnershipInquiryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "company", "inquiry_type", "status", "assigned_to", "created_at")
    list_filter = ("status", "inquiry_type", "consent", "created_at")
    search_fields = ("name", "email", "company", "phone", "requirements")
    autocomplete_fields = ("assigned_to",)
    readonly_fields = ("consent", "consent_at", "created_at", "updated_at")
    list_select_related = ("assigned_to",)
    actions = (mark_in_progress, close_inquiries)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("email", "status", "consent_source", "consent_at", "updated_at")
    list_filter = ("status", "consent_source", "created_at")
    search_fields = ("email",)
    readonly_fields = ("email", "consent_source", "consent_at", "created_at", "updated_at")
