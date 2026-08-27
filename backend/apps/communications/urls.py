from django.urls import path

from .views import NewsletterSubscriptionCreateView, PartnershipInquiryCreateView

urlpatterns = [
    path("inquiries/", PartnershipInquiryCreateView.as_view(), name="inquiry-create"),
    path(
        "newsletter/subscriptions/",
        NewsletterSubscriptionCreateView.as_view(),
        name="newsletter-subscription-create",
    ),
]
