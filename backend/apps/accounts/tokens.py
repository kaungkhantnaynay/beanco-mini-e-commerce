from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .models import User


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "beanco.accounts.EmailVerificationTokenGenerator"

    def _make_hash_value(self, user: User, timestamp: int) -> str:
        return "|".join(
            (
                str(user.pk),
                user.password,
                user.email,
                str(user.is_active),
                str(user.email_verified_at),
                str(timestamp),
            )
        )


email_verification_token = EmailVerificationTokenGenerator()
