# ruff: noqa: F405
import os

os.environ.setdefault("APP_ENV", "PRODUCTION")

from .base import *  # noqa: E402,F403,F405

DEBUG = False

if len(SECRET_KEY) < 50 or SECRET_KEY.startswith("unsafe-"):
    raise RuntimeError("PRODUCTION requires a strong DJANGO_SECRET_KEY")
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise RuntimeError("PRODUCTION requires explicit DJANGO_ALLOWED_HOSTS")
if not CSRF_TRUSTED_ORIGINS or any("*" in origin for origin in CSRF_TRUSTED_ORIGINS):
    raise RuntimeError("PRODUCTION requires explicit HTTPS CSRF origins")
if any(not origin.startswith("https://") for origin in CSRF_TRUSTED_ORIGINS):
    raise RuntimeError("PRODUCTION CSRF origins must use HTTPS")
if not MAPTILER_API_KEY:
    raise RuntimeError("PRODUCTION requires its own MAPTILER_API_KEY")
if not ADMIN_MFA_REQUIRED:
    raise RuntimeError("PRODUCTION requires admin MFA")
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("PRODUCTION requires DATABASE_URL")
if not os.getenv("REDIS_URL"):
    raise RuntimeError("PRODUCTION requires REDIS_URL")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
SESSION_COOKIE_AGE = int(os.getenv("DJANGO_ADMIN_SESSION_AGE", "1800"))
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SYNTHETIC_MARKETPLACE_ENABLED = False
SYNTHETIC_DOCUMENT_UPLOAD_ENABLED = False
