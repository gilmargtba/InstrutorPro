import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.contrib.auth.models import Permission
from django.db import IntegrityError, connections

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.people.models import Person, RoleAssignment
from apps.people.policies import can_manage_role_assignments
from apps.people.services import (
    RoleAssignmentPermissionDenied,
    grant_role,
    revoke_role,
)


@pytest.fixture
def actor(db):
    account = Account.objects.create_user(
        username="role-operator",
        email="role-operator@example.invalid",
        password="test-only",
    )
    account.user_permissions.add(Permission.objects.get(codename="manage_role_assignments"))
    return account


@pytest.fixture
def person(db):
    account = Account.objects.create_user(
        username="role-target",
        email="role-target@example.invalid",
        password="test-only",
    )
    return Person.objects.create(account=account)


def command(actor, person, role=RoleAssignment.Role.STUDENT, reason="TEST_REASON"):
    return {
        "actor": actor,
        "person": person,
        "role": role,
        "reason": reason,
        "actor_context": "ADMIN",
    }


@pytest.mark.parametrize("role", RoleAssignment.Role.values)
def test_grants_each_supported_personal_role(actor, person, role):
    assignment = grant_role(**command(actor, person, role))
    assert assignment.status == "ACTIVE"
    assert assignment.granted_by == actor
    assert assignment.grant_reason == "TEST_REASON"


@pytest.mark.parametrize(
    "roles",
    [
        (RoleAssignment.Role.STUDENT, RoleAssignment.Role.INSTRUCTOR),
        (RoleAssignment.Role.INSTRUCTOR, RoleAssignment.Role.DOCTOR),
    ],
)
def test_compatible_roles_coexist_without_transitive_grants(actor, person, roles):
    for role in roles:
        grant_role(**command(actor, person, role))
    assert set(person.role_assignments.values_list("role", flat=True)) == set(roles)
    assert person.account.user_permissions.count() == 0
    assert person.account.groups.count() == 0


def test_duplicate_grant_is_idempotent(actor, person):
    first = grant_role(**command(actor, person, reason="INITIAL"))
    second = grant_role(**command(actor, person, reason="RETRY"))
    assert first.id == second.id
    assert RoleAssignment.objects.filter(person=person, revoked_at__isnull=True).count() == 1
    assert AuditEvent.objects.filter(action="people.role_grant_idempotent").count() == 1


@pytest.mark.django_db(transaction=True)
def test_concurrent_grants_create_one_active_assignment():
    permission = Permission.objects.get(codename="manage_role_assignments")
    actor = Account.objects.create_user(
        username="concurrent-operator",
        email="concurrent-operator@example.invalid",
        password="test-only",
    )
    actor.user_permissions.add(permission)
    target = Account.objects.create_user(
        username="concurrent-target",
        email="concurrent-target@example.invalid",
        password="test-only",
    )
    person = Person.objects.create(account=target)
    barrier = Barrier(2)

    def worker():
        connections.close_all()
        try:
            barrier.wait()
            local_actor = Account.objects.get(pk=actor.pk)
            local_person = Person.objects.get(pk=person.pk)
            assignment = grant_role(**command(local_actor, local_person, reason="CONCURRENT"))
            return assignment.id
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        ids = list(executor.map(lambda _: worker(), range(2)))

    assert len(set(ids)) == 1
    assert (
        RoleAssignment.objects.filter(
            person=person, role="STUDENT", revoked_at__isnull=True
        ).count()
        == 1
    )


def test_database_rejects_two_equivalent_active_assignments(actor, person):
    grant_role(**command(actor, person))
    with pytest.raises(IntegrityError):
        RoleAssignment.objects.create(
            person=person,
            role=RoleAssignment.Role.STUDENT,
            granted_by=actor,
            grant_reason="BYPASS_ATTEMPT",
        )


def test_revoke_preserves_history_and_is_idempotent(actor, person):
    assignment = grant_role(**command(actor, person, reason="INITIAL"))
    revoked = revoke_role(**command(actor, person, reason="REQUESTED_REVOCATION"))
    repeated = revoke_role(**command(actor, person, reason="RETRY_REVOCATION"))
    assignment.refresh_from_db()

    assert revoked.id == repeated.id == assignment.id
    assert assignment.status == "REVOKED"
    assert assignment.revoked_by == actor
    assert assignment.revoke_reason == "REQUESTED_REVOCATION"
    assert RoleAssignment.objects.filter(pk=assignment.pk).exists()
    assert AuditEvent.objects.filter(action="people.role_revoke_idempotent").count() == 1


def test_reassignment_after_revocation_creates_new_historical_cycle(actor, person):
    first = grant_role(**command(actor, person, reason="FIRST_CYCLE"))
    revoke_role(**command(actor, person, reason="END_FIRST_CYCLE"))
    second = grant_role(**command(actor, person, reason="SECOND_CYCLE"))

    assert first.id != second.id
    assert RoleAssignment.objects.filter(person=person, role="STUDENT").count() == 2
    assert (
        RoleAssignment.objects.filter(
            person=person, role="STUDENT", revoked_at__isnull=True
        ).count()
        == 1
    )


@pytest.mark.parametrize("operation", [grant_role, revoke_role])
def test_unauthorized_actor_is_denied(actor, person, operation):
    unauthorized = Account.objects.create_user(
        username=f"unauthorized-{operation.__name__}",
        email=f"{operation.__name__}@example.invalid",
        password="test-only",
    )
    if operation is revoke_role:
        grant_role(**command(actor, person))
    with pytest.raises(RoleAssignmentPermissionDenied):
        operation(**command(unauthorized, person))


def test_deny_by_default_for_missing_or_inactive_actor(actor):
    assert can_manage_role_assignments(actor=None) is False
    actor.is_active = False
    actor.lifecycle_status = Account.LifecycleStatus.BLOCKED
    actor.save(update_fields=["is_active", "lifecycle_status"])
    assert can_manage_role_assignments(actor=actor) is False


def test_superuser_without_explicit_permission_is_denied(person):
    superuser = Account.objects.create_superuser(
        username="implicit-superuser",
        email="implicit-superuser@example.invalid",
        password="test-only",
    )
    with pytest.raises(RoleAssignmentPermissionDenied):
        grant_role(**command(superuser, person))


def test_grant_and_revoke_audits_are_minimized_and_correlated(actor, person):
    request_id = uuid.uuid4()
    assignment = grant_role(**command(actor, person, reason="AUDITED_GRANT"), request_id=request_id)
    revoke_role(**command(actor, person, reason="AUDITED_REVOKE"), request_id=request_id)
    events = list(AuditEvent.objects.filter(target_id=assignment.id).order_by("occurred_at"))

    assert [event.action for event in events] == ["people.role_granted", "people.role_revoked"]
    assert all(event.actor == actor and event.request_id == request_id for event in events)
    assert events[0].metadata["before"] == {"status": "ABSENT"}
    assert events[0].metadata["after"] == {"status": "ACTIVE"}
    assert events[1].metadata["before"] == {"status": "ACTIVE"}
    assert events[1].metadata["after"] == {"status": "REVOKED"}
    assert "email" not in str(events[0].metadata).lower()


def test_clinic_is_not_a_personal_role(actor, person):
    assert "CLINIC" not in RoleAssignment.Role.values
    with pytest.raises(ValueError, match="Unsupported personal role"):
        grant_role(**command(actor, person, role="CLINIC"))
