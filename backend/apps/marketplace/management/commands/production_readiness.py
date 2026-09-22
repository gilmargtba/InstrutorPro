from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.marketplace.capabilities import (
    CAPABILITIES,
    configuration_errors,
    enabled,
    instructor_registration_mode,
    professional_verification_mode,
)


class Command(BaseCommand):
    help = "Fail-closed technical production configuration check (not business/legal approval)."

    def handle(self, *args, **options):
        checks = {
            "APP_ENV": settings.APP_ENV == "PRODUCTION",
            "DEBUG": settings.DEBUG is False,
            "SECRET_KEY": len(settings.SECRET_KEY) >= 50
            and not settings.SECRET_KEY.startswith("unsafe-"),
            "ALLOWED_HOSTS": bool(settings.ALLOWED_HOSTS) and "*" not in settings.ALLOWED_HOSTS,
            "CSRF": bool(settings.CSRF_TRUSTED_ORIGINS)
            and all(
                origin.startswith("https://") and "*" not in origin
                for origin in settings.CSRF_TRUSTED_ORIGINS
            ),
            "CORS": not getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False),
            "HTTPS": settings.SECURE_SSL_REDIRECT
            and settings.SESSION_COOKIE_SECURE
            and settings.CSRF_COOKIE_SECURE,
            "SYNTHETIC": not settings.SYNTHETIC_MARKETPLACE_ENABLED
            and not settings.SYNTHETIC_DOCUMENT_UPLOAD_ENABLED,
            "REAL_CAPABILITY_CONFIGURATION": not configuration_errors(),
            "ADMIN_MFA": settings.ADMIN_MFA_REQUIRED,
            "MAPTILER": bool(settings.MAPTILER_API_KEY) or not enabled("REAL_MARKETPLACE_SEARCH"),
            "EMAIL_TRANSACTIONAL": settings.EMAIL_BACKEND
            != "django.core.mail.backends.console.EmailBackend"
            and bool(settings.EMAIL_HOST)
            and bool(settings.DEFAULT_FROM_EMAIL),
            "DATABASE": bool(settings.DATABASES["default"].get("NAME")),
            "PRIVATE_STORAGE": "private" in str(settings.MEDIA_ROOT).lower(),
        }
        for name, passed in checks.items():
            self.stdout.write(f"{name}={'PASS' if passed else 'FAIL'}")
        failures = [name for name, passed in checks.items() if not passed]
        if failures:
            raise CommandError("Technical production readiness failed: " + ", ".join(failures))
        self.stdout.write(self.style.SUCCESS("TECHNICAL_PRODUCTION_READINESS=PASS"))
        self.stdout.write(f"INSTRUCTOR_REGISTRATION_MODE={instructor_registration_mode()}")
        self.stdout.write(f"PROFESSIONAL_VERIFICATION_MODE={professional_verification_mode()}")
        self.stdout.write(f"REAL_PRODUCTION_AUTHORIZATION={settings.REAL_PRODUCTION_AUTHORIZATION}")
        for name in CAPABILITIES:
            self.stdout.write(f"{name}={'ENABLED' if enabled(name) else 'BLOCKED'}")
