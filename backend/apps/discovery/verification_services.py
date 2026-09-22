from uuid import UUID

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.capabilities import enabled
from apps.people.identifiers import encrypt_identifier, fingerprint_identifier, normalize_cpf

from .models import (
    InstructorProfile,
    ProfessionalVerification,
    ProfessionalVerificationRequest,
    allow_critical_state_mutation,
)
from .services import InvalidWorkflowTransition, WorkflowPermissionDenied

SAFE_REJECTION_MESSAGE = (
    "Não foi possível concluir a verificação. Revise seus dados e envie uma nova solicitação."
)


def _request_id(value):
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def _audit(actor, action, request, reason, request_id=None, **metadata):
    AuditEvent.objects.create(
        actor=actor,
        action=f"discovery.professional_verification.{action}",
        target_type="discovery.ProfessionalVerificationRequest",
        target_id=request.id,
        request_id=_request_id(request_id),
        reason_code=reason,
        metadata={"status": request.status, **metadata},
    )


def can_review(actor):
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and actor.has_perm("discovery.review_professional_verification")
    )


def _require_feature(profile):
    if profile.is_demo or not enabled("REAL_PROFESSIONAL_VERIFICATION"):
        raise WorkflowPermissionDenied("A verificação profissional real não está disponível.")


@transaction.atomic
def save_verification_draft(*, actor, profile, cpf, request_id=None):
    profile = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if actor != profile.person.account:
        raise WorkflowPermissionDenied("Somente o próprio instrutor pode informar seus dados.")
    _require_feature(profile)
    latest = (
        ProfessionalVerificationRequest.objects.select_for_update()
        .filter(profile=profile)
        .order_by("-created_at")
        .first()
    )
    if latest and latest.status in {
        ProfessionalVerificationRequest.Status.SUBMITTED,
        ProfessionalVerificationRequest.Status.UNDER_REVIEW,
        ProfessionalVerificationRequest.Status.VERIFIED,
    }:
        raise InvalidWorkflowTransition(
            "O CPF não pode ser alterado enquanto a solicitação estiver em andamento."
        )
    person = profile.person.__class__.objects.select_for_update().get(pk=profile.person_id)
    normalized = normalize_cpf(cpf)
    fingerprint = fingerprint_identifier(normalized)
    try:
        person.cpf_ciphertext = encrypt_identifier(normalized)
        person.cpf_fingerprint = fingerprint
        person.cpf_last2 = normalized[-2:]
        person.cpf_key_version = "v1"
        person.save(
            update_fields=["cpf_ciphertext", "cpf_fingerprint", "cpf_last2", "cpf_key_version"]
        )
    except IntegrityError as exc:
        raise InvalidWorkflowTransition("Este CPF já está vinculado a outra conta.") from exc

    current = latest if latest and latest.status == latest.Status.DRAFT else None
    if current is None:
        current = ProfessionalVerificationRequest.objects.create(profile=profile)
    _audit(actor, "draft_saved", current, "OWNER_DRAFT_SAVED", request_id, fields=["cpf"])
    return current


@transaction.atomic
def submit_verification_request(*, actor, profile, request_id=None):
    profile = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if actor != profile.person.account:
        raise WorkflowPermissionDenied("Somente o próprio instrutor pode enviar a solicitação.")
    _require_feature(profile)
    current = (
        ProfessionalVerificationRequest.objects.select_for_update()
        .filter(profile=profile)
        .order_by("-created_at")
        .first()
    )
    if current and current.status in {
        ProfessionalVerificationRequest.Status.SUBMITTED,
        ProfessionalVerificationRequest.Status.UNDER_REVIEW,
        ProfessionalVerificationRequest.Status.VERIFIED,
    }:
        return current, False
    if not profile.person.cpf_ciphertext:
        raise InvalidWorkflowTransition("Informe um CPF válido antes de enviar a solicitação.")
    if current is None or current.status == ProfessionalVerificationRequest.Status.REJECTED:
        raise InvalidWorkflowTransition(
            "Revise e confirme o CPF antes de enviar uma nova solicitação."
        )
    current.status = ProfessionalVerificationRequest.Status.SUBMITTED
    current.submitted_at = timezone.now()
    with allow_critical_state_mutation():
        current.save(update_fields=["status", "submitted_at", "updated_at"])
    _audit(actor, "submitted", current, "OWNER_SUBMITTED", request_id)
    return current, True


@transaction.atomic
def start_verification_review(*, actor, verification_request, request_id=None):
    if not can_review(actor):
        raise WorkflowPermissionDenied("Permissão de revisão profissional obrigatória.")
    item = ProfessionalVerificationRequest.objects.select_for_update().get(
        pk=verification_request.pk
    )
    if item.status == item.Status.UNDER_REVIEW and item.reviewer_id == actor.id:
        return item, False
    if item.status != item.Status.SUBMITTED:
        raise InvalidWorkflowTransition("Somente solicitação enviada pode iniciar análise.")
    if item.reviewer_id and item.reviewer_id != actor.id:
        raise InvalidWorkflowTransition("Solicitação já atribuída a outro revisor.")
    item.status = item.Status.UNDER_REVIEW
    item.reviewer = actor
    item.review_started_at = timezone.now()
    with allow_critical_state_mutation():
        item.save(update_fields=["status", "reviewer", "review_started_at", "updated_at"])
    profile = InstructorProfile.objects.select_for_update().get(pk=item.profile_id)
    profile.verification_status = InstructorProfile.VerificationStatus.PENDING
    with allow_critical_state_mutation():
        profile.save(update_fields=["verification_status"])
    _audit(actor, "review_started", item, "ADMIN_REVIEW_STARTED", request_id)
    return item, True


def _lock_for_decision(actor, verification_request):
    if not can_review(actor):
        raise WorkflowPermissionDenied("Permissão de revisão profissional obrigatória.")
    item = ProfessionalVerificationRequest.objects.select_for_update().get(
        pk=verification_request.pk
    )
    if item.status != item.Status.UNDER_REVIEW:
        raise InvalidWorkflowTransition("A decisão exige solicitação em análise.")
    if item.reviewer_id != actor.id:
        raise InvalidWorkflowTransition("Somente o revisor responsável pode decidir.")
    return item


@transaction.atomic
def approve_verification_request(*, actor, verification_request, request_id=None):
    item = _lock_for_decision(actor, verification_request)
    if (
        not item.verification_method.strip()
        or not item.verification_source.strip()
        or not item.checked_at
    ):
        raise InvalidWorkflowTransition("Método, fonte e data da consulta são obrigatórios.")
    now = timezone.now()
    item.status = item.Status.VERIFIED
    item.decided_at = now
    item.decision_by = actor
    item.public_message = "Verificação profissional concluída."
    with allow_critical_state_mutation():
        item.save(
            update_fields=["status", "decided_at", "decision_by", "public_message", "updated_at"]
        )
    profile = InstructorProfile.objects.select_for_update().get(pk=item.profile_id)
    profile.verification_status = InstructorProfile.VerificationStatus.VERIFIED
    with allow_critical_state_mutation():
        profile.save(update_fields=["verification_status"])
    ProfessionalVerification.objects.create(
        profile=profile,
        provider="MANUAL_AUTHORIZED_SOURCE",
        authority=item.verification_source.strip(),
        method=item.verification_method.strip(),
        provenance_reference=str(item.id),
        status=ProfessionalVerification.Status.VERIFIED,
        verified_at=now,
        actor=actor,
        reason="ADMIN_PROFESSIONAL_VERIFICATION_APPROVED",
    )
    _audit(actor, "approved", item, "ADMIN_APPROVED", request_id)
    return item


@transaction.atomic
def reject_verification_request(*, actor, verification_request, request_id=None):
    item = _lock_for_decision(actor, verification_request)
    if not item.rejection_reason_code.strip():
        raise InvalidWorkflowTransition("O motivo estruturado da rejeição é obrigatório.")
    item.status = item.Status.REJECTED
    item.decided_at = timezone.now()
    item.decision_by = actor
    item.public_message = SAFE_REJECTION_MESSAGE
    with allow_critical_state_mutation():
        item.save(
            update_fields=["status", "decided_at", "decision_by", "public_message", "updated_at"]
        )
    profile = InstructorProfile.objects.select_for_update().get(pk=item.profile_id)
    profile.verification_status = InstructorProfile.VerificationStatus.REJECTED
    with allow_critical_state_mutation():
        profile.save(update_fields=["verification_status"])
    ProfessionalVerification.objects.create(
        profile=profile,
        provider="MANUAL_AUTHORIZED_SOURCE",
        authority=item.verification_source.strip(),
        method=item.verification_method.strip(),
        provenance_reference=str(item.id),
        status=ProfessionalVerification.Status.REJECTED,
        actor=actor,
        reason=item.rejection_reason_code.strip(),
    )
    _audit(actor, "rejected", item, item.rejection_reason_code, request_id)
    return item
