from datetime import timedelta
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.capabilities import enabled

from .models import (
    InstructorProfile,
    InstructorServiceArea,
    LocationPublicationAuthorization,
    ProfessionalVerification,
    PublicationDecision,
    allow_critical_state_mutation,
)


class WorkflowPermissionDenied(PermissionError):
    pass


class InvalidWorkflowTransition(ValueError):
    pass


PublicationPermissionDenied = WorkflowPermissionDenied
PublicationPreconditionError = InvalidWorkflowTransition


def can_manage_publication(actor):
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and (
            actor.user_permissions.filter(
                content_type__app_label="discovery", codename="manage_instructor_publication"
            ).exists()
            or actor.groups.filter(
                permissions__content_type__app_label="discovery",
                permissions__codename="manage_instructor_publication",
            ).exists()
        )
    )


def _rid(value):
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def _audit(actor, action, profile, before, after, reason, request_id=None, **extra):
    return AuditEvent.objects.create(
        actor=actor,
        action=f"discovery.{action}",
        target_type="discovery.InstructorProfile",
        target_id=profile.id,
        request_id=_rid(request_id),
        reason_code=reason,
        metadata={"before": before, "after": after, **extra},
    )


def _manager(actor):
    if not can_manage_publication(actor):
        raise WorkflowPermissionDenied(
            "Permissão explícita para o workflow profissional é obrigatória"
        )


def _save(instance, fields):
    with allow_critical_state_mutation():
        instance.save(update_fields=fields)


@transaction.atomic
def invalidate_after_owner_sensitive_edit(*, actor, profile, changed_fields, request_id=None):
    """Fail closed when owner edits data used by verification/publication."""
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if actor != p.person.account:
        raise WorkflowPermissionDenied("Somente a própria conta pode alterar o perfil")
    before = {
        "profile_status": p.profile_status,
        "verification_status": p.verification_status,
        "publication_status": p.publication_status,
    }
    p.profile_status = InstructorProfile.Status.UNDER_REVIEW
    p.verification_status = InstructorProfile.VerificationStatus.PENDING
    p.verified_until = None
    p.publication_status = InstructorProfile.PublicationStatus.UNPUBLISHED
    _save(
        p,
        ["profile_status", "verification_status", "verified_until", "publication_status"],
    )
    ProfessionalVerification.objects.create(
        profile=p,
        provider="OWNER_EDIT",
        status=ProfessionalVerification.Status.PENDING,
        actor=actor,
        reason="OWNER_SENSITIVE_DATA_CHANGED",
    )
    if before["publication_status"] != p.publication_status:
        PublicationDecision.objects.create(
            profile=p,
            decision=PublicationDecision.Decision.UNPUBLISH,
            actor=actor,
            reason="OWNER_SENSITIVE_DATA_CHANGED",
            before=before,
            after={
                "profile_status": p.profile_status,
                "verification_status": p.verification_status,
                "publication_status": p.publication_status,
            },
        )
    _audit(
        actor,
        "owner_sensitive_edit_invalidated",
        p,
        before,
        {
            "profile_status": p.profile_status,
            "verification_status": p.verification_status,
            "publication_status": p.publication_status,
        },
        "OWNER_SENSITIVE_DATA_CHANGED",
        request_id,
        changed_fields=sorted(changed_fields),
    )
    return p


@transaction.atomic
def submit_profile(*, actor, profile, reason="DEMO_ONBOARDING_SUBMISSION", request_id=None):
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if actor != p.person.account:
        raise WorkflowPermissionDenied("Somente a própria conta pode enviar o perfil")
    if not p.is_demo and not enabled("REAL_INSTRUCTOR_REGISTRATION"):
        raise WorkflowPermissionDenied("Onboarding real não está autorizado")
    if p.profile_status != "DRAFT":
        raise InvalidWorkflowTransition("Somente perfil em rascunho pode ser enviado")
    before = {"profile_status": p.profile_status}
    p.profile_status = "SUBMITTED"
    _save(p, ["profile_status"])
    _audit(
        actor,
        "profile_submitted",
        p,
        before,
        {"profile_status": p.profile_status},
        reason,
        request_id,
    )
    return p


@transaction.atomic
def start_review(*, actor, profile, reason="ADMIN_DEMO_REVIEW", request_id=None):
    _manager(actor)
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if p.profile_status != "SUBMITTED":
        raise InvalidWorkflowTransition("Somente perfil enviado pode iniciar revisão")
    before = {"profile_status": p.profile_status, "verification_status": p.verification_status}
    p.profile_status = "UNDER_REVIEW"
    p.verification_status = "PENDING"
    _save(p, ["profile_status", "verification_status"])
    _audit(
        actor,
        "profile_review_started",
        p,
        before,
        {"profile_status": p.profile_status, "verification_status": p.verification_status},
        reason,
        request_id,
    )
    return p


@transaction.atomic
def verify_professional(
    *,
    actor,
    profile,
    reason="ADMIN_DEMO_VERIFICATION",
    request_id=None,
    valid_days=30,
    authority="",
    method="",
    provenance_reference="",
):
    _manager(actor)
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if p.profile_status != "UNDER_REVIEW" or p.verification_status != "PENDING":
        raise InvalidWorkflowTransition("Verificação exige perfil em revisão e pendente")
    if not p.is_demo and (not authority.strip() or not method.strip()):
        raise InvalidWorkflowTransition(
            "Verificação real exige autoridade e método, sem anexar documento"
        )
    now = timezone.now()
    until = now + timedelta(days=valid_days)
    before = {"verification_status": p.verification_status, "verified_until": p.verified_until}
    p.verification_status = "VERIFIED"
    p.verified_until = until
    _save(p, ["verification_status", "verified_until"])
    record = ProfessionalVerification.objects.create(
        profile=p,
        provider="SYNTHETIC" if p.is_demo else "MANUAL_NO_FILE",
        authority=authority.strip(),
        method=method.strip(),
        provenance_reference=provenance_reference.strip(),
        status="VERIFIED",
        verified_at=now,
        verified_until=until,
        actor=actor,
        reason=reason,
    )
    _audit(
        actor,
        "verification_verified",
        p,
        before,
        {"verification_status": "VERIFIED", "verified_until": until.isoformat()},
        reason,
        request_id,
        verification_id=str(record.id),
        authority=record.authority,
        method=record.method,
        provenance_reference=record.provenance_reference,
    )
    return record


@transaction.atomic
def reject_verification(*, actor, profile, reason, request_id=None):
    _manager(actor)
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if p.profile_status != "UNDER_REVIEW" or p.verification_status != "PENDING":
        raise InvalidWorkflowTransition("Rejeição exige verificação pendente em revisão")
    before = {"profile_status": p.profile_status, "verification_status": p.verification_status}
    p.profile_status = "REJECTED"
    p.verification_status = "REJECTED"
    _save(p, ["profile_status", "verification_status"])
    record = ProfessionalVerification.objects.create(
        profile=p, provider="SYNTHETIC", status="REJECTED", actor=actor, reason=reason
    )
    _audit(
        actor,
        "verification_rejected",
        p,
        before,
        {"profile_status": "REJECTED", "verification_status": "REJECTED"},
        reason,
        request_id,
        verification_id=str(record.id),
    )
    return record


@transaction.atomic
def decide_publication(*, actor, profile, decision, reason, request_id=None):
    _manager(actor)
    if not reason:
        raise ValueError("Motivo obrigatório")
    p = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    before = {"profile_status": p.profile_status, "publication_status": p.publication_status}
    verification = p.verification_history.order_by("-created_at").first()
    if decision == "APPROVE":
        from apps.marketplace.documents import documents_satisfy_active_requirements

        verification_evidence_valid = bool(
            verification
            and verification.status == ProfessionalVerification.Status.VERIFIED
            and (
                p.is_demo
                or (
                    verification.provider == "MANUAL_NO_FILE"
                    and verification.authority
                    and verification.method
                )
            )
        )
        dossier_valid = documents_satisfy_active_requirements(p) if p.is_demo else True
        if (
            p.profile_status != "UNDER_REVIEW"
            or p.verification_status != "VERIFIED"
            or (p.verified_until and p.verified_until <= timezone.now())
            or not p.service_area.location_authorized
            or not verification_evidence_valid
            or not dossier_valid
        ):
            raise InvalidWorkflowTransition(
                "Revisão, verificação válida e localização autorizada são obrigatórias"
            )
        p.profile_status = "APPROVED"
        p.publication_status = "APPROVED"
    else:
        allowed = {
            "REJECT": ({"UNDER_REVIEW"}, "REJECTED", "REJECTED"),
            "SUSPEND": ({"APPROVED"}, "SUSPENDED", "SUSPENDED"),
            "UNPUBLISH": ({"APPROVED", "SUSPENDED"}, p.profile_status, "UNPUBLISHED"),
        }
        states, profile_state, publication_state = allowed[decision]
        if p.profile_status not in states:
            raise InvalidWorkflowTransition(
                f"Transição {decision} inválida para {p.profile_status}"
            )
        p.profile_status = profile_state
        p.publication_status = publication_state
    _save(p, ["profile_status", "publication_status"])
    after = {"profile_status": p.profile_status, "publication_status": p.publication_status}
    record = PublicationDecision.objects.create(
        profile=p,
        decision=decision,
        actor=actor,
        reason=reason,
        verification=verification,
        before=before,
        after=after,
    )
    _audit(
        actor,
        f"publication_{decision.lower()}",
        p,
        before,
        after,
        reason,
        request_id,
        decision_id=str(record.id),
    )
    return record


def approve_publication(**kwargs):
    return decide_publication(decision="APPROVE", **kwargs)


def reject_publication(**kwargs):
    return decide_publication(decision="REJECT", **kwargs)


def suspend_publication(**kwargs):
    return decide_publication(decision="SUSPEND", **kwargs)


def unpublish_professional(**kwargs):
    return decide_publication(decision="UNPUBLISH", **kwargs)


@transaction.atomic
def grant_service_location_authorization(
    *, actor, service_area, purpose, policy_version, reason, request_id=None
):
    a = (
        InstructorServiceArea.objects.select_for_update()
        .select_related("profile__person__account")
        .get(pk=service_area.pk)
    )
    if actor != a.profile.person.account and not can_manage_publication(actor):
        raise WorkflowPermissionDenied("Ator não autorizado para consentir com a localização")
    if a.location_authorized or a.authorization_history.filter(revoked_at__isnull=True).exists():
        raise InvalidWorkflowTransition("A localização já está autorizada")
    before = {
        "location_authorization": "NOT_GRANTED"
        if not a.authorization_history.exists()
        else "REVOKED"
    }
    a.location_authorized = True
    _save(a, ["location_authorized"])
    record = LocationPublicationAuthorization.objects.create(
        service_area=a,
        purpose=purpose,
        policy_version=policy_version,
        authorized_at=timezone.now(),
        actor=actor,
        reason=reason,
    )
    _audit(
        actor,
        "location_authorized",
        a.profile,
        before,
        {"location_authorization": "GRANTED"},
        reason,
        request_id,
        authorization_id=str(record.id),
        purpose=purpose,
        policy_version=policy_version,
    )
    return record


@transaction.atomic
def revoke_service_location_authorization(*, actor, service_area, reason, request_id=None):
    _manager(actor)
    a = (
        InstructorServiceArea.objects.select_for_update()
        .select_related("profile")
        .get(pk=service_area.pk)
    )
    current = (
        a.authorization_history.filter(revoked_at__isnull=True).order_by("-authorized_at").first()
    )
    if not a.location_authorized or not current:
        raise InvalidWorkflowTransition("Não existe autorização ativa para revogar")
    current.revoked_at = timezone.now()
    current.revoked_by = actor
    current.reason = reason
    current.save(update_fields=["revoked_at", "revoked_by", "reason"])
    a.location_authorized = False
    _save(a, ["location_authorized"])
    _audit(
        actor,
        "location_authorization_revoked",
        a.profile,
        {"location_authorization": "GRANTED"},
        {"location_authorization": "REVOKED"},
        reason,
        request_id,
        authorization_id=str(current.id),
    )
    return current
