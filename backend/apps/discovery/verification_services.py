from uuid import UUID

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.capabilities import enabled
from apps.marketplace.documents import (
    DocumentPermissionDenied,
    DocumentValidationError,
    review_document,
)
from apps.marketplace.models import InstructorDocument
from apps.marketplace.real_documents import applicable_requirements, upload_available
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


def _advance_profile(*, actor, item, target, allowed, reason, request_id=None):
    """Keep the profile workflow aligned with its real verification request."""
    profile = InstructorProfile.objects.select_for_update().get(pk=item.profile_id)
    before = profile.profile_status
    if before == target:
        return profile
    if before not in allowed:
        raise InvalidWorkflowTransition("Estado do perfil incompatível com a verificação.")
    profile.profile_status = target
    with allow_critical_state_mutation():
        profile.save(update_fields=["profile_status"])
    AuditEvent.objects.create(
        actor=actor,
        action="discovery.professional_verification.profile_status_changed",
        target_type="discovery.InstructorProfile",
        target_id=profile.id,
        request_id=_request_id(request_id),
        reason_code=reason,
        metadata={"before": before, "after": target, "verification_request_id": str(item.id)},
    )
    return profile


def can_start_document_supplement(profile, latest=None):
    """A supplement is available only for a verified, unpublished real instructor."""
    if latest is None:
        latest = profile.verification_requests.order_by("-created_at").first()
    return bool(
        latest
        and (
            latest.status == ProfessionalVerificationRequest.Status.VERIFIED
            or (
                latest.status == ProfessionalVerificationRequest.Status.REJECTED
                and latest.previous_verified_request_id
            )
        )
        and not profile.is_demo
        and enabled("REAL_PROFESSIONAL_VERIFICATION")
        and upload_available()
        and profile.person.cpf_ciphertext
        and profile.verification_status
        in {
            InstructorProfile.VerificationStatus.VERIFIED,
            InstructorProfile.VerificationStatus.REJECTED,
        }
        and profile.profile_status
        in {InstructorProfile.Status.UNDER_REVIEW, InstructorProfile.Status.REJECTED}
        and profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    )


@transaction.atomic
def start_document_supplement(*, actor, profile, request_id=None):
    profile = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if actor != profile.person.account:
        raise WorkflowPermissionDenied("Somente o próprio instrutor pode complementar documentos.")
    latest = (
        ProfessionalVerificationRequest.objects.select_for_update()
        .filter(profile=profile)
        .order_by("-created_at")
        .first()
    )
    if latest and latest.status == latest.Status.DRAFT and latest.previous_verified_request_id:
        return latest, False
    if not can_start_document_supplement(profile, latest):
        raise InvalidWorkflowTransition(
            "A complementação exige verificação concluída, upload disponível "
            "e perfil não publicado."
        )
    previous_verified = (
        latest.previous_verified_request if latest.status == latest.Status.REJECTED else latest
    )
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, previous_verified_request=previous_verified
    )
    _audit(
        actor,
        "supplement_started",
        item,
        "OWNER_DOCUMENT_SUPPLEMENT_STARTED",
        request_id,
        previous_verified_request_id=str(previous_verified.id),
    )
    return item, True


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
    if latest and latest.previous_verified_request_id:
        raise InvalidWorkflowTransition(
            "O CPF não pode ser alterado na complementação de documentos."
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
    if current.previous_verified_request_id and not current.documents.exists():
        raise InvalidWorkflowTransition(
            "Anexe ao menos um documento antes de enviar a complementação."
        )
    if current.previous_verified_request_id and not upload_available():
        raise InvalidWorkflowTransition("Envio de documentos indisponível nesta etapa.")
    if current.documents.exclude(scan_status=InstructorDocument.ScanStatus.CLEAN).exists():
        raise InvalidWorkflowTransition(
            "Aguarde a verificação de segurança ou remova arquivos recusados."
        )
    if upload_available() and not current.previous_verified_request_id:
        requirements = list(
            applicable_requirements(profile).order_by("uf", "category", "document_type")
        )
        for requirement in requirements:
            documents = list(current.documents.filter(requirement=requirement))
            if requirement.required and not documents:
                raise InvalidWorkflowTransition(
                    f"Documento obrigatório pendente: {requirement.label}."
                )
            if any(
                document.scan_status != InstructorDocument.ScanStatus.CLEAN
                for document in documents
            ):
                raise InvalidWorkflowTransition("Aguarde a análise antimalware dos documentos.")
        current.requirements_snapshot = [
            {
                "id": str(requirement.id),
                "rule_version": requirement.rule_version,
                "required": requirement.required,
                "document_type": requirement.document_type,
            }
            for requirement in requirements
        ]
    allowed_profile_states = {
        InstructorProfile.Status.DRAFT,
        InstructorProfile.Status.REJECTED,
    }
    if current.previous_verified_request_id:
        allowed_profile_states.add(InstructorProfile.Status.UNDER_REVIEW)
    _advance_profile(
        actor=actor,
        item=current,
        target=InstructorProfile.Status.SUBMITTED,
        allowed=allowed_profile_states,
        reason="OWNER_VERIFICATION_SUBMITTED",
        request_id=request_id,
    )
    if current.previous_verified_request_id:
        profile.verification_status = InstructorProfile.VerificationStatus.PENDING
        with allow_critical_state_mutation():
            profile.save(update_fields=["verification_status"])
    current.status = ProfessionalVerificationRequest.Status.SUBMITTED
    current.submitted_at = timezone.now()
    with allow_critical_state_mutation():
        current.save(
            update_fields=["status", "submitted_at", "requirements_snapshot", "updated_at"]
        )
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
    profile = _advance_profile(
        actor=actor,
        item=item,
        target=InstructorProfile.Status.UNDER_REVIEW,
        allowed={InstructorProfile.Status.DRAFT, InstructorProfile.Status.SUBMITTED},
        reason="ADMIN_VERIFICATION_REVIEW_STARTED",
        request_id=request_id,
    )
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


def review_checklist(item):
    """Operational hints only; never an authorization or approval decision."""
    if item.status != item.Status.UNDER_REVIEW:
        return []
    documents = list(item.documents.all())
    missing = []
    for requirement in item.requirements_snapshot:
        if requirement.get("required") and not any(
            str(document.requirement_id) == str(requirement.get("id"))
            and document.scan_status == InstructorDocument.ScanStatus.CLEAN
            and document.status == InstructorDocument.Status.APPROVED
            for document in documents
        ):
            missing.append("Documento obrigatório sem aprovação individual")
            break
    if any(document.scan_status != InstructorDocument.ScanStatus.CLEAN for document in documents):
        missing.append("Arquivo em quarentena ou sem análise antimalware concluída")
    if item.previous_verified_request_id and any(
        document.status != InstructorDocument.Status.APPROVED for document in documents
    ):
        missing.append("Documento complementar sem aprovação individual")
    elif any(
        document.status
        in {
            InstructorDocument.Status.PENDING,
            InstructorDocument.Status.UNDER_REVIEW,
        }
        for document in documents
    ):
        missing.append("Documento sem revisão individual")
    if not item.verification_method.strip():
        missing.append("Método da consulta não registrado")
    if not item.verification_source.strip():
        missing.append("Fonte da consulta não registrada")
    if not item.checked_at:
        missing.append("Data da consulta não registrada")
    return missing


@transaction.atomic
def record_review_and_approve(
    *,
    actor,
    verification_request,
    method,
    source,
    notes,
    consultation_confirmed,
    reviewed_document_ids=(),
    request_id=None,
):
    """Record the human attestation and decide atomically; no publication follows."""
    item = _lock_for_decision(actor, verification_request)
    method = method.strip()
    source = source.strip()
    if not consultation_confirmed or not method or not source:
        raise InvalidWorkflowTransition("Confirme a consulta e informe método e fonte.")
    if len(method) > 40 or len(source) > 80:
        raise InvalidWorkflowTransition("Método ou fonte excede o tamanho permitido.")
    selected_ids = {str(value) for value in reviewed_document_ids}
    pending_documents = list(
        item.documents.select_for_update().filter(
            status__in=[InstructorDocument.Status.PENDING, InstructorDocument.Status.UNDER_REVIEW]
        )
    )
    pending_by_id = {str(document.pk): document for document in pending_documents}
    if selected_ids - pending_by_id.keys():
        raise InvalidWorkflowTransition("A seleção de documentos mudou. Atualize a análise.")
    for document_id in selected_ids:
        try:
            review_document(
                actor=actor,
                document=pending_by_id[document_id],
                decision=InstructorDocument.Status.APPROVED,
                reason="ADMIN_APPROVED_WITH_VERIFICATION",
                source=source,
            )
        except (DocumentPermissionDenied, DocumentValidationError) as exc:
            raise InvalidWorkflowTransition(str(exc)) from exc
    item.verification_method = method
    item.verification_source = source
    item.checked_at = timezone.now()
    item.internal_notes = notes.strip()
    item.save(
        update_fields=[
            "verification_method",
            "verification_source",
            "checked_at",
            "internal_notes",
            "updated_at",
        ]
    )
    _audit(actor, "review_metadata_updated", item, "ADMIN_CONSULTATION_CONFIRMED", request_id)
    return approve_verification_request(
        actor=actor, verification_request=item, request_id=request_id
    )


@transaction.atomic
def approve_verification_request(*, actor, verification_request, request_id=None):
    item = _lock_for_decision(actor, verification_request)
    if item.previous_verified_request_id and (
        not item.documents.exists()
        or item.documents.exclude(
            scan_status=InstructorDocument.ScanStatus.CLEAN,
            status=InstructorDocument.Status.APPROVED,
        ).exists()
    ):
        raise InvalidWorkflowTransition(
            "Todos os documentos complementares precisam de aprovação individual."
        )
    if item.documents.filter(
        status__in=[InstructorDocument.Status.PENDING, InstructorDocument.Status.UNDER_REVIEW]
    ).exists():
        raise InvalidWorkflowTransition("Revise individualmente os documentos anexados.")
    for requirement in item.requirements_snapshot:
        if (
            requirement["required"]
            and not item.documents.filter(
                requirement_id=requirement["id"],
                scan_status=InstructorDocument.ScanStatus.CLEAN,
                status=InstructorDocument.Status.APPROVED,
            ).exists()
        ):
            raise InvalidWorkflowTransition("Documento obrigatório ainda não foi aprovado.")
    if (
        not item.verification_method.strip()
        or not item.verification_source.strip()
        or not item.checked_at
    ):
        raise InvalidWorkflowTransition("Método, fonte e data da consulta são obrigatórios.")
    if len(item.verification_method.strip()) > 40 or len(item.verification_source.strip()) > 80:
        raise InvalidWorkflowTransition("Método ou fonte excede o limite da evidência.")
    now = timezone.now()
    item.status = item.Status.VERIFIED
    item.decided_at = now
    item.decision_by = actor
    item.public_message = "Verificação profissional concluída."
    with allow_critical_state_mutation():
        item.save(
            update_fields=["status", "decided_at", "decision_by", "public_message", "updated_at"]
        )
    profile = _advance_profile(
        actor=actor,
        item=item,
        target=InstructorProfile.Status.UNDER_REVIEW,
        allowed={InstructorProfile.Status.DRAFT, InstructorProfile.Status.SUBMITTED},
        reason="ADMIN_VERIFICATION_APPROVED_PENDING_PUBLICATION",
        request_id=request_id,
    )
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
def reject_verification_request(*, actor, verification_request, reason_code=None, request_id=None):
    item = _lock_for_decision(actor, verification_request)
    if reason_code is not None:
        item.rejection_reason_code = reason_code.strip()
    if not item.rejection_reason_code.strip():
        raise InvalidWorkflowTransition("O motivo estruturado da rejeição é obrigatório.")
    item.status = item.Status.REJECTED
    item.decided_at = timezone.now()
    item.decision_by = actor
    item.public_message = SAFE_REJECTION_MESSAGE
    with allow_critical_state_mutation():
        item.save(
            update_fields=[
                "status",
                "rejection_reason_code",
                "decided_at",
                "decision_by",
                "public_message",
                "updated_at",
            ]
        )
    profile = _advance_profile(
        actor=actor,
        item=item,
        target=InstructorProfile.Status.REJECTED,
        allowed={
            InstructorProfile.Status.DRAFT,
            InstructorProfile.Status.SUBMITTED,
            InstructorProfile.Status.UNDER_REVIEW,
        },
        reason="ADMIN_VERIFICATION_REJECTED",
        request_id=request_id,
    )
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
