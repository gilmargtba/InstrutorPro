from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from django.contrib.gis.geos import Point
from django.db import close_old_connections
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.marketplace.lesson_packages import package_visibility, save_lesson_package
from apps.marketplace.models import DataMode, InstructorLessonPackage, InstructorOffer, Plan
from apps.marketplace.saas import assign_free_plan, ensure_saas_catalog
from apps.people.models import Person, RoleAssignment


@pytest.fixture
def instructor():
    account = Account.objects.create_user(
        username="packages-owner", email="packages-owner@example.invalid", password="safe-test-pass"
    )
    person = Person.objects.create(account=account)
    RoleAssignment.objects.create(person=person, role="INSTRUCTOR", grant_reason="TEST")
    profile = InstructorProfile.objects.create(
        person=person,
        display_name="Instrutora de Pacotes",
        categories=["A", "B"],
        profile_status="APPROVED",
        verification_status="VERIFIED",
        verified_until=timezone.now() + timedelta(days=30),
        publication_status="APPROVED",
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.2177, -30.0346, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    for category in ("A", "B"):
        InstructorOffer.objects.create(
            instructor=profile,
            category=category,
            price_amount="90.00",
            duration_minutes=60,
            data_mode=DataMode.SYNTHETIC,
        )
    assign_free_plan(account)
    return account, profile


def client_for(account):
    client = APIClient()
    client.force_authenticate(account)
    return client


def payload(name="Pacote inicial", **overrides):
    return {
        "name": name,
        "category": "B",
        "lesson_count": 2,
        "price_amount": "170.00",
        "vehicle_included": False,
        "description": "Duas aulas combinadas diretamente.",
        "is_active": True,
        **overrides,
    }


def set_paid_plan(account, code):
    ensure_saas_catalog()
    plan = Plan.objects.get(code=code)
    plan.status = Plan.Status.ACTIVE
    plan.save(update_fields=["status"])
    subscription = account.subscriptions.get(status="ACTIVE")
    subscription.plan = plan
    subscription.current_period_end = timezone.now() + timedelta(days=30)
    subscription.save(update_fields=["plan", "current_period_end"])
    return subscription


@pytest.mark.django_db
def test_free_limit_inactive_edit_and_audit(instructor):
    account, _ = instructor
    client = client_for(account)
    endpoint = "/api/v1/marketplace/instructor/packages/"
    created = client.post(endpoint, payload(), format="json")
    assert created.status_code == 201
    package_id = created.json()["id"]
    assert created.json()["price_per_lesson"] == 85
    assert (
        client.post(endpoint, payload("Segundo"), format="json").json()["code"]
        == "package_limit_reached"
    )
    inactive = client.post(endpoint, payload("Inativo", is_active=False), format="json")
    assert inactive.status_code == 201
    detail = f"{endpoint}{inactive.json()['id']}/"
    assert (
        client.patch(detail, {"is_active": True}, format="json").json()["code"]
        == "package_limit_reached"
    )
    assert (
        client.patch(f"{endpoint}{package_id}/", {"is_active": False}, format="json").status_code
        == 200
    )
    assert (
        client.patch(
            detail, {"is_active": True, "price_amount": "180.00"}, format="json"
        ).status_code
        == 200
    )
    assert client.get(endpoint).json()["active_count"] == 1
    assert AuditEvent.objects.filter(action="marketplace.lesson_package.updated").count() >= 2


@pytest.mark.django_db
@pytest.mark.parametrize("lessons", [2, 5, 10])
@pytest.mark.parametrize("vehicle", [False, True])
def test_allowed_sizes_and_vehicle_options(instructor, lessons, vehicle):
    account, _ = instructor
    response = client_for(account).post(
        "/api/v1/marketplace/instructor/packages/",
        payload(lesson_count=lessons, vehicle_included=vehicle, price_amount="100.00"),
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["vehicle_included"] is vehicle
    assert response.json()["lesson_count"] == lessons


@pytest.mark.django_db
def test_pro_six_premium_unlimited_and_downgrade_visibility(instructor):
    account, profile = instructor
    client = client_for(account)
    endpoint = "/api/v1/marketplace/instructor/packages/"
    subscription = set_paid_plan(account, "PRO")
    for number in range(6):
        assert client.post(endpoint, payload(f"Pacote {number}"), format="json").status_code == 201
    assert (
        client.post(endpoint, payload("Sétimo"), format="json").json()["code"]
        == "package_limit_reached"
    )
    subscription.plan = Plan.objects.get(code="PREMIUM")
    subscription.plan.status = Plan.Status.ACTIVE
    subscription.plan.save(update_fields=["status"])
    subscription.save(update_fields=["plan"])
    for number in range(6, 9):
        assert client.post(endpoint, payload(f"Pacote {number}"), format="json").status_code == 201
    assert client.get(endpoint).json()["active_limit"] is None
    subscription.plan = Plan.objects.get(code="FREE")
    subscription.save(update_fields=["plan"])
    plan, limit, active, visible = package_visibility(profile)
    assert (plan, limit, len(active), [item.name for item in visible]) == (
        "FREE",
        1,
        9,
        ["Pacote 0"],
    )
    assert InstructorLessonPackage.objects.filter(instructor=profile, is_active=True).count() == 9
    assert client.get(endpoint).json()["packages"][1]["visible"] is False
    public = APIClient().get(f"/api/v1/instructors/{profile.pk}/")
    assert public.status_code == 200
    assert [item["name"] for item in public.json()["lesson_packages"]] == ["Pacote 0"]


@pytest.mark.django_db
def test_expired_or_past_due_paid_period_falls_back_to_free(instructor):
    account, profile = instructor
    subscription = set_paid_plan(account, "PRO")
    subscription.current_period_end = timezone.now() - timedelta(seconds=1)
    subscription.save(update_fields=["current_period_end"])
    assert package_visibility(profile)[:2] == ("FREE", 1)
    subscription.current_period_end = timezone.now() + timedelta(days=1)
    subscription.status = "PAST_DUE"
    subscription.save(update_fields=["current_period_end", "status"])
    assert package_visibility(profile)[:2] == ("FREE", 1)


@pytest.mark.django_db
def test_invalid_values_and_cross_instructor_access_are_denied(instructor):
    account, _ = instructor
    client = client_for(account)
    endpoint = "/api/v1/marketplace/instructor/packages/"
    for bad in (payload(lesson_count=3), payload(price_amount="-1"), payload(category="E")):
        assert client.post(endpoint, bad, format="json").status_code == 400
    created = client.post(endpoint, payload(), format="json")
    other = Account.objects.create_user(
        username="other-packages", email="other-packages@example.invalid"
    )
    other_person = Person.objects.create(account=other)
    RoleAssignment.objects.create(person=other_person, role="INSTRUCTOR", grant_reason="TEST")
    InstructorProfile.objects.create(person=other_person, display_name="Outro", categories=["B"])
    other_client = client_for(other)
    assert other_client.get(endpoint).json()["packages"] == []
    assert (
        other_client.patch(
            f"{endpoint}{created.json()['id']}/", {"is_active": False}, format="json"
        ).status_code
        == 404
    )
    assert APIClient().get(endpoint).status_code in (401, 403)


@pytest.mark.django_db
def test_public_profile_shows_only_visible_packages_and_keeps_individual_offers(instructor):
    account, profile = instructor
    client = client_for(account)
    endpoint = "/api/v1/marketplace/instructor/packages/"
    assert client.post(endpoint, payload("Visível"), format="json").status_code == 201
    assert (
        client.post(endpoint, payload("Inativo", is_active=False), format="json").status_code == 201
    )
    public = APIClient().get(f"/api/v1/instructors/{profile.pk}/")
    assert public.status_code == 200
    assert [item["name"] for item in public.json()["lesson_packages"]] == ["Visível"]
    assert [item["category"] for item in public.json()["lesson_options"]] == ["A", "B"]


@pytest.mark.django_db(transaction=True)
def test_concurrent_free_activations_cannot_exceed_limit(instructor):
    account, profile = instructor
    data = payload()

    def attempt(number):
        close_old_connections()
        try:
            save_lesson_package(
                actor=account, profile=profile, data={**data, "name": f"Concorrente {number}"}
            )
            return "created"
        except Exception as exc:
            return type(exc).__name__
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(attempt, [1, 2]))
    assert outcomes.count("created") == 1
    assert InstructorLessonPackage.objects.filter(instructor=profile, is_active=True).count() == 1
