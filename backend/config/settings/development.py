import os

os.environ.setdefault("DJANGO_SECRET_KEY", "unsafe-development-key-change-me")

from .base import *  # noqa: E402,F403

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"
