from django.urls import path

from .views import CheckoutSessionCreateView, CustomerOrderCancellationView, StripeWebhookView

urlpatterns = [
    path(
        "orders/<uuid:public_id>/payment-session/",
        CheckoutSessionCreateView.as_view(),
        name="payment-session-create",
    ),
    path("payments/stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path(
        "account/orders/<uuid:public_id>/cancel/",
        CustomerOrderCancellationView.as_view(),
        name="account-order-cancel",
    ),
]
