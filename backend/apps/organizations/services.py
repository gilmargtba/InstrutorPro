from __future__ import annotations

from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import PlatformOrganization
from .policies import can_manage_platform_organization, can_validate_platform_organization
from .validators import normalize_cnpj

EDITABLE_FIELDS = (
    "cnpj",
    "legal_name",
    "trade_name",
    "business_address",
    "legal_representative",
    "operational_contact",
    "privacy_contact",
    "phone",
    "dpo_name",
    "dpo_contact",
    "dpo_appointment_reference",
)


class OrganizationPermissionDenied(PermissionError):
    pass


class OrganizationVersionConflict(RuntimeError):
    pass


class OrganizationValidationError(ValueError):
    pass


def _request_id(value):
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def _snapshot(organization):
    return {
        "status": organization.validation_status,
        "version": organization.version,
        "cnpj": f"**********{organization.cnpj[-4:]}" if organization.cnpj else "",
        "legal_name": organization.legal_name,
        "trade_name": organization.trade_name,
        "business_address": "[REDACTED]" if organization.business_address else "",
        "legal_representative": "[REDACTED]" if organization.legal_representative else "",
        "operational_contact": "[REDACTED]" if organization.operational_contact else "",
        "privacy_contact": "[REDACTED]" if organization.privacy_contact else "",
        "phone": "[REDACTED]" if organization.phone else "",
        "dpo_name": "[REDACTED]" if organization.dpo_name else "",
        "dpo_contact": "[REDACTED]" if organization.dpo_contact else "",
        "dpo_appointment_reference": (
            "[REDACTED]" if organization.dpo_appointment_reference else ""
        ),
    }


def _audit(*, actor, organization, action, reason, before, after, request_id, changed_fields):
    AuditEvent.objects.create(
        actor=actor,
        action=action,
        target_type="organizations.PlatformOrganization",
        target_id=organization.id,
        request_id=_request_id(request_id),
        reason_code=reason,
        metadata={
            "changed_fields": sorted(changed_fields),
            "before": before,
            "after": after,
        },
    )


def _normalized_data(data):
    normalized = {field: str(data.get(field) or "").strip() for field in EDITABLE_FIELDS}
    normalized["cnpj"] = normalize_cnpj(normalized["cnpj"])
    return normalized


@transaction.atomic
def save_platform_organization(
    *, actor, data, expected_version, reason, request_id=None, organization=None
):
    if not can_manage_platform_organization(actor=actor):
        raise OrganizationPermissionDenied("Permissão explícita de configuração é obrigatória")
    values = _normalized_data(data)

    if organization is None:
        if PlatformOrganization.objects.exists():
            raise OrganizationVersionConflict("A organização controladora já foi criada")
        instance = PlatformOrganization(**values)
        instance.validation_status = (
            PlatformOrganization.ValidationStatus.PENDING_VALIDATION
            if instance.is_complete()
            else PlatformOrganization.ValidationStatus.INCOMPLETE
        )
        instance.full_clean()
        try:
            instance.save()
        except IntegrityError as exc:
            raise OrganizationVersionConflict("A organização controladora já foi criada") from exc
        _audit(
            actor=actor,
            organization=instance,
            action="organizations.platform_organization_created",
            reason=reason,
            before={"status": "ABSENT", "version": None},
            after=_snapshot(instance),
            request_id=request_id,
            changed_fields=EDITABLE_FIELDS,
        )
        return instance

    instance = PlatformOrganization.objects.select_for_update().get(pk=organization.pk)
    if instance.version != expected_version:
        raise OrganizationVersionConflict("A configuração foi alterada por outra sessão")
    before = _snapshot(instance)
    changed_fields = [field for field, value in values.items() if getattr(instance, field) != value]
    if not changed_fields:
        return instance
    for field, value in values.items():
        setattr(instance, field, value)
    instance.validation_status = (
        PlatformOrganization.ValidationStatus.PENDING_VALIDATION
        if instance.is_complete()
        else PlatformOrganization.ValidationStatus.INCOMPLETE
    )
    instance.validated_at = None
    instance.validated_by = None
    instance.version += 1
    instance.full_clean()
    instance.save(
        update_fields=[
            *EDITABLE_FIELDS,
            "validation_status",
            "validated_at",
            "validated_by",
            "version",
            "updated_at",
        ]
    )
    _audit(
        actor=actor,
        organization=instance,
        action="organizations.platform_organization_updated",
        reason=reason,
        before=before,
        after=_snapshot(instance),
        request_id=request_id,
        changed_fields=changed_fields,
    )
    return instance


@transaction.atomic
def validate_platform_organization(
    *, actor, organization, expected_version, reason, request_id=None
):
    if not can_validate_platform_organization(actor=actor):
        raise OrganizationPermissionDenied("Permissão explícita de validação é obrigatória")
    instance = PlatformOrganization.objects.select_for_update().get(pk=organization.pk)
    if instance.version != expected_version:
        raise OrganizationVersionConflict("A configuração foi alterada por outra sessão")
    if instance.validation_status == PlatformOrganization.ValidationStatus.VALIDATED:
        return instance
    if not instance.is_complete():
        raise OrganizationValidationError("Complete os campos obrigatórios antes de validar")
    before = _snapshot(instance)
    instance.validation_status = PlatformOrganization.ValidationStatus.VALIDATED
    instance.validated_at = timezone.now()
    instance.validated_by = actor
    instance.version += 1
    try:
        instance.full_clean()
    except ValidationError as exc:
        raise OrganizationValidationError(str(exc)) from exc
    instance.save(
        update_fields=[
            "validation_status",
            "validated_at",
            "validated_by",
            "version",
            "updated_at",
        ]
    )
    _audit(
        actor=actor,
        organization=instance,
        action="organizations.platform_organization_validated",
        reason=reason,
        before=before,
        after=_snapshot(instance),
        request_id=request_id,
        changed_fields=("validation_status", "validated_at", "validated_by"),
    )
    return instance
