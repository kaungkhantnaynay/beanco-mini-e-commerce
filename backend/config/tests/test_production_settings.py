import os
import subprocess
import sys
from pathlib import Path


def test_production_s3_settings_support_supabase_storage() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    environment = {
        **os.environ,
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "DJANGO_SECRET_KEY": "ci-only-secret-key-with-more-than-fifty-characters-123456789",
        "DATABASE_URL": "sqlite:///:memory:",
        "DJANGO_ALLOWED_HOSTS": "api.example.test",
        "FRONTEND_ORIGIN": "https://shop.example.test",
        "AWS_S3_ENDPOINT_URL": ("https://project-ref.storage.supabase.co/storage/v1/s3"),
        "AWS_ACCESS_KEY_ID": "test-access-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret-key",
        "AWS_STORAGE_BUCKET_NAME": "beanco-preview-media",
        "AWS_S3_REGION_NAME": "ap-southeast-1",
        "AWS_S3_ADDRESSING_STYLE": "path",
        "AWS_S3_SIGNATURE_VERSION": "s3v4",
        "AWS_QUERYSTRING_AUTH": "true",
        "AWS_QUERYSTRING_EXPIRE": "900",
        "EMAIL_HOST_PASSWORD": "test-email-password",
        "DEFAULT_FROM_EMAIL": "BeanCo <noreply@example.test>",
        "STAFF_NOTIFICATION_EMAIL": "alerts@example.test",
        "STRIPE_SECRET_KEY": "test-stripe-secret",
        "STRIPE_WEBHOOK_SECRET": "test-webhook-secret",
        "STRIPE_SUCCESS_URL": "https://shop.example.test/payment/success",
        "STRIPE_CANCEL_URL": "https://shop.example.test/payment/cancelled",
    }
    assertions = """
from django.conf import settings

assert settings.AWS_S3_ENDPOINT_URL == (
    "https://project-ref.storage.supabase.co/storage/v1/s3"
)
assert settings.AWS_S3_REGION_NAME == "ap-southeast-1"
assert settings.AWS_S3_ADDRESSING_STYLE == "path"
assert settings.AWS_S3_SIGNATURE_VERSION == "s3v4"
assert settings.AWS_QUERYSTRING_AUTH is True
assert settings.AWS_QUERYSTRING_EXPIRE == 900
assert settings.AWS_DEFAULT_ACL is None
assert settings.AWS_S3_FILE_OVERWRITE is False
"""

    subprocess.run(  # noqa: S603
        [sys.executable, "-c", assertions],
        cwd=backend_dir,
        env=environment,
        check=True,
    )
