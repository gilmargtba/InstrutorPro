import os

os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-secret-key")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost")

from .base import *  # noqa: E402,F403

APP_ENV = "TEST"
CELERY_TASK_ALWAYS_EAGER = True
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
SYNTHETIC_MARKETPLACE_ENABLED = True
DEMAND_MAP_MIN_AGGREGATION_COUNT = 3
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "registration": "10000/minute",
    "login": "10000/minute",
    "password_reset": "10000/minute",
}
