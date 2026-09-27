"""Policy-gated deletion of private professional evidence.

No production policy is created or approved by this module.
"""

from dataclasses import dataclass
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import DataMode, DocumentRetentionPolicy, InstructorDocument


@dataclass(frozen=True)
class DocumentRetentionResult:
    policy_available: bool
    eligible: int
    processed: int
    dry_run: bool


def approved_policy(scope):
    if scope not in DocumentRetentionPolicy.Scope.values:
        raise ValueError("Escopo de retenção inválido.")
    return DocumentRetentionPolicy.objects.filter(
        scope=scope,
        active=True,
        approved_at__isnull=False,
        approved_by__isnull=False,
    ).first()


def schedule_document_retention(document, *, now=None):
    """Schedule only when an explicitly approved policy already exists."""
    scope = (
        DocumentRetentionPolicy.Scope.PRODUCTION
        if document.data_mode == DataMode.REAL
        else DocumentRetentionPolicy.Scope.TEST
    )
    policy = approved_policy(scope)
    if policy is None:
        return False
    document.retention_policy = policy
    document.retention_expires_at = (now or timezone.now()) + timedelta(days=policy.retention_days)
    document.retention_status = InstructorDocument.RetentionStatus.SCHEDULED
    document.save(update_fields=["retention_policy", "retention_expires_at", "retention_status"])
    AuditEvent.objects.create(
        action="marketplace.professional_document.retention_scheduled",
        target_type="marketplace.InstructorDocument",
        target_id=document.pk,
        reason_code="APPROVED_RETENTION_POLICY",
        metadata={"policy_id": str(policy.pk), "scope": policy.scope},
    )
    return True


def _eligible_documents(scope, policy, now):
    data_mode = (
        DataMode.REAL if scope == DocumentRetentionPolicy.Scope.PRODUCTION else DataMode.SYNTHETIC
    )
    return InstructorDocument.objects.filter(
        data_mode=data_mode,
        retention_policy=policy,
        retention_status=InstructorDocument.RetentionStatus.SCHEDULED,
        retention_expires_at__lte=now,
        legal_hold=False,
    ).order_by("retention_expires_at", "pk")


@transaction.atomic
def _delete_document(document_id, policy, now):
    policy = DocumentRetentionPolicy.objects.select_for_update().get(pk=policy.pk)
    if not policy.active or policy.approved_at is None or policy.approved_by_id is None:
        return False
    try:
        document = InstructorDocument.objects.select_for_update().get(pk=document_id)
    except InstructorDocument.DoesNotExist:
        return False
    if (
        document.data_mode
        != (
            DataMode.REAL
            if policy.scope == DocumentRetentionPolicy.Scope.PRODUCTION
            else DataMode.SYNTHETIC
        )
        or document.retention_policy_id != policy.pk
        or document.retention_status != InstructorDocument.RetentionStatus.SCHEDULED
        or document.retention_expires_at is None
        or document.retention_expires_at > now
        or document.legal_hold
    ):
        return False
    # A missing object is a successful retry after an earlier partial failure.
    document.file.storage.delete(document.file.name)
    AuditEvent.objects.create(
        action="marketplace.professional_document.retention_deleted",
        target_type="marketplace.InstructorDocument",
        target_id=document.pk,
        reason_code="APPROVED_RETENTION_POLICY",
        metadata={"policy_id": str(policy.pk), "scope": policy.scope},
    )
    document.delete()
    return True


def enforce_professional_document_retention(*, scope, dry_run=True, now=None, batch_size=100):
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("Lote de retenção inválido.")
    policy = approved_policy(scope)
    if policy is None:
        return DocumentRetentionResult(False, 0, 0, dry_run)
    now = now or timezone.now()
    queryset = _eligible_documents(scope, policy, now)
    eligible = queryset.count()
    if dry_run:
        return DocumentRetentionResult(True, eligible, 0, True)
    ids = list(queryset.values_list("pk", flat=True)[:batch_size])
    processed = sum(_delete_document(document_id, policy, now) for document_id in ids)
    return DocumentRetentionResult(True, eligible, processed, False)
