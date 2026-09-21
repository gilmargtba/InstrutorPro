import re

import pytest
from django.core import mail
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.marketplace.capabilities import enabled
from apps.marketplace.models import InstructorContactChannel, InstructorOffer, InstructorVehicle
from apps.people.models import Person, RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord

PRODUCTION_REGISTRATION = {
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "INSTRUCTOR_REGISTRATION_MODE": "PRODUCTION",
    "REAL_ACCOUNT_REGISTRATION": True,
    "REAL_PERSONAL_DATA": True,
    "REAL_INSTRUCTOR_REGISTRATION": True,
    "REAL_STUDENT_USE": False,
    "REAL_MARKETPLACE_SEARCH": False,
    "REAL_DOCUMENT_UPLOADS": False,
    "REAL_AUTOMATIC_PUBLICATION": False,
    "REAL_PAYMENTS": False,
    "REAL_PRO_BILLING": False,
}


def signup_payload(**overrides):
    data = {
        "role": "INSTRUCTOR",
        "username": "instrutora-nacional",
        "email": "instrutora.nacional@example.com",
        "password": "senha-segura-123",
        "password_confirmation": "senha-segura-123",
        "display_name": "Instrutora Nacional",
        "birth_date": "1990-01-01",
        "terms_version": "1.0",
        "privacy_version": "2026-09-16",
        "terms_accepted": True,
        "privacy_acknowledged": True,
    }
    data.update(overrides)
    return data


@pytest.fixture(autouse=True)
def national_territories(db):
    call_command("seed_territories", verbosity=0)


@pytest.mark.django_db
@override_settings(**PRODUCTION_REGISTRATION)
def test_instructor_production_e2e_without_regulatory_readiness_or_geocoder():
    client = APIClient()
    response = client.post(
        "/api/v1/marketplace/accounts/register/", signup_payload(), format="json"
    )
    assert response.status_code == 201

    account = Account.objects.get(email="instrutora.nacional@example.com")
    assert account.lifecycle_status == Account.LifecycleStatus.ACTIVE
    assert Person.objects.filter(account=account).exists()
    assert RoleAssignment.objects.get(person=account.person).role == "INSTRUCTOR"
    profile = InstructorProfile.objects.get(person=account.person)
    assert profile.verification_status == InstructorProfile.VerificationStatus.NOT_STARTED
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    acceptance = LegalAcceptanceRecord.objects.get(account=account)
    assert len(acceptance.terms_document.content_sha256) == 64
    assert acceptance.accepted_at is not None

    client.post("/api/v1/marketplace/session/logout/")
    login = client.post(
        "/api/v1/marketplace/session/login/",
        {"email": account.email, "password": "senha-segura-123"},
        format="json",
    )
    assert login.status_code == 200
    assert login.json()["roles"] == ["INSTRUCTOR"]

    onboarding = client.patch(
        "/api/v1/account/me/",
        {
            "instructor_display_name": "Instrutora Nacional",
            "bio": "Atendimento profissional em categorias A e C.",
            "categories": ["A", "C"],
            "transmission_options": ["MANUAL", "AUTOMATIC"],
            "whatsapp": "+5568999990001",
            "price_amount": "120.00",
            "duration_minutes": 60,
            "instructor_city": "Rio Branco",
            "instructor_uf": "AC",
            "service_radius_km": 20,
            "service_location_authorized": False,
            "vehicle": {
                "category": "A",
                "make": "Marca",
                "model": "Modelo",
                "year": 2025,
                "transmission": "MANUAL",
            },
        },
        format="json",
    )
    assert onboarding.status_code == 200
    profile.refresh_from_db()
    area = InstructorServiceArea.objects.get(profile=profile)
    assert (area.city, area.uf, area.public_service_location) == ("Rio Branco", "AC", None)
    assert not area.location_authorized
    assert InstructorContactChannel.objects.filter(instructor=profile).exists()
    assert InstructorOffer.objects.filter(instructor=profile, category="A").exists()
    assert InstructorVehicle.objects.filter(instructor=profile, category="A").exists()
    assert profile.verification_status == "NOT_STARTED"
    assert profile.publication_status == "UNPUBLISHED"
    assert not enabled("REAL_DOCUMENT_UPLOADS")
    assert not enabled("REAL_AUTOMATIC_PUBLICATION")
    assert not enabled("REAL_PAYMENTS")
    assert not enabled("REAL_PRO_BILLING")


@pytest.mark.django_db
@override_settings(**PRODUCTION_REGISTRATION)
@pytest.mark.parametrize(
    ("overrides", "error_field"),
    [
        ({"password": "curta", "password_confirmation": "curta"}, "password"),
        ({"birth_date": "2012-01-01"}, "birth_date"),
        ({"terms_accepted": False}, "non_field_errors"),
        ({"privacy_acknowledged": False}, "non_field_errors"),
    ],
)
def test_production_signup_rejects_invalid_mandatory_data(overrides, error_field):
    response = APIClient().post(
        "/api/v1/marketplace/accounts/register/",
        signup_payload(**overrides),
        format="json",
    )
    assert response.status_code == 400
    assert error_field in response.json()["error"]["details"]
    assert not Account.objects.filter(email="instrutora.nacional@example.com").exists()


@pytest.mark.django_db
@override_settings(**PRODUCTION_REGISTRATION)
def test_production_signup_handles_duplicate_email_without_partial_account():
    first = APIClient().post(
        "/api/v1/marketplace/accounts/register/", signup_payload(), format="json"
    )
    assert first.status_code == 201

    duplicate = APIClient().post(
        "/api/v1/marketplace/accounts/register/",
        signup_payload(username="outro-usuario"),
        format="json",
    )
    assert duplicate.status_code == 400
    assert Account.objects.filter(email="instrutora.nacional@example.com").count() == 1
    assert not Account.objects.filter(username="outro-usuario").exists()


@pytest.mark.django_db
@override_settings(**PRODUCTION_REGISTRATION)
def test_production_onboarding_rejects_invalid_uf_and_vehicle_values():
    client = APIClient()
    assert (
        client.post(
            "/api/v1/marketplace/accounts/register/", signup_payload(), format="json"
        ).status_code
        == 201
    )

    invalid_uf = client.patch(
        "/api/v1/account/me/",
        {"instructor_city": "Cidade", "instructor_uf": "XX"},
        format="json",
    )
    assert invalid_uf.status_code == 400
    assert "instructor_uf" in invalid_uf.json()["error"]["details"]

    invalid_vehicle = client.patch(
        "/api/v1/account/me/",
        {
            "vehicle": {
                "category": "Z",
                "make": "Marca",
                "model": "Modelo",
                "year": 2025,
                "transmission": "UNKNOWN",
            }
        },
        format="json",
    )
    assert invalid_vehicle.status_code == 400
    assert "vehicle" in invalid_vehicle.json()["error"]["details"]


@pytest.mark.django_db
@override_settings(
    **PRODUCTION_REGISTRATION,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.test",
    FRONTEND_PUBLIC_URL="https://instrutorprocnh.example.test",
)
def test_password_reset_is_generic_secure_and_invalidates_token():
    account = Account.objects.create_user(
        username="recovery", email="recovery@example.com", password="senha-antiga-123"
    )
    response = APIClient().post(
        "/api/v1/marketplace/password-reset/request/",
        {"email": account.email},
        format="json",
    )
    assert response.status_code == 202
    assert len(mail.outbox) == 1
    match = re.search(r"uid=([^&\s]+)&token=([^\s]+)", mail.outbox[0].body)
    assert match
    uid, token = match.groups()

    confirm = APIClient().post(
        "/api/v1/marketplace/password-reset/confirm/",
        {
            "uid": uid,
            "token": token,
            "password": "senha-nova-segura-123",
            "password_confirmation": "senha-nova-segura-123",
        },
        format="json",
    )
    assert confirm.status_code == 200
    account.refresh_from_db()
    assert account.check_password("senha-nova-segura-123")
    assert (
        APIClient()
        .post(
            "/api/v1/marketplace/password-reset/confirm/",
            {
                "uid": uid,
                "token": token,
                "password": "outra-senha-segura-123",
                "password_confirmation": "outra-senha-segura-123",
            },
            format="json",
        )
        .status_code
        == 400
    )


@pytest.mark.django_db
@override_settings(**PRODUCTION_REGISTRATION)
def test_password_reset_does_not_enumerate_unknown_email():
    response = APIClient().post(
        "/api/v1/marketplace/password-reset/request/",
        {"email": "unknown@example.com"},
        format="json",
    )
    assert response.status_code == 202


@pytest.mark.django_db
@override_settings(
    **PRODUCTION_REGISTRATION,
    EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
)
def test_password_reset_fails_closed_without_transactional_email():
    response = APIClient().post(
        "/api/v1/marketplace/password-reset/request/",
        {"email": "unknown@example.com"},
        format="json",
    )
    assert response.status_code == 503
