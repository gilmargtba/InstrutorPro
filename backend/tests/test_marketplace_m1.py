import pytest
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.marketplace.models import DataMode, StudentDemand, StudentProfile
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
            "display_name": "Aluno Demo",
            "city": "Porto Alegre",
            "uf": "RS",
            "intended_category": "B",
            "synthetic_data_confirmed": True,
        },
        format="json",
    )
    assert response.status_code == 201
    profile = StudentProfile.objects.get()
    assert profile.data_mode == DataMode.SYNTHETIC
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
