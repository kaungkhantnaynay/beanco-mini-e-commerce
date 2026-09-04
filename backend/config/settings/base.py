"""Shared Django settings. Environment-specific modules refine these defaults."""

from datetime import timedelta
from pathlib import Path

import environ
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="development-only-key-not-for-production")
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "apps.accounts",
    "apps.catalog",
    "apps.inventory",
    "apps.communications",
    "apps.carts",
    "apps.orders",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "config.middleware.RequestCorrelationMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    ),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DATA_UPLOAD_MAX_MEMORY_SIZE = env.int("DATA_UPLOAD_MAX_MEMORY_SIZE", default=2 * 1024 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = env.int("FILE_UPLOAD_MAX_MEMORY_SIZE", default=2 * 1024 * 1024)
PRODUCT_IMAGE_MAX_BYTES = env.int("PRODUCT_IMAGE_MAX_BYTES", default=10 * 1024 * 1024)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_PAGINATION_CLASS": "apps.api.pagination.BeanCoPageNumberPagination",
    "PAGE_SIZE": 12,
    "EXCEPTION_HANDLER": "apps.api.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {
        "inquiries": env("INQUIRY_THROTTLE_RATE", default="5/hour"),
        "newsletter": env("NEWSLETTER_THROTTLE_RATE", default="10/hour"),
        "carts": env("CART_THROTTLE_RATE", default="60/hour"),
        "checkout": env("CHECKOUT_THROTTLE_RATE", default="20/hour"),
        "orders": env("ORDER_THROTTLE_RATE", default="10/hour"),
        "registration": env("REGISTRATION_THROTTLE_RATE", default="5/hour"),
        "login": env("LOGIN_THROTTLE_RATE", default="10/minute"),
        "password_reset": env("PASSWORD_RESET_THROTTLE_RATE", default="5/hour"),
        "account_auth": env("ACCOUNT_AUTH_THROTTLE_RATE", default="20/hour"),
        "payments": env("PAYMENT_THROTTLE_RATE", default="20/hour"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "BeanCo API",
    "DESCRIPTION": "Versioned API for the BeanCo storefront.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "ENUM_NAME_OVERRIDES": {
        "PaymentAttemptStatusEnum": "apps.payments.models.PaymentAttempt.Status",
        "OrderStatusEnum": "apps.orders.models.Order.Status",
    },
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=["http://localhost:3000"])
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (*default_headers, "idempotency-key")
CORS_EXPOSE_HEADERS = ("X-Request-ID",)

SESSION_COOKIE_NAME = env("SESSION_COOKIE_NAME", default="beanco_sessionid")
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=not DEBUG)
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_NAME = env("CSRF_COOKIE_NAME", default="beanco_csrftoken")
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SAMESITE = "Lax"

CART_COOKIE_NAME = env("CART_COOKIE_NAME", default="beanco_cart")
CART_COOKIE_MAX_AGE = 30 * 24 * 60 * 60
CART_COOKIE_SECURE = env.bool("CART_COOKIE_SECURE", default=not DEBUG)

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
ACCOUNT_EMAIL_BACKEND = env(
    "ACCOUNT_EMAIL_BACKEND", default="django.core.mail.backends.locmem.EmailBackend"
)
PAYMENT_EMAIL_BACKEND = env(
    "PAYMENT_EMAIL_BACKEND", default="django.core.mail.backends.locmem.EmailBackend"
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="BeanCo <noreply@beanco.example>")
STAFF_NOTIFICATION_EMAIL = env("STAFF_NOTIFICATION_EMAIL", default="partnerships@beanco.example")
ACCOUNT_EMAIL_VERIFICATION_URL = env(
    "ACCOUNT_EMAIL_VERIFICATION_URL", default="http://localhost:3000/account/verify-email"
)
ACCOUNT_PASSWORD_RESET_URL = env(
    "ACCOUNT_PASSWORD_RESET_URL", default="http://localhost:3000/account/reset-password"
)

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_CHECKOUT_TTL = timedelta(minutes=30)
STRIPE_SUCCESS_URL = env(
    "STRIPE_SUCCESS_URL",
    default="http://localhost:3000/orders/{order_id}?payment=return&session_id={CHECKOUT_SESSION_ID}",
)
STRIPE_CANCEL_URL = env(
    "STRIPE_CANCEL_URL", default="http://localhost:3000/orders/{order_id}?payment=cancelled"
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "config.logging.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},
}
