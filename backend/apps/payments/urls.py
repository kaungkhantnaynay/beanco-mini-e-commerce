from django.urls import path

from .views import CheckoutSessionCreateView, StripeWebhookView

urlpatterns = [
    path(
        "orders/<uuid:public_id>/payment-session/",
        CheckoutSessionCreateView.as_view(),
        name="payment-session-create",
    ),
    path("payments/stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
