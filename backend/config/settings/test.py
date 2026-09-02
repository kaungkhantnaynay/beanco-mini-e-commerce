"""Fast, isolated test settings."""

from .base import *  # noqa: F403
from .base import MIDDLEWARE as BASE_MIDDLEWARE

DEBUG = False
SECRET_KEY = "test-only-secret-key"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CART_COOKIE_SECURE = True
MIDDLEWARE = [
    middleware
    for middleware in BASE_MIDDLEWARE
    if middleware != "whitenoise.middleware.WhiteNoiseMiddleware"
]
