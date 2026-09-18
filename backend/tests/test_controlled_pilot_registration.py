from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.gis.geos import Point
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.discovery.selectors import search_published_instructors
from apps.marketplace.models import (
    DataMode,
    InstructorContactChannel,
    InstructorOffer,
    MarketplaceEvent,
    StudentProfile,
)
from apps.people.models import RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord
from apps.territories.models import Country, FederativeUnit

PILOT = {
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "REAL_PRODUCTION_AUTHORIZATION": "CONTROLLED_PILOT",
    "REAL_ACCOUNT_REGISTRATION": True,
    "REAL_PERSONAL_DATA": True,
    "REAL_STUDENT_USE": True,
    "REAL_INSTRUCTOR_REGISTRATION": True,
}


def payload(role="STUDENT"):
    return {
        "role": role,
        "username": f"real-{role.lower()}",
        "email": f"real-{role.lower()}@example.com",
        "password": "safe-test-password",
        "password_confirmation": "safe-test-password",
        "display_name": "Pessoa Piloto",
        "birth_date": "1990-01-01",
        "city": "Porto Alegre",
        "uf": "RS",
        "terms_version": "1.0",
        "privacy_version": "2026-09-16",
        "terms_accepted": True,
        "privacy_acknowledged": True,
    }


@pytest.fixture(autouse=True)
def territory(db):
    country = Country.objects.create(code="BR", name="Brasil")
    FederativeUnit.objects.create(
        country=country, code="RS", name="Rio Grande do Sul", ibge_code="43"
    )


@pytest.mark.django_db
@override_settings(**PILOT)
def test_real_student_registration_is_atomic_and_records_exact_acceptance():
    response = APIClient().post("/api/v1/marketplace/accounts/register/", payload(), format="json")

    assert response.status_code == 201
    account = Account.objects.get(email="real-student@example.com")
    assert RoleAssignment.objects.get(person=account.person).role == "STUDENT"
    assert StudentProfile.objects.get(person=account.person).data_mode == DataMode.REAL
    acceptance = LegalAcceptanceRecord.objects.get(account=account)
    assert acceptance.terms_document.audience == "STUDENT"
    assert acceptance.terms_document.version == "1.0"
    assert acceptance.privacy_notice.version == "2026-09-16"
    assert acceptance.accepted_at is not None


@pytest.mark.django_db
@override_settings(**PILOT)
def test_real_instructor_registration_is_unpublished_and_uses_instructor_terms():
    response = APIClient().post(
        "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
    )

    assert response.status_code == 201
    account = Account.objects.get(email="real-instructor@example.com")
    profile = InstructorProfile.objects.get(person=account.person)
    assert not profile.is_demo
    assert profile.publication_status == "UNPUBLISHED"
    assert profile.verification_status == "NOT_STARTED"
    acceptance = LegalAcceptanceRecord.objects.get(account=account)
    assert acceptance.terms_document.audience == "INSTRUCTOR"


@pytest.mark.django_db
@override_settings(**PILOT)
def test_real_instructor_can_save_non_documental_onboarding_without_self_publication():
    client = APIClient()
    assert client.post(
        "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
    ).status_code == 201

    response = client.patch(
        "/api/v1/account/me/",
        {
            "bio": "Atendimento categoria B.",
            "transmission_options": ["MANUAL"],
            "whatsapp": "+5551999990001",
            "price_amount": "95.00",
            "duration_minutes": 60,
            "vehicle": {
                "category": "B",
                "make": "Marca",
                "model": "Modelo",
                "year": 2024,
                "transmission": "MANUAL",
            },
        },
        format="json",
    )

    assert response.status_code == 200
    profile = InstructorProfile.objects.get(person__account__email="real-instructor@example.com")
    assert profile.offers.get().data_mode == DataMode.REAL
    assert profile.vehicle.data_mode == DataMode.REAL
    assert profile.profile_status == "DRAFT"
    assert profile.verification_status == "NOT_STARTED"
    assert profile.publication_status == "UNPUBLISHED"
    assert not profile.documents.exists()


@pytest.mark.django_db
@override_settings(**PILOT)
@pytest.mark.parametrize(
    "field,value",
    [
        ("terms_accepted", False),
        ("privacy_acknowledged", False),
        ("terms_version", "0.9"),
        ("privacy_version", "0.9"),
    ],
)
def test_real_registration_fails_closed_for_missing_or_invalid_legal_evidence(field, value):
    data = payload()
    data[field] = value

    response = APIClient().post(
        "/api/v1/marketplace/accounts/register/", data, format="json"
    )

    assert response.status_code == 400
    assert not Account.objects.filter(email=data["email"]).exists()


@pytest.mark.django_db
@override_settings(**PILOT)
def test_acceptance_failure_rolls_back_account_person_and_role():
    with patch(
        "apps.marketplace.api.LegalAcceptanceRecord.objects.create",
        side_effect=RuntimeError("acceptance persistence failed"),
    ), pytest.raises(RuntimeError):
        APIClient().post("/api/v1/marketplace/accounts/register/", payload(), format="json")

    assert not Account.objects.filter(email="real-student@example.com").exists()
    assert not RoleAssignment.objects.exists()


@pytest.mark.django_db
def test_real_registration_is_blocked_without_controlled_pilot_capabilities():
    response = APIClient().post("/api/v1/marketplace/accounts/register/", payload(), format="json")

    assert response.status_code == 403
    assert not Account.objects.filter(email="real-student@example.com").exists()


@pytest.mark.django_db
@override_settings(
    SYNTHETIC_MARKETPLACE_ENABLED=False,
    REAL_PRODUCTION_AUTHORIZATION="CONTROLLED_PILOT",
    REAL_MARKETPLACE_SEARCH=True,
)
def test_real_selector_excludes_synthetic_and_requires_approved_real_offer():
    synthetic = _published_profile("selector-synthetic", is_demo=True, data_mode=DataMode.SYNTHETIC)
    real = _published_profile("selector-real", is_demo=False, data_mode=DataMode.REAL)
    pending = _published_profile(
        "selector-pending",
        is_demo=False,
        data_mode=DataMode.REAL,
        publication_status="UNPUBLISHED",
    )

    results = list(
        search_published_instructors(
            latitude=-30.0346, longitude=-51.2177, radius_km=10, category="B"
        )
    )

    assert [profile.id for profile in results] == [real.id]
    assert synthetic.id not in [profile.id for profile in results]
    assert pending.id not in [profile.id for profile in results]


@pytest.mark.django_db
@override_settings(
    SYNTHETIC_MARKETPLACE_ENABLED=False,
    REAL_PRODUCTION_AUTHORIZATION="CONTROLLED_PILOT",
    REAL_MARKETPLACE_SEARCH=True,
    REAL_WHATSAPP_CONTACT=True,
    REAL_MARKETPLACE_ANALYTICS=True,
)
def test_real_whatsapp_records_minimized_deduplicated_analytics():
    profile = _published_profile("real-contact", is_demo=False, data_mode=DataMode.REAL)
    InstructorContactChannel.objects.create(
        instructor=profile,
        whatsapp_e164="+5551999990001",
        data_mode=DataMode.REAL,
    )
    client = APIClient()
    url = f"/api/v1/instructors/{profile.id}/whatsapp-contact/"

    first = client.post(url, {"category": "B", "source": "public-profile"}, format="json")
    second = client.post(url, {"category": "B", "source": "public-profile"}, format="json")

    assert first.status_code == 200
    assert first.json()["unique_contact"] is True
    assert second.json()["unique_contact"] is False
    assert "whatsapp_e164" not in first.json()
    event = MarketplaceEvent.objects.get(
        event_type=MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED,
        instructor=profile,
    )
    assert event.data_mode == DataMode.REAL
    assert "Olá" not in str(event.__dict__)
    assert "+5551999990001" not in str(event.__dict__)


def _published_profile(username, *, is_demo, data_mode, publication_status="APPROVED"):
    account = Account.objects.create_user(
        username=username, email=f"{username}@example.com", password="test-password"
    )
    person = account.person if hasattr(account, "person") else None
    if person is None:
        from apps.people.models import Person

        person = Person.objects.create(account=account)
    RoleAssignment.objects.create(person=person, role="INSTRUCTOR", grant_reason="TEST")
    profile = InstructorProfile.objects.create(
        person=person,
        display_name=username,
        categories=["B"],
        transmission_options=["MANUAL"],
        profile_status="APPROVED",
        verification_status="VERIFIED",
        verified_until=timezone.now() + timedelta(days=30),
        publication_status=publication_status,
        is_demo=is_demo,
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.2177, -30.0346, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    InstructorOffer.objects.create(
        instructor=profile,
        category="B",
        price_amount="90.00",
        duration_minutes=60,
        data_mode=data_mode,
    )
    return profile
