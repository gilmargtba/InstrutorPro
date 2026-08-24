import uuid

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import Account
from .policies import can_manage_account_lifecycle


class AccountLifecyclePermissionDenied(PermissionError):
    pass


class AccountLifecycleConflict(RuntimeError):
    pass


class AccountLifecycleInvalidTransition(RuntimeError):
    pass


def _validate_command(*, actor: Account | None, reason: str, actor_context: str):
    if not can_manage_account_lifecycle(actor=actor):
        raise AccountLifecyclePermissionDenied("Explicit account-lifecycle permission is required")
    if not reason or len(reason) > 100:
        raise ValueError("A reason with at most 100 characters is required")
    if not actor_context or len(actor_context) > 100:
        raise ValueError("An actor context with at most 100 characters is required")


def _transition(
    *,
    actor: Account,
    account: Account,
    target_status: str,
    reason: str,
    actor_context: str,
    expected_version: int,
    request_id: uuid.UUID | None,
) -> Account:
    _validate_command(actor=actor, reason=reason, actor_context=actor_context)
    locked = Account.objects.select_for_update().get(pk=account.pk)
    before_status = locked.lifecycle_status
    before_version = locked.lifecycle_version

    if before_status == target_status:
        return locked
    if before_status == Account.LifecycleStatus.DEACTIVATED:
        raise AccountLifecycleInvalidTransition(
            "A deactivated account cannot transition in CODEX 02B"
        )
    if expected_version != before_version and target_status != Account.LifecycleStatus.DEACTIVATED:
        raise AccountLifecycleConflict("Account lifecycle version is stale")

    locked.lifecycle_status = target_status
    locked.is_active = target_status == Account.LifecycleStatus.ACTIVE
    locked.lifecycle_changed_at = timezone.now()
    locked.lifecycle_changed_by = actor
    locked.lifecycle_reason = reason
    locked.lifecycle_version += 1
    locked.save(
        update_fields=[
            "lifecycle_status",
            "is_active",
            "lifecycle_changed_at",
            "lifecycle_changed_by",
            "lifecycle_reason",
            "lifecycle_version",
        ]
    )
    audit_action = {
        Account.LifecycleStatus.ACTIVE: "accounts.account_activated",
        Account.LifecycleStatus.BLOCKED: "accounts.account_blocked",
        Account.LifecycleStatus.DEACTIVATED: "accounts.account_deactivated",
    }[target_status]
    AuditEvent.objects.create(
        actor=actor,
        action=audit_action,
        target_type="accounts.Account",
        target_id=locked.id,
        request_id=request_id,
        reason_code=reason,
        metadata={
            "actor_context": actor_context,
            "before": {"status": before_status, "version": before_version},
            "after": {"status": target_status, "version": locked.lifecycle_version},
        },
    )
    return locked


@transaction.atomic
def activate_account(
    *,
    actor: Account,
    account: Account,
    reason: str,
    actor_context: str,
    expected_version: int,
    request_id: uuid.UUID | None = None,
) -> Account:
    return _transition(
        actor=actor,
        account=account,
        target_status=Account.LifecycleStatus.ACTIVE,
        reason=reason,
        actor_context=actor_context,
        expected_version=expected_version,
        request_id=request_id,
    )


@transaction.atomic
def block_account(
    *,
    actor: Account,
    account: Account,
    reason: str,
    actor_context: str,
    expected_version: int,
    request_id: uuid.UUID | None = None,
) -> Account:
    return _transition(
        actor=actor,
        account=account,
        target_status=Account.LifecycleStatus.BLOCKED,
        reason=reason,
        actor_context=actor_context,
        expected_version=expected_version,
        request_id=request_id,
    )


@transaction.atomic
def deactivate_account(
    *,
    actor: Account,
    account: Account,
    reason: str,
    actor_context: str,
    expected_version: int,
    request_id: uuid.UUID | None = None,
) -> Account:
    return _transition(
        actor=actor,
        account=account,
        target_status=Account.LifecycleStatus.DEACTIVATED,
        reason=reason,
        actor_context=actor_context,
        expected_version=expected_version,
        request_id=request_id,
    )
