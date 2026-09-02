from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import User
from .tokens import email_verification_token


def _uid(user: User) -> str:
    return urlsafe_base64_encode(force_bytes(user.pk))


def _send_account_email(*, subject: str, body: str, recipient: str) -> None:
    connection = get_connection(settings.ACCOUNT_EMAIL_BACKEND)
    EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
        connection=connection,
    ).send(fail_silently=False)


def send_verification_email(user: User) -> None:
    query = urlencode({"uid": _uid(user), "token": email_verification_token.make_token(user)})
    url = f"{settings.ACCOUNT_EMAIL_VERIFICATION_URL}?{query}"
    _send_account_email(
        subject="Verify your BeanCo email",
        body=(
            f"Verify your BeanCo account using this link:\n\n{url}\n\n"
            "If you did not register, ignore this email."
        ),
        recipient=user.email,
    )


def send_password_reset_email(user: User) -> None:
    query = urlencode({"uid": _uid(user), "token": default_token_generator.make_token(user)})
    url = f"{settings.ACCOUNT_PASSWORD_RESET_URL}?{query}"
    _send_account_email(
        subject="Reset your BeanCo password",
        body=(
            f"Reset your BeanCo password using this link:\n\n{url}\n\n"
            "If you did not request this, ignore this email."
        ),
        recipient=user.email,
    )
