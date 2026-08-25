import os

from .base import *  # noqa: F403

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

_https_enabled = os.getenv("DJANGO_HTTPS_ENABLED", "false").lower() == "true"
SESSION_COOKIE_SECURE = _https_enabled
CSRF_COOKIE_SECURE = _https_enabled
SECURE_SSL_REDIRECT = _https_enabled
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = False
