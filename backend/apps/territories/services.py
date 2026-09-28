from django.conf import settings
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import RegulatoryReadiness
from .policies import INSTRUCTOR_PROVIDER_TYPE, INSTRUCTOR_PUBLICATION_CAPABILITY


@transaction.atomic
def approve_instructor_publication_uf(*, actor, readiness_id, valid_from, reason):
    """Record an explicit human decision for one UF; never approve a batch."""
    if not actor.is_authenticated or not actor.is_staff or not actor.can_operate:
        raise PermissionDenied("Revisor administrativo ativo obrigatório.")
    if actor.username != getattr(settings, "REGULATORY_RESPONSIBLE_ADMIN", "gilmar"):
        raise PermissionDenied("A confirmação cabe à conta administrativa responsável.")
    if not actor.has_perm("territories.change_regulatoryreadiness"):
        raise PermissionDenied("Permissão de revisão regulatória obrigatória.")
    item = RegulatoryReadiness.objects.select_for_update().get(pk=readiness_id)
    if (
        item.provider_type != INSTRUCTOR_PROVIDER_TYPE
        or item.capability != INSTRUCTOR_PUBLICATION_CAPABILITY
        or item.status != RegulatoryReadiness.Status.REVIEW_REQUIRED
    ):
        raise ValidationError(
            "Somente análise pendente de publicação de instrutor pode ser aprovada."
        )
    if not item.source_url or not item.source_reference or not item.notes:
        raise ValidationError("Fonte oficial, norma e observações são obrigatórias.")
    if not valid_from:
        raise ValidationError("Informe a data de início de vigência confirmada.")
    if item.valid_until and item.valid_until < valid_from:
        raise ValidationError("A vigência final precede a inicial.")
    if not reason.strip():
        raise ValidationError("Justificativa da decisão obrigatória.")
    now = timezone.now()
    item.valid_from = valid_from
    item.reviewed_by = actor
    item.reviewed_at = now
    item.approved_by = actor
    item.approved_at = now
    item.status = RegulatoryReadiness.Status.APPROVED
    item.save()
    AuditEvent.objects.create(
        actor=actor,
        action="territories.regulatory_readiness_approve",
        target_type="RegulatoryReadiness",
        target_id=item.id,
        reason_code="HUMAN_REVIEW",
        metadata={
            "uf": item.federative_unit.code,
            "provider_type": item.provider_type,
            "capability": item.capability,
            "source_reference": item.source_reference,
            "valid_from": valid_from.isoformat(),
            "reason": reason.strip()[:500],
        },
    )
    return item
