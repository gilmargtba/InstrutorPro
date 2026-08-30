from datetime import timedelta

import pytest
from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    LocationPublicationAuthorization,
    ProfessionalVerification,
    PublicationDecision,
)
from apps.discovery.selectors import search_demo_instructors
from apps.discovery.services import (
    InvalidWorkflowTransition,
    PublicationPermissionDenied,
    approve_publication,
    decide_publication,
    grant_service_location_authorization,
    revoke_service_location_authorization,
    start_review,
    submit_profile,
    verify_professional,
)
from apps.people.models import Person, RoleAssignment


@pytest.fixture
def actor(db):
    a = Account.objects.create_user(
        username="reviewer", email="reviewer@example.invalid", password="x"
    )
    a.user_permissions.add(
        Permission.objects.get(
            content_type__app_label="discovery", codename="manage_instructor_publication"
        )
    )
    return a


def make_profile(actor, **overrides):
    n = Account.objects.count()
    account = Account.objects.create_user(
        username=f"demo-{n}", email=f"demo-{n}@example.invalid", password="x"
    )
    person = Person.objects.create(account=account)
    if overrides.pop("role", True):
        RoleAssignment.objects.create(
            person=person, role="INSTRUCTOR", granted_by=actor, grant_reason="DEMO"
        )
    data = {
        "person": person,
        "display_name": "Rafael Demo",
        "categories": ["B"],
        "transmission_options": ["MANUAL"],
        "profile_status": "APPROVED",
        "verification_status": "VERIFIED",
        "verified_until": timezone.now() + timedelta(days=30),
        "publication_status": "APPROVED",
    }
    data.update(overrides)
    profile = InstructorProfile.objects.create(**data)
    area = InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.2177, -30.0346, srid=4326),
        private_location=None,
        radius_km=10,
        location_authorized=True,
    )
    auth = LocationPublicationAuthorization.objects.create(
        service_area=area,
        purpose="DEMO_DISCOVERY",
        policy_version="DEMO-1",
        authorized_at=timezone.now(),
        actor=actor,
    )
    verification = ProfessionalVerification.objects.create(
        profile=profile,
        provider="SYNTHETIC",
        status=profile.verification_status,
        verified_at=timezone.now(),
        verified_until=profile.verified_until,
        actor=actor,
        reason="DEMO",
    )
    return profile, area, auth, verification


def visible():
    return list(
        search_demo_instructors(latitude=-30.0346, longitude=-51.2177, radius_km=10, category="B")
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("profile_status", "DRAFT"),
        ("profile_status", "UNDER_REVIEW"),
        ("verification_status", "PENDING"),
        ("verification_status", "REJECTED"),
        ("publication_status", "UNPUBLISHED"),
    ],
)
def test_ineligible_states_do_not_appear(actor, field, value):
    make_profile(actor, **{field: value})
    assert visible() == []


@pytest.mark.django_db
def test_expired_does_not_appear(actor):
    make_profile(actor, verified_until=timezone.now() - timedelta(seconds=1))
    assert visible() == []


@pytest.mark.django_db
def test_role_without_profile_does_not_appear(actor):
    a = Account.objects.create_user(username="role", email="role@example.invalid", password="x")
    p = Person.objects.create(account=a)
    RoleAssignment.objects.create(
        person=p, role="INSTRUCTOR", granted_by=actor, grant_reason="DEMO"
    )
    assert visible() == []


@pytest.mark.django_db
def test_unauthorized_location_does_not_appear(actor):
    _, area, _, _ = make_profile(actor)
    revoke_service_location_authorization(actor=actor, service_area=area, reason="DEMO_REVOKE")
    assert visible() == []


@pytest.mark.django_db
@pytest.mark.parametrize("lifecycle", ["BLOCKED", "DEACTIVATED"])
def test_inactive_account_does_not_appear(actor, lifecycle):
    profile, *_ = make_profile(actor)
    a = profile.person.account
    a.lifecycle_status = lifecycle
    a.is_active = False
    a.save()
    assert visible() == []


@pytest.mark.django_db
def test_revoked_role_does_not_appear(actor):
    profile, *_ = make_profile(actor)
    role = profile.person.role_assignments.get()
    role.revoked_at = timezone.now()
    role.save()
    assert visible() == []


@pytest.mark.django_db
def test_approved_appears_radius_and_filters_work(actor):
    profile, *_ = make_profile(actor)
    assert visible()[0].id == profile.id
    assert not search_demo_instructors(
        latitude=-31, longitude=-52, radius_km=5, category="B"
    ).exists()
    assert not search_demo_instructors(
        latitude=-30.0346, longitude=-51.2177, radius_km=10, category="B", transmission="AUTOMATIC"
    ).exists()


@pytest.mark.django_db
def test_suspend_unpublish_preserve_history_and_audit(actor):
    profile, *_ = make_profile(actor)
    decide_publication(actor=actor, profile=profile, decision="SUSPEND", reason="DEMO_SUSPEND")
    assert visible() == []
    decide_publication(actor=actor, profile=profile, decision="UNPUBLISH", reason="DEMO_UNPUBLISH")
    assert visible() == []
    assert PublicationDecision.objects.filter(profile=profile).count() == 2
    assert AuditEvent.objects.filter(target_id=profile.id).count() == 2


@pytest.mark.django_db
def test_unauthorized_actor_cannot_publish(actor):
    profile, *_ = make_profile(actor, publication_status="UNPUBLISHED")
    other = Account.objects.create_user(
        username="other", email="other@example.invalid", password="x"
    )
    with pytest.raises(PublicationPermissionDenied):
        decide_publication(actor=other, profile=profile, decision="APPROVE", reason="NO")


@pytest.mark.django_db
def test_location_revocation_removes_and_preserves_history(actor):
    _, area, auth, _ = make_profile(actor)
    revoke_service_location_authorization(actor=actor, service_area=area, reason="DEMO_REVOKE")
    assert visible() == []
    assert area.authorization_history.count() == 1


@pytest.mark.django_db
def test_complete_workflow_and_audit(actor):
    profile, area, _, _ = make_profile(
        actor,
        profile_status="DRAFT",
        verification_status="NOT_STARTED",
        verified_until=None,
        publication_status="UNPUBLISHED",
    )
    # Replace fixture authorization so the consent transition is exercised.
    area.location_authorized = False
    from apps.discovery.models import allow_critical_state_mutation

    with allow_critical_state_mutation():
        area.save(update_fields=["location_authorized"])
    area.authorization_history.all().delete()
    submit_profile(actor=profile.person.account, profile=profile)
    start_review(actor=actor, profile=profile)
    verify_professional(actor=actor, profile=profile)
    grant_service_location_authorization(
        actor=profile.person.account,
        service_area=area,
        purpose="SYNTHETIC_MARKETPLACE_DISCOVERY",
        policy_version="DEMO-1",
        reason="DEMO_CONSENT",
    )
    approve_publication(actor=actor, profile=profile, reason="DEMO_APPROVE")
    profile.refresh_from_db()
    assert (profile.profile_status, profile.verification_status, profile.publication_status) == (
        "APPROVED",
        "VERIFIED",
        "APPROVED",
    )
    assert (
        AuditEvent.objects.filter(
            target_id=profile.id,
            action__in=[
                "discovery.profile_submitted",
                "discovery.profile_review_started",
                "discovery.verification_verified",
                "discovery.location_authorized",
                "discovery.publication_approve",
            ],
        ).count()
        == 5
    )


@pytest.mark.django_db
def test_invalid_transition_and_direct_state_change_are_blocked(actor):
    profile, *_ = make_profile(
        actor,
        profile_status="DRAFT",
        verification_status="NOT_STARTED",
        publication_status="UNPUBLISHED",
    )
    with pytest.raises(InvalidWorkflowTransition):
        start_review(actor=actor, profile=profile)
    profile.publication_status = "APPROVED"
    with pytest.raises(ValueError, match="domain service"):
        profile.save()


@pytest.mark.django_db
def test_demo_onboarding_submits_without_auto_publication():
    response = APIClient().post(
        "/api/v1/demo/instructor-onboarding/",
        {
            "email": "alex-instructor@example.invalid",
            "password": "DemoSeguro123!",
            "prerequisite_accepted": True,
            "display_name": "Alex Demo",
            "city": "Porto Alegre",
            "uf": "RS",
            "category": "B",
            "vehicle_available": True,
            "vehicle_make": "Marca Demo",
            "vehicle_model": "Modelo Demo",
            "vehicle_year": 2024,
            "vehicle_transmission": "MANUAL",
            "transmissions": ["MANUAL"],
            "radius_km": 10,
            "latitude": -30.0346,
            "longitude": -51.2177,
            "location_authorized": True,
            "credential_type": "CREDENCIAL_DEMO",
            "credential_uf": "RS",
            "credential_validity": "12/2027",
            "synthetic_data_confirmed": True,
        },
        format="json",
    )
    assert response.status_code == 201
    profile = InstructorProfile.objects.get(pk=response.json()["id"])
    assert profile.profile_status == "SUBMITTED" and profile.publication_status == "UNPUBLISHED"
    assert (
        profile.service_area.private_location is None and profile.service_area.location_authorized
    )
    assert AuditEvent.objects.filter(target_id=profile.id).count() == 3
    assert profile.vehicle.model == "Modelo Demo"
    assert profile.prerequisite_acceptances.count() == 1
    assert profile.person.account.check_password("DemoSeguro123!")
    assert InstructorProfile in admin.site._registry


@pytest.mark.django_db
def test_api_excludes_private_location(actor):
    make_profile(actor)
    r = APIClient().get(
        "/api/v1/instructors/search/",
        {"latitude": -30.0346, "longitude": -51.2177, "radius_km": 10, "category": "B"},
    )
    assert r.status_code == 200 and r.json()["count"] == 1
    assert "private_location" not in r.json()["results"][0]


@pytest.mark.django_db
def test_national_summary_counts_only_published_instructors(actor):
    make_profile(actor)
    make_profile(actor)
    make_profile(actor, publication_status="UNPUBLISHED")
    profile, area, *_ = make_profile(actor)
    area.uf = "SP"
    area.city = "São Paulo"
    area.save(update_fields=["uf", "city"])

    response = APIClient().get("/api/v1/instructors/states/")

    assert response.status_code == 200
    assert response.json() == {
        "states": [
            {"uf": "RS", "count": 2, "search_location": "Porto Alegre"},
            {"uf": "SP", "count": 1, "search_location": "São Paulo"},
        ]
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params",
    [
        {},
        {"latitude": 91, "longitude": 0, "radius_km": 5, "category": "B"},
        {"latitude": 0, "longitude": 0, "radius_km": 7, "category": "B"},
    ],
)
def test_invalid_api(params):
    assert APIClient().get("/api/v1/instructors/search/", params).status_code == 400
