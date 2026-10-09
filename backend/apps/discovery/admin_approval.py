"""One-screen administrative orchestration; domain decisions remain in services."""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.capabilities import enabled
from apps.marketplace.models import DataMode, InstructorDocument, InstructorOffer
from apps.territories.models import RegulatoryReadiness
from apps.territories.policies import (
    INSTRUCTOR_PROVIDER_TYPE,
    INSTRUCTOR_PUBLICATION_CAPABILITY,
    instructor_publication_is_allowed,
)
from apps.territories.services import approve_instructor_publication_uf

from .models import InstructorProfile, InstructorServiceArea, ProfessionalVerificationRequest
from .selectors import published_instructor_profiles
from .services import InvalidWorkflowTransition, approve_publication, can_manage_publication
from .verification_services import (
    can_review,
    record_review_and_approve,
    reject_verification_request,
    start_verification_review,
)

CATEGORIES = frozenset("ABCDE")


def _area(profile):
    try:
        return profile.service_area
    except InstructorServiceArea.DoesNotExist:
        return None


def _readiness(area):
    if not area:
        return None
    return (
        RegulatoryReadiness.objects.select_related("federative_unit")
        .filter(
            federative_unit__code=area.uf,
            provider_type=INSTRUCTOR_PROVIDER_TYPE,
            capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        )
        .first()
    )


def regulatory_evidence_missing(item):
    if item is None:
        return ["Análise regulatória da UF não cadastrada"]
    labels = {
        "source_url": "link da fonte oficial",
        "source_reference": "norma/referência",
        "source_authority": "órgão responsável",
        "source_consulted_at": "data da consulta",
        "evidence": "evidências",
        "notes": "observações",
    }
    missing = [label for field, label in labels.items() if not getattr(item, field)]
    if item.source_consulted_at and item.source_consulted_at > timezone.localdate():
        missing.append("data da consulta válida")
    return missing


def approval_panel(profile, actor):
    area = _area(profile)
    readiness = _readiness(area)
    verification = profile.verification_requests.order_by("-created_at", "-pk").first()
    offers = list(profile.offers.filter(data_mode=DataMode.REAL).order_by("category", "created_at"))
    active_categories = {
        offer.category
        for offer in offers
        if offer.is_active and offer.category in profile.categories
    }
    contact = getattr(profile, "contact_channel", None)
    contact_ok = bool(
        contact
        and contact.is_active
        and contact.data_mode == DataMode.REAL
        and enabled("REAL_WHATSAPP_CONTACT")
    )
    registration_ok = bool(
        profile.person.account.is_active
        and profile.person.account.lifecycle_status == "ACTIVE"
        and profile.person.role_assignments.filter(
            role="INSTRUCTOR", revoked_at__isnull=True
        ).exists()
    )
    uf_ok = bool(area and instructor_publication_is_allowed(area.uf))
    verification_ok = bool(
        verification
        and verification.status == ProfessionalVerificationRequest.Status.VERIFIED
        and profile.verification_status == InstructorProfile.VerificationStatus.VERIFIED
        and (not profile.verified_until or profile.verified_until > timezone.now())
    )
    documents = list(verification.documents.select_related("requirement")) if verification else []
    documents_ok = all(
        document.scan_status == InstructorDocument.ScanStatus.CLEAN
        and document.status == InstructorDocument.Status.APPROVED
        for document in documents
    )
    area_ok = bool(area and area.location_authorized and area.public_service_location)
    blockers = []
    if not registration_ok:
        blockers.append("Cadastro/conta ou papel de instrutor incompleto")
    if not documents_ok:
        blockers.append("Documentos sem scanner limpo ou revisão individual")
    if not verification_ok:
        blockers.append("Verificação profissional ainda não aprovada")
    if not uf_ok:
        blockers.append(
            f"UF {area.uf if area else 'não informada'} sem aprovação regulatória vigente"
        )
    if not area_ok:
        blockers.append("Área pública de atendimento não autorizada ou sem localização")
    if not active_categories:
        blockers.append("Nenhuma oferta real ativa para categoria cadastrada")
    if not contact_ok:
        blockers.append("WhatsApp profissional não configurado/ativo")
    if not enabled("REAL_MARKETPLACE_SEARCH"):
        blockers.append("REAL_MARKETPLACE_SEARCH desativada")
    if (
        profile.verification_requests.filter(
            status__in=["DRAFT", "SUBMITTED", "UNDER_REVIEW"]
        ).exists()
        and verification_ok
    ):
        blockers.append("Existe solicitação de verificação ativa")
    if profile.publication_status != InstructorProfile.PublicationStatus.APPROVED and (
        profile.profile_status != InstructorProfile.Status.UNDER_REVIEW
    ):
        blockers.append("Perfil não está em revisão para publicação")
    pending_documents = [
        document
        for document in documents
        if document.scan_status == InstructorDocument.ScanStatus.CLEAN
        and document.status
        in {InstructorDocument.Status.PENDING, InstructorDocument.Status.UNDER_REVIEW}
    ]
    return {
        "profile": profile,
        "area": area,
        "readiness": readiness,
        "regulatory_missing": regulatory_evidence_missing(readiness),
        "verification": verification,
        "documents": documents,
        "pending_documents": pending_documents,
        "offers": offers,
        "category_rows": [
            (category, category in profile.categories, category in active_categories)
            for category in "ABCDE"
        ],
        "active_categories": sorted(active_categories),
        "contact_ok": contact_ok,
        "registration_ok": registration_ok,
        "documents_ok": documents_ok,
        "verification_ok": verification_ok,
        "uf_ok": uf_ok,
        "area_ok": area_ok,
        "blockers": blockers,
        "ready_to_publish": not blockers and profile.publication_status != "APPROVED",
        "public": published_instructor_profiles().filter(pk=profile.pk).exists(),
        "can_review": can_review(actor),
        "can_decide_verification": bool(
            verification
            and verification.status == ProfessionalVerificationRequest.Status.UNDER_REVIEW
            and verification.reviewer_id == actor.id
            and can_review(actor)
        ),
        "can_publish": can_manage_publication(actor),
        "can_regulatory": actor.has_perm("territories.change_regulatoryreadiness"),
        "can_offer": actor.has_perm("marketplace.change_instructoroffer"),
        "responsible": actor.username
        == getattr(settings, "REGULATORY_RESPONSIBLE_ADMIN", "gilmar"),
    }


def _require_confirmation(data, name, message):
    if data.get(name) != "on":
        raise InvalidWorkflowTransition(message)


def _approve_uf(actor, panel, data):
    _require_confirmation(data, "confirm_uf", "Confirme pessoalmente a fonte e a vigência da UF.")
    item = panel["readiness"]
    if item is None or item.status != RegulatoryReadiness.Status.REVIEW_REQUIRED:
        raise InvalidWorkflowTransition("A UF não está pendente de revisão.")
    missing = regulatory_evidence_missing(item)
    if missing:
        raise InvalidWorkflowTransition("Faltam evidências da UF: " + ", ".join(missing))
    try:
        valid_from = date.fromisoformat(data.get("valid_from", ""))
    except ValueError as exc:
        raise InvalidWorkflowTransition("Informe a data de início de vigência confirmada.") from exc
    approve_instructor_publication_uf(
        actor=actor,
        readiness_id=item.pk,
        valid_from=valid_from,
        reason=data.get("uf_reason", "").strip(),
    )


def _verify(actor, panel, data, request_id):
    _require_confirmation(
        data, "confirm_verification", "Confirme pessoalmente a consulta profissional."
    )
    item = panel["verification"]
    if item is None:
        raise InvalidWorkflowTransition("Não existe solicitação profissional para analisar.")
    if item.status != item.Status.UNDER_REVIEW:
        raise InvalidWorkflowTransition("A solicitação não está pronta para análise.")
    record_review_and_approve(
        actor=actor,
        verification_request=item,
        method=data.get("verification_method", ""),
        source=data.get("verification_source", ""),
        notes=data.get("verification_notes", ""),
        consultation_confirmed=True,
        reviewed_document_ids=data.getlist("reviewed_document_ids"),
        request_id=request_id,
    )


def _publish(actor, profile, data, request_id):
    _require_confirmation(data, "confirm_publish", "Confirme pessoalmente a publicação do perfil.")
    profile.refresh_from_db()
    panel = approval_panel(profile, actor)
    if panel["blockers"]:
        raise InvalidWorkflowTransition("Publicação bloqueada: " + "; ".join(panel["blockers"]))
    if profile.profile_status != InstructorProfile.Status.UNDER_REVIEW:
        raise InvalidWorkflowTransition("Perfil não está em revisão para publicação.")
    reason = data.get("publication_reason", "").strip()
    record = approve_publication(actor=actor, profile=profile, reason=reason, request_id=request_id)
    if not published_instructor_profiles().filter(pk=profile.pk).exists():
        raise InvalidWorkflowTransition("Perfil não ficou visível na busca; publicação revertida.")
    return record


def _save_offer(actor, profile, data):
    if not actor.has_perm("marketplace.change_instructoroffer"):
        raise PermissionDenied("Permissão para gerenciar ofertas obrigatória.")
    category = data.get("offer_category", "").upper().strip()
    if category not in CATEGORIES or category not in profile.categories:
        raise InvalidWorkflowTransition("Escolha uma categoria cadastrada no perfil.")
    try:
        price = Decimal(data.get("offer_price", ""))
        duration = int(data.get("offer_duration", ""))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise InvalidWorkflowTransition("Informe preço e duração válidos para a oferta.") from exc
    if not price.is_finite() or price <= 0 or duration <= 0:
        raise InvalidWorkflowTransition("Preço e duração devem ser positivos.")
    reason = data.get("offer_reason", "").strip()
    if not reason:
        raise InvalidWorkflowTransition("Informe a justificativa da oferta.")
    offer = (
        InstructorOffer.objects.select_for_update()
        .filter(instructor=profile, category=category, data_mode=DataMode.REAL)
        .order_by("-is_active", "-created_at")
        .first()
    )
    created = offer is None
    if created:
        offer = InstructorOffer(instructor=profile, category=category, data_mode=DataMode.REAL)
    offer.price_amount = price
    offer.duration_minutes = duration
    offer.is_active = data.get("offer_active") == "on"
    offer.full_clean()
    offer.save()
    AuditEvent.objects.create(
        actor=actor,
        action="discovery.instructor_offer.admin_saved",
        target_type="marketplace.InstructorOffer",
        target_id=offer.pk,
        reason_code="ADMIN_EXPLICIT_OFFER",
        metadata={
            "category": category,
            "created": created,
            "active": offer.is_active,
            "reason": reason[:500],
        },
    )


@transaction.atomic
def execute_approval_action(*, actor, profile, data, request_id=None):
    """Explicit human decisions in one transaction; no partial approval on failure."""
    if (
        not actor.is_authenticated
        or not actor.can_operate
        or actor.username != getattr(settings, "REGULATORY_RESPONSIBLE_ADMIN", "gilmar")
    ):
        raise PermissionDenied("Somente o administrador responsável pode usar este painel.")
    profile = InstructorProfile.objects.select_for_update().get(pk=profile.pk)
    if profile.is_demo:
        raise InvalidWorkflowTransition("Este fluxo é somente para instrutores reais.")
    operation = data.get("operation")
    panel = approval_panel(profile, actor)
    if operation in {"approve_uf", "approve_publish"} and data.get("confirm_uf") == "on":
        _approve_uf(actor, panel, data)
    elif operation == "approve_uf":
        _approve_uf(actor, panel, data)
    if (
        operation in {"approve_verification", "approve_publish"}
        and data.get("confirm_verification") == "on"
    ):
        _verify(actor, panel, data, request_id)
    elif operation == "approve_verification":
        _verify(actor, panel, data, request_id)
    if operation == "start_review":
        if panel["verification"] is None:
            raise InvalidWorkflowTransition("Solicitação de verificação inexistente.")
        start_verification_review(
            actor=actor, verification_request=panel["verification"], request_id=request_id
        )
    elif operation == "reject_verification":
        if panel["verification"] is None:
            raise InvalidWorkflowTransition("Solicitação de verificação inexistente.")
        reject_verification_request(
            actor=actor,
            verification_request=panel["verification"],
            reason_code=data.get("rejection_reason_code", ""),
            request_id=request_id,
        )
    elif operation == "save_offer":
        _save_offer(actor, profile, data)
    elif operation in {"publish", "approve_publish"}:
        return _publish(actor, profile, data, request_id)
    elif operation not in {"approve_uf", "approve_verification"}:
        raise InvalidWorkflowTransition("Ação administrativa inválida.")
    return None
