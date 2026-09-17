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
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "REAL_ACCOUNT_REGISTRATION": False,
    "REAL_PERSONAL_DATA": False,
    "REAL_STUDENT_USE": False,
    "REAL_INSTRUCTOR_REGISTRATION": False,
    "REAL_MARKETPLACE_SEARCH": False,
    "REAL_WHATSAPP_CONTACT": False,
    "REAL_MARKETPLACE_ANALYTICS": False,
    "REAL_DOCUMENT_UPLOADS": False,
    "REAL_AUTOMATIC_PUBLICATION": False,
    "REAL_PAYMENTS": False,
    "REAL_PRO_BILLING": False,
    "ADMIN_MFA_REQUIRED": True,
    "MAPTILER_API_KEY": "production-key-present",
    "MEDIA_ROOT": "/app/private_documents",
}


@override_settings(**SECURE_SETTINGS)
def test_production_readiness_passes_with_all_real_capabilities_disabled():
    output = StringIO()

    call_command("production_readiness", stdout=output)

    assert "REAL_CAPABILITY_CONFIGURATION=PASS" in output.getvalue()
    assert "TECHNICAL_PRODUCTION_READINESS=PASS" in output.getvalue()
    assert "REAL_PRODUCTION_AUTHORIZATION=NOT_GRANTED" in output.getvalue()


def test_production_readiness_fails_if_capability_is_enabled_without_authorization():
    enabled_setting = "REAL_ACCOUNT_REGISTRATION"
    configured = {**SECURE_SETTINGS, enabled_setting: True}
    output = StringIO()

    with override_settings(**configured), pytest.raises(CommandError):
        call_command("production_readiness", stdout=output)

    assert "REAL_CAPABILITY_CONFIGURATION=FAIL" in output.getvalue()


@override_settings(
    **{
        **SECURE_SETTINGS,
        "REAL_PRODUCTION_AUTHORIZATION": "CONTROLLED_PILOT",
        "REAL_ACCOUNT_REGISTRATION": True,
        "REAL_PERSONAL_DATA": True,
        "REAL_STUDENT_USE": True,
        "REAL_INSTRUCTOR_REGISTRATION": True,
        "REAL_MARKETPLACE_SEARCH": True,
        "REAL_WHATSAPP_CONTACT": True,
        "REAL_MARKETPLACE_ANALYTICS": True,
    }
)
def test_production_readiness_accepts_only_explicit_pilot_capabilities():
    output = StringIO()

    call_command("production_readiness", stdout=output)

    result = output.getvalue()
    assert "REAL_PRODUCTION_AUTHORIZATION=CONTROLLED_PILOT" in result
    assert "REAL_ACCOUNT_REGISTRATION=ENABLED" in result
    assert "REAL_DOCUMENT_UPLOADS=BLOCKED" in result
    assert "REAL_AUTOMATIC_PUBLICATION=BLOCKED" in result
    assert "REAL_PAYMENTS=BLOCKED" in result
    assert "REAL_PRO_BILLING=BLOCKED" in result


@pytest.mark.parametrize(
    "forbidden",
    [
        "REAL_DOCUMENT_UPLOADS",
        "REAL_AUTOMATIC_PUBLICATION",
        "REAL_PAYMENTS",
        "REAL_PRO_BILLING",
    ],
)
def test_controlled_pilot_rejects_forbidden_capability(forbidden):
    configured = {
        **SECURE_SETTINGS,
        "REAL_PRODUCTION_AUTHORIZATION": "CONTROLLED_PILOT",
        forbidden: True,
    }
    with override_settings(**configured), pytest.raises(CommandError):
        call_command("production_readiness", stdout=StringIO())
