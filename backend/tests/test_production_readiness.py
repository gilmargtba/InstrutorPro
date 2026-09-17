from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

SECURE_SETTINGS = {
    "APP_ENV": "PRODUCTION",
    "DEBUG": False,
    "SECRET_KEY": "s" * 64,
    "ALLOWED_HOSTS": ["instrutorprocnh.com.br"],
    "CSRF_TRUSTED_ORIGINS": ["https://instrutorprocnh.com.br"],
    "CORS_ALLOW_ALL_ORIGINS": False,
    "SECURE_SSL_REDIRECT": True,
    "SESSION_COOKIE_SECURE": True,
    "CSRF_COOKIE_SECURE": True,
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "SYNTHETIC_DOCUMENT_UPLOAD_ENABLED": False,
    "REAL_STUDENT_REGISTRATION_ENABLED": False,
    "REAL_INSTRUCTOR_REGISTRATION_ENABLED": False,
    "REAL_INSTRUCTOR_PUBLICATION_ENABLED": False,
    "REAL_STUDENT_DEMAND_ENABLED": False,
    "REAL_DOCUMENT_UPLOAD_ENABLED": False,
    "ADMIN_MFA_REQUIRED": True,
    "MAPTILER_API_KEY": "production-key-present",
    "MEDIA_ROOT": "/app/private_documents",
}


@override_settings(**SECURE_SETTINGS)
def test_production_readiness_passes_with_all_real_capabilities_disabled():
    output = StringIO()

    call_command("production_readiness", stdout=output)

    assert "REAL_CAPABILITIES_DISABLED=PASS" in output.getvalue()
    assert "TECHNICAL_PRODUCTION_READINESS=PASS" in output.getvalue()
    assert "REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED" in output.getvalue()


@pytest.mark.parametrize(
    "enabled_setting",
    [
        "REAL_STUDENT_REGISTRATION_ENABLED",
        "REAL_INSTRUCTOR_REGISTRATION_ENABLED",
        "REAL_INSTRUCTOR_PUBLICATION_ENABLED",
        "REAL_STUDENT_DEMAND_ENABLED",
        "REAL_DOCUMENT_UPLOAD_ENABLED",
    ],
)
def test_production_readiness_fails_if_any_real_capability_is_enabled(enabled_setting):
    configured = {**SECURE_SETTINGS, enabled_setting: True}
    output = StringIO()

    with override_settings(**configured), pytest.raises(CommandError):
        call_command("production_readiness", stdout=output)

    assert "REAL_CAPABILITIES_DISABLED=FAIL" in output.getvalue()
