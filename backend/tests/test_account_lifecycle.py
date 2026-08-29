import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.db import connections
from django.test import RequestFactory

from apps.accounts.models import Account
from apps.accounts.policies import can_account_operate, can_manage_account_lifecycle
from apps.accounts.services import (
    AccountLifecycleConflict,
    AccountLifecycleInvalidTransition,
    AccountLifecyclePermissionDenied,
    activate_account,
    block_account,
    deactivate_account,
)
from apps.audit.models import AuditEvent
from apps.people.models import Person, RoleAssignment
from apps.people.services import grant_role, revoke_role


@pytest.fixture
def actor(db):
    account = Account.objects.create_user(
        username="lifecycle-operator",
        email="lifecycle-operator@example.invalid",
        password="test-only",
    )
    account.user_permissions.add(
        Permission.objects.get(codename="manage_account_lifecycle"),
        Permission.objects.get(codename="manage_role_assignments"),
    )
    return account


@pytest.fixture
def target(db):
    return Account.objects.create_user(
        username="lifecycle-target",
        email="lifecycle-target@example.invalid",
        password="test-only",
    )


def command(actor, target, reason="LIFECYCLE_TEST"):
    return {
        "actor": actor,
        "account": target,
        "reason": reason,
        "actor_context": "ADMIN",
        "expected_version": target.lifecycle_version,
    }


def test_account_starts_active_and_can_operate(target):
    assert target.lifecycle_status == Account.LifecycleStatus.ACTIVE
    assert target.lifecycle_version == 0
    assert target.is_active
    assert can_account_operate(account=target)


def test_block_and_explicit_reactivation(actor, target):
    blocked = block_account(**command(actor, target, reason="SECURITY_BLOCK"))
    assert blocked.lifecycle_status == Account.LifecycleStatus.BLOCKED
    assert not blocked.is_active

    activated = activate_account(**command(actor, blocked, reason="REACTIVATION_APPROVED"))
    assert activated.lifecycle_status == Account.LifecycleStatus.ACTIVE
    assert activated.is_active


@pytest.mark.parametrize(
    ("operation", "target_status"),
    [
        (activate_account, Account.LifecycleStatus.ACTIVE),
        (block_account, Account.LifecycleStatus.BLOCKED),
        (deactivate_account, Account.LifecycleStatus.DEACTIVATED),
    ],
)
def test_repeated_target_state_is_idempotent(actor, target, operation, target_status):
    if target_status != Account.LifecycleStatus.ACTIVE:
        first = operation(**command(actor, target, reason="FIRST_COMMAND"))
    else:
        first = target
    events_before = AuditEvent.objects.filter(target_id=target.id).count()
    repeated = operation(**command(actor, first, reason="RETRY_COMMAND"))

    assert repeated.lifecycle_status == target_status
    assert repeated.lifecycle_version == first.lifecycle_version
    assert AuditEvent.objects.filter(target_id=target.id).count() == events_before


def test_deactivated_account_is_terminal_in_this_slice(actor, target):
    deactivated = deactivate_account(**command(actor, target, reason="CLOSE_ACCOUNT"))
    with pytest.raises(AccountLifecycleInvalidTransition):
        activate_account(**command(actor, deactivated, reason="UNSUPPORTED_REACTIVATION"))
    with pytest.raises(AccountLifecycleInvalidTransition):
        block_account(**command(actor, deactivated, reason="INVALID_BLOCK"))


@pytest.mark.parametrize("operation", [activate_account, block_account, deactivate_account])
def test_unauthorized_actor_is_denied(actor, target, operation):
    unauthorized = Account.objects.create_user(
        username=f"unauthorized-{operation.__name__}",
        email=f"{operation.__name__}@example.invalid",
        password="test-only",
    )
    with pytest.raises(AccountLifecyclePermissionDenied):
        operation(**command(unauthorized, target))


def test_deny_by_default_includes_superuser_without_explicit_permission(target):
    superuser = Account.objects.create_superuser(
        username="implicit-lifecycle-superuser",
        email="implicit-lifecycle-superuser@example.invalid",
        password="test-only",
    )
    assert not can_manage_account_lifecycle(actor=None)
    assert not can_manage_account_lifecycle(actor=superuser)
    with pytest.raises(AccountLifecyclePermissionDenied):
        block_account(**command(superuser, target))


@pytest.mark.parametrize("operation", [block_account, deactivate_account])
def test_non_active_account_cannot_authenticate_or_operate(actor, target, operation):
    changed = operation(**command(actor, target))
    assert not can_account_operate(account=changed)
    assert (
        authenticate(
            request=RequestFactory().post("/admin/login/"),
            username=target.username,
            password="test-only",
        )
        is None
    )


def test_block_preserves_person_and_role_assignments(actor, target):
    person = Person.objects.create(account=target)
    assignment = grant_role(
        actor=actor,
        person=person,
        role=RoleAssignment.Role.INSTRUCTOR,
        reason="SYNTHETIC_GRANT",
        actor_context="ADMIN",
    )
    block_account(**command(actor, target))

    assert Person.objects.filter(pk=person.pk, account=target).exists()
    assert RoleAssignment.objects.filter(pk=assignment.pk, revoked_at__isnull=True).exists()


def test_deactivation_preserves_account_person_roles_and_audit(actor, target):
    person = Person.objects.create(account=target)
    assignment = grant_role(
        actor=actor,
        person=person,
        role=RoleAssignment.Role.STUDENT,
        reason="SYNTHETIC_GRANT",
        actor_context="ADMIN",
    )
    deactivate_account(**command(actor, target, reason="SYNTHETIC_DEACTIVATION"))

    assert Account.objects.filter(pk=target.pk).exists()
    assert Person.objects.filter(pk=person.pk).exists()
    assert RoleAssignment.objects.filter(pk=assignment.pk).exists()
    assert AuditEvent.objects.filter(
        target_id=target.pk, action="accounts.account_deactivated"
    ).exists()


def test_role_revocation_does_not_change_account_lifecycle(actor, target):
    person = Person.objects.create(account=target)
    grant_role(
        actor=actor,
        person=person,
        role=RoleAssignment.Role.STUDENT,
        reason="SYNTHETIC_GRANT",
        actor_context="ADMIN",
    )
    revoke_role(
        actor=actor,
        person=person,
        role=RoleAssignment.Role.STUDENT,
        reason="SYNTHETIC_REVOKE",
        actor_context="ADMIN",
    )
    target.refresh_from_db()
    assert target.lifecycle_status == Account.LifecycleStatus.ACTIVE
    assert target.is_active


def test_stale_transition_is_rejected(actor, target):
    blocked = block_account(**command(actor, target))
    with pytest.raises(AccountLifecycleConflict):
        activate_account(
            actor=actor,
            account=blocked,
            reason="STALE_ACTIVATION",
            actor_context="ADMIN",
            expected_version=0,
        )


@pytest.mark.django_db(transaction=True)
def test_concurrent_duplicate_blocks_are_idempotent():
    permission = Permission.objects.get(codename="manage_account_lifecycle")
    actor = Account.objects.create_user(
        username="concurrent-lifecycle-operator",
        email="concurrent-lifecycle-operator@example.invalid",
        password="test-only",
    )
    actor.user_permissions.add(permission)
    target = Account.objects.create_user(
        username="concurrent-lifecycle-target",
        email="concurrent-lifecycle-target@example.invalid",
        password="test-only",
    )
    barrier = Barrier(2)

    def worker():
        connections.close_all()
        try:
            barrier.wait()
            local_actor = Account.objects.get(pk=actor.pk)
            local_target = Account.objects.get(pk=target.pk)
            return block_account(
                actor=local_actor,
                account=local_target,
                reason="CONCURRENT_BLOCK",
                actor_context="ADMIN",
                expected_version=0,
            ).lifecycle_status
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: worker(), range(2)))

    assert results == [Account.LifecycleStatus.BLOCKED] * 2
    assert (
        AuditEvent.objects.filter(target_id=target.pk, action="accounts.account_blocked").count()
        == 1
    )


@pytest.mark.django_db(transaction=True)
def test_concurrent_block_and_deactivate_end_deactivated():
    permission = Permission.objects.get(codename="manage_account_lifecycle")
    actor = Account.objects.create_user(
        username="priority-lifecycle-operator",
        email="priority-lifecycle-operator@example.invalid",
        password="test-only",
    )
    actor.user_permissions.add(permission)
    target = Account.objects.create_user(
        username="priority-lifecycle-target",
        email="priority-lifecycle-target@example.invalid",
        password="test-only",
    )
    barrier = Barrier(2)

    def worker(operation):
        connections.close_all()
        try:
            barrier.wait()
            local_actor = Account.objects.get(pk=actor.pk)
            local_target = Account.objects.get(pk=target.pk)
            try:
                operation(
                    actor=local_actor,
                    account=local_target,
                    reason="CONCURRENT_TERMINAL_STATE",
                    actor_context="ADMIN",
                    expected_version=0,
                )
            except AccountLifecycleInvalidTransition:
                pass
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(worker, [block_account, deactivate_account]))

    target.refresh_from_db()
    assert target.lifecycle_status == Account.LifecycleStatus.DEACTIVATED
    assert not target.is_active


def test_effective_transitions_are_audited_with_reason_and_before_after(actor, target):
    request_id = uuid.uuid4()
    blocked = block_account(**command(actor, target, reason="AUDITED_BLOCK"), request_id=request_id)
    activated = activate_account(
        **command(actor, blocked, reason="AUDITED_ACTIVATION"), request_id=request_id
    )
    deactivate_account(
        **command(actor, activated, reason="AUDITED_DEACTIVATION"), request_id=request_id
    )
    events = list(AuditEvent.objects.filter(target_id=target.id).order_by("occurred_at"))

    assert [event.action for event in events] == [
        "accounts.account_blocked",
        "accounts.account_activated",
        "accounts.account_deactivated",
    ]
    assert [event.reason_code for event in events] == [
        "AUDITED_BLOCK",
        "AUDITED_ACTIVATION",
        "AUDITED_DEACTIVATION",
    ]
    assert all(event.actor == actor and event.request_id == request_id for event in events)
    assert events[0].metadata["before"] == {"status": "ACTIVE", "version": 0}
    assert events[-1].metadata["after"] == {"status": "DEACTIVATED", "version": 3}
    assert "email" not in str(events[0].metadata).lower()
