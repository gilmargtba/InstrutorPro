import uuid

import pytest
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.urls import reverse

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.audit.services import redact_metadata
from apps.organizations.models import Clinic, ClinicMembership
from apps.people.models import Person, RoleAssignment
from apps.people.services import grant_role
from apps.territories.models import FederativeUnit, RegulatoryReadiness


@pytest.mark.django_db
def test_health_and_request_id(client):
    request_id = str(uuid.uuid4())
    response = client.get(reverse("health"), HTTP_X_REQUEST_ID=request_id)
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_invalid_request_id_is_replaced(client):
    response = client.get(reverse("health"), HTTP_X_REQUEST_ID="not-a-uuid")
    assert response.status_code == 200
    assert uuid.UUID(response.headers["X-Request-ID"])


@pytest.mark.django_db
def test_readiness_checks_database(client):
    response = client.get(reverse("readiness"))
    assert response.status_code == 200
    assert response.json()["checks"]["database"] == "up"


@pytest.mark.django_db
def test_territorial_seed_is_idempotent():
    call_command("seed_territories")
    call_command("seed_territories")
    assert FederativeUnit.objects.count() == 27
    assert set(
        FederativeUnit.objects.filter(commercial_status="FIRST_WAVE").values_list("code", flat=True)
    ) == {"RS", "SC", "SP", "RJ", "ES"}
    assert (
        FederativeUnit.objects.exclude(code__in={"RS", "SC", "SP", "RJ", "ES"})
        .filter(commercial_status="PREPARATION")
        .count()
        == 22
    )
    assert RegulatoryReadiness.objects.count() == 0


@pytest.fixture
def synthetic_person(db):
    account = Account.objects.create_user(
        username="synthetic-account", email="synthetic@example.invalid", password="test-only"
    )
    return Person.objects.create(account=account)


@pytest.fixture
def authorized_actor(db):
    actor = Account.objects.create_user(
        username="synthetic-operator",
        email="operator@example.invalid",
        password="test-only",
    )
    actor.user_permissions.add(Permission.objects.get(codename="manage_role_assignments"))
    return actor


def test_synthetic_account_and_person_can_exist_without_role(synthetic_person):
    assert synthetic_person.account.email.endswith(".invalid")
    assert synthetic_person.role_assignments.count() == 0


@pytest.mark.parametrize(
    "role",
    [
        RoleAssignment.Role.STUDENT,
        RoleAssignment.Role.INSTRUCTOR,
        RoleAssignment.Role.DOCTOR,
        RoleAssignment.Role.PSYCHOLOGIST,
    ],
)
def test_each_personal_role_can_be_assigned_independently(synthetic_person, authorized_actor, role):
    assignment = grant_role(
        actor=authorized_actor,
        person=synthetic_person,
        role=role,
        reason="FOUNDATION_TEST",
        actor_context="ADMIN",
    )
    assert assignment.role == role
    assert assignment.revoked_at is None


def test_student_and_instructor_roles_are_compatible_and_idempotent(
    synthetic_person, authorized_actor
):
    command = {"actor": authorized_actor, "person": synthetic_person, "actor_context": "ADMIN"}
    student = grant_role(role=RoleAssignment.Role.STUDENT, reason="FIRST_GRANT", **command)
    instructor = grant_role(role=RoleAssignment.Role.INSTRUCTOR, reason="FIRST_GRANT", **command)
    repeated_student = grant_role(role=RoleAssignment.Role.STUDENT, reason="RETRY", **command)

    assert student.pk == repeated_student.pk
    assert instructor.pk != student.pk
    assert set(synthetic_person.role_assignments.values_list("role", flat=True)) == {
        "STUDENT",
        "INSTRUCTOR",
    }


def test_all_personal_roles_can_coexist_without_permission_inheritance(
    synthetic_person, authorized_actor
):
    for role in RoleAssignment.Role.values:
        grant_role(
            actor=authorized_actor,
            person=synthetic_person,
            role=role,
            reason="COMPATIBILITY_TEST",
            actor_context="ADMIN",
        )

    assert synthetic_person.role_assignments.count() == 4
    assert synthetic_person.account.user_permissions.count() == 0
    assert synthetic_person.account.groups.count() == 0


def test_clinic_is_an_organization_linked_by_explicit_membership(synthetic_person):
    clinic = Clinic.objects.create(display_name="Clínica Sintética")
    membership = ClinicMembership.objects.create(
        clinic=clinic,
        person=synthetic_person,
        authorization=ClinicMembership.Authorization.RESPONSIBLE,
    )

    assert membership.is_active
    assert clinic.memberships.get() == membership
    assert "CLINIC" not in RoleAssignment.Role.values


@pytest.mark.django_db
def test_audit_event_accepts_system_actor_and_is_append_only():
    event = AuditEvent.objects.create(action="foundation.checked", target_type="system")
    assert event.actor is None
    event.reason_code = "changed"
    with pytest.raises(ValueError, match="append-only"):
        event.save()
    with pytest.raises(ValueError, match="append-only"):
        event.delete()


def test_audit_metadata_redacts_sensitive_keys():
    result = redact_metadata({"token": "secret-value", "safe_count": 27})
    assert result == {"token": "[REDACTED]", "safe_count": 27}
