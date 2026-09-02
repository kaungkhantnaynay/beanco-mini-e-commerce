"""PostgreSQL-backed test settings for transaction and concurrency verification."""

from .base import env
from .test import *  # noqa: F403

DATABASES = {"default": env.db("DATABASE_URL")}
