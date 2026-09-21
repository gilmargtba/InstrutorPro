from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.discovery.selectors import search_published_instructors
from apps.marketplace.capabilities import enabled
from apps.marketplace.documents import DocumentValidationError, inspect_document
from apps.marketplace.models import (
    DataMode,
    InstructorContactChannel,
    InstructorOffer,
    MarketplaceEvent,
    StudentProfile,
)
from apps.people.models import RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord
from apps.territories.models import FederativeUnit, RegulatoryReadiness
from apps.territories.policies import (
    INSTRUCTOR_PROVIDER_TYPE,
    INSTRUCTOR_PUBLICATION_CAPABILITY,
)

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
    call_command("seed_territories", verbosity=0)
    RegulatoryReadiness.objects.create(
        federative_unit=FederativeUnit.objects.get(code="RS"),
        provider_type=INSTRUCTOR_PROVIDER_TYPE,
        capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        status=RegulatoryReadiness.Status.APPROVED,
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
@override_settings(
    SYNTHETIC_MARKETPLACE_ENABLED=False,
    SYNTHETIC_DOCUMENT_UPLOAD_ENABLED=False,
    REAL_PRODUCTION_AUTHORIZATION="CONTROLLED_PILOT",
    REAL_ACCOUNT_REGISTRATION=True,
    REAL_PERSONAL_DATA=True,
    REAL_STUDENT_USE=False,
    REAL_INSTRUCTOR_REGISTRATION=True,
    REAL_DOCUMENT_UPLOADS=False,
    REAL_AUTOMATIC_PUBLICATION=False,
)
def test_instructor_pilot_registration_does_not_enable_student_documents_or_publication():
    response = APIClient().post(
        "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
    )

    assert response.status_code == 201
    profile = InstructorProfile.objects.get(person__account__email="real-instructor@example.com")
    assert profile.verification_status == "NOT_STARTED"
    assert profile.publication_status == "UNPUBLISHED"
    assert not enabled("REAL_DOCUMENT_UPLOADS")
    assert not enabled("REAL_AUTOMATIC_PUBLICATION")
    with pytest.raises(DocumentValidationError, match="Upload real permanece desabilitado"):
        inspect_document(
            SimpleUploadedFile("credential.pdf", b"%PDF-1.7", content_type="application/pdf"),
            data_mode=DataMode.REAL,
        )


@pytest.mark.django_db
@override_settings(**PILOT)
def test_real_instructor_can_save_non_documental_onboarding_without_self_publication():
    client = APIClient()
    assert (
        client.post(
            "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
        ).status_code
        == 201
    )

    response = client.patch(
        "/api/v1/account/me/",
        {
            "bio": "Atendimento categoria B.",
            "transmission_options": ["MANUAL"],
            "whatsapp": "+5551999990001",
            "price_amount": "95.00",
            "duration_minutes": 60,
            "instructor_city": "Porto Alegre",
            "instructor_uf": "RS",
            "service_latitude": -30.0346,
            "service_longitude": -51.2177,
            "service_radius_km": 10,
            "service_location_authorized": True,
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
    assert profile.service_area.private_location is None
    assert profile.service_area.location_authorized is True
    assert profile.profile_status == "DRAFT"
    assert profile.verification_status == "NOT_STARTED"
    assert profile.publication_status == "UNPUBLISHED"
    assert not profile.documents.exists()


@pytest.mark.django_db
@override_settings(**PILOT)
@pytest.mark.parametrize(
    ("city", "uf", "latitude", "longitude"),
    [
        ("Porto Alegre", "RS", -30.0346, -51.2177),
        ("São Paulo", "SP", -23.5505, -46.6333),
        ("Rio de Janeiro", "RJ", -22.9068, -43.1729),
        ("Goiânia", "GO", -16.6869, -49.2648),
        ("Florianópolis", "SC", -27.5949, -48.5482),
        ("Vitória", "ES", -20.3155, -40.3128),
        ("Manaus", "AM", -3.1190, -60.0217),
    ],
)
def test_real_instructor_onboarding_accepts_representative_national_service_areas(
    city, uf, latitude, longitude
):
    client = APIClient()
    assert (
        client.post(
            "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
        ).status_code
        == 201
    )

    response = client.patch(
        "/api/v1/account/me/",
        {
            "instructor_city": city,
            "instructor_uf": uf,
            "service_latitude": latitude,
            "service_longitude": longitude,
            "service_radius_km": 20,
            "service_location_authorized": True,
        },
        format="json",
    )

    assert response.status_code == 200
    area = InstructorServiceArea.objects.get(profile__person__account__username="real-instructor")
    assert (area.city, area.uf) == (city, uf)
    assert area.private_location is None
    assert area.profile.publication_status == "UNPUBLISHED"


@pytest.mark.django_db
@override_settings(**PILOT)
def test_real_instructor_onboarding_rejects_unknown_uf():
    client = APIClient()
    assert (
        client.post(
            "/api/v1/marketplace/accounts/register/", payload("INSTRUCTOR"), format="json"
        ).status_code
        == 201
    )
    response = client.patch(
        "/api/v1/account/me/",
        {
            "instructor_city": "Cidade inválida",
            "instructor_uf": "XX",
            "service_latitude": -15,
            "service_longitude": -47,
        },
        format="json",
    )
    assert response.status_code == 400


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

    response = APIClient().post("/api/v1/marketplace/accounts/register/", data, format="json")

    assert response.status_code == 400
    assert not Account.objects.filter(email=data["email"]).exists()


@pytest.mark.django_db
@override_settings(**PILOT)
def test_acceptance_failure_rolls_back_account_person_and_role():
    with (
        patch(
            "apps.marketplace.api.LegalAcceptanceRecord.objects.create",
            side_effect=RuntimeError("acceptance persistence failed"),
        ),
        pytest.raises(RuntimeError),
    ):
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
)
def test_real_selector_blocks_publication_in_uf_without_explicit_readiness():
    go = _published_profile(
        "selector-go",
        is_demo=False,
        data_mode=DataMode.REAL,
        city="Goiânia",
        uf="GO",
        latitude=-16.6869,
        longitude=-49.2648,
    )
    results = search_published_instructors(
        latitude=-16.6869, longitude=-49.2648, radius_km=10, category="B"
    )
    assert go not in list(results)


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


def _published_profile(
    username,
    *,
    is_demo,
    data_mode,
    publication_status="APPROVED",
    city="Porto Alegre",
    uf="RS",
    latitude=-30.0346,
    longitude=-51.2177,
):
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
        city=city,
        uf=uf,
        public_service_location=Point(longitude, latitude, srid=4326),
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
