import uuid

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import Account
from apps.audit.models import AuditEvent

from .models import Person, RoleAssignment
from .policies import can_manage_role_assignments


class RoleAssignmentPermissionDenied(PermissionError):
    pass


class RoleAssignmentNotFound(LookupError):
    pass


def _validate_command(*, actor: Account | None, role: str, reason: str, actor_context: str):
    if not can_manage_role_assignments(actor=actor):
        raise RoleAssignmentPermissionDenied("Explicit role-management permission is required")
    if role not in RoleAssignment.Role.values:
        raise ValueError("Unsupported personal role")
    if not reason or len(reason) > 100:
        raise ValueError("A reason with at most 100 characters is required")
    if not actor_context or len(actor_context) > 100:
        raise ValueError("An actor context with at most 100 characters is required")


def _audit(
    *,
    actor: Account,
    actor_context: str,
    action: str,
    assignment: RoleAssignment,
    reason: str,
    before: dict,
    after: dict,
    request_id: uuid.UUID | None,
):
    AuditEvent.objects.create(
        actor=actor,
        action=action,
        target_type="people.RoleAssignment",
        target_id=assignment.id,
        request_id=request_id,
        reason_code=reason,
        metadata={
            "actor_context": actor_context,
            "target_person_id": str(assignment.person_id),
            "role": assignment.role,
            "before": before,
            "after": after,
        },
    )


@transaction.atomic
def grant_role(
    *,
    actor: Account,
    person: Person,
    role: str,
    reason: str,
    actor_context: str,
    request_id: uuid.UUID | None = None,
) -> RoleAssignment:
    _validate_command(actor=actor, role=role, reason=reason, actor_context=actor_context)
    locked_person = Person.objects.select_for_update().get(pk=person.pk)
    active = RoleAssignment.objects.filter(
        person=locked_person, role=role, revoked_at__isnull=True
    ).first()
    if active:
        _audit(
            actor=actor,
            actor_context=actor_context,
            action="people.role_grant_idempotent",
            assignment=active,
            reason=reason,
            before={"status": "ACTIVE"},
            after={"status": "ACTIVE"},
            request_id=request_id,
        )
        return active

    try:
        with transaction.atomic():
            assignment = RoleAssignment.objects.create(
                person=locked_person,
                role=role,
                granted_by=actor,
                grant_reason=reason,
            )
    except IntegrityError:
        assignment = RoleAssignment.objects.get(
            person=locked_person, role=role, revoked_at__isnull=True
        )
    _audit(
        actor=actor,
        actor_context=actor_context,
        action="people.role_granted",
        assignment=assignment,
        reason=reason,
        before={"status": "ABSENT"},
        after={"status": "ACTIVE"},
        request_id=request_id,
    )
    return assignment


@transaction.atomic
def revoke_role(
    *,
    actor: Account,
    person: Person,
    role: str,
    reason: str,
    actor_context: str,
    request_id: uuid.UUID | None = None,
) -> RoleAssignment:
    _validate_command(actor=actor, role=role, reason=reason, actor_context=actor_context)
    locked_person = Person.objects.select_for_update().get(pk=person.pk)
    assignment = (
        RoleAssignment.objects.select_for_update()
        .filter(person=locked_person, role=role, revoked_at__isnull=True)
        .first()
    )
    if assignment is None:
        assignment = (
            RoleAssignment.objects.filter(person=locked_person, role=role)
            .order_by("-granted_at")
            .first()
        )
        if assignment is None:
            raise RoleAssignmentNotFound("Role was never assigned to this person")
        _audit(
            actor=actor,
            actor_context=actor_context,
            action="people.role_revoke_idempotent",
            assignment=assignment,
            reason=reason,
            before={"status": "REVOKED"},
            after={"status": "REVOKED"},
            request_id=request_id,
        )
        return assignment

    assignment.revoked_at = timezone.now()
    assignment.revoked_by = actor
    assignment.revoke_reason = reason
    assignment.save(update_fields=["revoked_at", "revoked_by", "revoke_reason"])
    _audit(
        actor=actor,
        actor_context=actor_context,
        action="people.role_revoked",
        assignment=assignment,
        reason=reason,
        before={"status": "ACTIVE"},
        after={"status": "REVOKED"},
        request_id=request_id,
    )
    return assignment
