import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost")

from .base import *  # noqa: E402,F403

CELERY_TASK_ALWAYS_EAGER = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SYNTHETIC_MARKETPLACE_ENABLED = True
DEMAND_MAP_MIN_AGGREGATION_COUNT = 3
