import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import NewsletterSubscription, PartnershipInquiry

logger = logging.getLogger(__name__)


def send_inquiry_notifications(inquiry: PartnershipInquiry) -> None:
    try:
        send_mail(
            subject=f"New BeanCo {inquiry.get_inquiry_type_display()} inquiry",
            message=(
                f"A new partnership inquiry was submitted by {inquiry.name} "
                f"({inquiry.email}). Review it in Django Admin."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.STAFF_NOTIFICATION_EMAIL],
        )
        send_mail(
            subject="We received your BeanCo inquiry",
            message=(
                f"Hello {inquiry.name},\n\n"
                "Thank you for contacting BeanCo. Our team will review your requirements."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
        )
    except Exception:
        logger.exception("inquiry_notification_failed", extra={"inquiry_id": inquiry.pk})


def send_subscription_confirmation(subscription: NewsletterSubscription) -> None:
    try:
        send_mail(
            subject="Welcome to BeanCo updates",
            message="You are subscribed to BeanCo updates.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscription.email],
        )
    except Exception:
        logger.exception(
            "newsletter_notification_failed", extra={"subscription_id": subscription.pk}
        )
