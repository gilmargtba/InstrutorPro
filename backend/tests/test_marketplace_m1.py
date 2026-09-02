import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.marketplace.models import (
    DataMode,
    InstructorOnboardingDraft,
    InstructorVehicle,
    StudentDemand,
    StudentProfile,
)
from apps.people.models import Person, RoleAssignment
from apps.territories.models import Country, FederativeUnit


@pytest.fixture
def rs(db):
    country, _ = Country.objects.get_or_create(code="BR", defaults={"name": "Brasil"})
    uf, _ = FederativeUnit.objects.get_or_create(
        code="RS", defaults={"name": "Rio Grande do Sul", "ibge_code": "43", "country": country}
    )
    return uf


@pytest.mark.django_db
def test_registration_rejects_non_synthetic_identity(rs):
    response = APIClient().post(
        "/api/v1/demo/marketplace/students/register/",
        {
            "username": "real",
            "email": "person@gmail.com",
            "password": "SafePassword123!",
            "password_confirmation": "SafePassword123!",
            "display_name": "Pessoa",
            "city": "Porto Alegre",
            "uf": "RS",
            "intended_category": "B",
            "synthetic_data_confirmed": True,
        },
        format="json",
    )
    assert response.status_code == 400
    assert Account.objects.count() == 0


@pytest.mark.django_db
def test_synthetic_registration_creates_role_session_and_demand(rs):
    client = APIClient()
    response = client.post(
        "/api/v1/demo/marketplace/students/register/",
        {
            "username": "aluno_demo",
            "email": "aluno@example.invalid",
            "password": "SafePassword123!",
            "password_confirmation": "SafePassword123!",
            "display_name": "Aluno Demo",
            "city": "Porto Alegre",
            "uf": "RS",
            "intended_category": "B",
            "preferred_transmission": "INDIFFERENT",
            "synthetic_data_confirmed": True,
        },
        format="json",
    )
    assert response.status_code == 201
    profile = StudentProfile.objects.get()
    assert profile.data_mode == DataMode.SYNTHETIC
    assert profile.preferred_transmission == "INDIFFERENT"
    assert RoleAssignment.objects.filter(person=profile.person, role="STUDENT").exists()
    response = client.post(
        "/api/v1/demo/marketplace/demands/",
        {
            "category": "B",
            "city": "Porto Alegre",
            "uf": "RS",
            "region": "Centro",
            "radius_km": 10,
            "transmission": "MANUAL",
            "availability": "Noite",
        },
        format="json",
    )
    assert response.status_code == 201
    assert StudentDemand.objects.get().data_mode == DataMode.SYNTHETIC


@pytest.mark.django_db
def test_registration_rejects_duplicate_email_and_password_mismatch(rs):
    Account.objects.create_user(
        username="existing", email="existing@example.invalid", password="SafePassword123!"
    )
    payload = {
        "username": "another",
        "email": "existing@example.invalid",
        "password": "SafePassword123!",
        "password_confirmation": "DifferentPassword123!",
        "display_name": "Aluno Demo",
        "city": "Porto Alegre",
        "uf": "RS",
        "intended_category": "B",
        "preferred_transmission": "MANUAL",
        "synthetic_data_confirmed": True,
    }
    response = APIClient().post(
        "/api/v1/demo/marketplace/students/register/", payload, format="json"
    )
    assert response.status_code == 400
    assert Account.objects.count() == 1


@pytest.mark.django_db
def test_aggregate_suppresses_groups_below_threshold(settings, rs):
    settings.DEMAND_MAP_MIN_AGGREGATION_COUNT = 3
    account = Account.objects.create_user(
        username="student", email="student@example.invalid", password="pass"
    )
    person = Person.objects.create(account=account)
    student = StudentProfile.objects.create(
        person=person, display_name="Demo", city="Porto Alegre", uf=rs, data_mode=DataMode.SYNTHETIC
    )
    for _ in range(2):
        StudentDemand.objects.create(
            student=student, category="B", city="Porto Alegre", uf=rs, data_mode=DataMode.SYNTHETIC
        )
    assert APIClient().get("/api/v1/demo/marketplace/demand-aggregates/").json()["regions"] == []
    StudentDemand.objects.create(
        student=student, category="B", city="Porto Alegre", uf=rs, data_mode=DataMode.SYNTHETIC
    )
    assert APIClient().get("/api/v1/demo/marketplace/demand-aggregates/").json()["regions"] == [
        {"uf": "RS", "city": "Porto Alegre", "count": 3}
    ]


def test_real_feature_flags_remain_disabled(settings):
    assert not settings.REAL_STUDENT_REGISTRATION_ENABLED
    assert not settings.REAL_INSTRUCTOR_REGISTRATION_ENABLED
    assert not settings.REAL_INSTRUCTOR_PUBLICATION_ENABLED
    assert not settings.REAL_STUDENT_DEMAND_ENABLED
    assert not settings.PUBLIC_DEMAND_MAP_ENABLED


@pytest.mark.django_db
def test_instructor_onboarding_persists_steps_resumes_and_submits(rs):
    client = APIClient()
    first = client.post(
        "/api/v1/demo/instructor-onboarding/draft/",
        {
            "step": 1,
            "email": "persistent-instructor@example.invalid",
            "password": "SafePassword123!",
            "display_name": "Instrutor Persistente Demo",
            "prerequisite_accepted": True,
        },
        format="json",
    )
    assert first.status_code == 200
    profile = InstructorProfile.objects.get(
        person__account__email="persistent-instructor@example.invalid"
    )
    assert profile.profile_status == InstructorProfile.Status.DRAFT
    assert InstructorOnboardingDraft.objects.get(instructor=profile).completed_steps == [1]

    vehicle = client.post(
        "/api/v1/demo/instructor-onboarding/draft/",
        {
            "step": 4,
            "category": "B",
            "vehicle_available": True,
            "vehicle_make": "Marca Teste",
            "vehicle_model": "Modelo Teste",
            "vehicle_year": 2024,
            "vehicle_transmission": "MANUAL",
        },
        format="json",
    )
    assert vehicle.status_code == 200
    assert InstructorVehicle.objects.get(instructor=profile).make == "Marca Teste"

    location = client.post(
        "/api/v1/demo/instructor-onboarding/draft/",
        {
            "step": 5,
            "city": "Porto Alegre",
            "uf": "RS",
            "region": "Centro",
            "radius_km": 10,
            "latitude": -30.0346,
            "longitude": -51.2177,
            "location_authorized": True,
        },
        format="json",
    )
    assert location.status_code == 200
    resumed = client.get("/api/v1/demo/instructor-onboarding/draft/")
    assert resumed.status_code == 200
    assert resumed.json()["service_area"]["city"] == "Porto Alegre"
    assert resumed.json()["current_step"] == 6

    submitted = client.post("/api/v1/demo/instructor-onboarding/submit/", {}, format="json")
    assert submitted.status_code == 200
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.SUBMITTED
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    assert AuditEvent.objects.filter(
        target_id=profile.id, action="discovery.synthetic_onboarding.completed"
    ).exists()
