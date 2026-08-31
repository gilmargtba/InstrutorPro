import hashlib
from pathlib import Path

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import DataMode, InstructorDocument, InstructorVehicle, ProfilePhoto


class DocumentValidationError(ValueError):
    pass


class DocumentPermissionDenied(PermissionError):
    pass


ALLOWED_TYPES = {
    ".pdf": ("application/pdf", (b"%PDF-",)),
    ".png": ("image/png", (b"\x89PNG\r\n\x1a\n",)),
    ".jpg": ("image/jpeg", (b"\xff\xd8\xff",)),
    ".jpeg": ("image/jpeg", (b"\xff\xd8\xff",)),
}


def inspect_document(upload, *, data_mode):
    name = Path(upload.name).name
    if name != upload.name or "/" in upload.name or "\\" in upload.name:
        raise DocumentValidationError("Nome de arquivo inválido")
    if data_mode == DataMode.REAL or not settings.REAL_DOCUMENT_UPLOAD_ENABLED:
        if data_mode != DataMode.SYNTHETIC:
            raise DocumentValidationError("Upload real permanece desabilitado")
    if not settings.SYNTHETIC_DOCUMENT_UPLOAD_ENABLED:
        raise DocumentValidationError("Upload de fixtures sintéticas está desabilitado")
    if not name.lower().startswith("fixture-"):
        raise DocumentValidationError(
            "Apenas arquivos sintéticos prefixados por fixture- são aceitos"
        )
    if upload.size <= 0 or upload.size > settings.INSTRUCTOR_DOCUMENT_MAX_BYTES:
        raise DocumentValidationError("Tamanho de arquivo inválido")
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise DocumentValidationError("Formato não permitido")
    header = upload.read(16)
    upload.seek(0)
    mime_type, signatures = ALLOWED_TYPES[suffix]
    if header.startswith((b"MZ", b"\x7fELF")) or not any(
        header.startswith(signature) for signature in signatures
    ):
        raise DocumentValidationError("Conteúdo do arquivo não corresponde ao formato permitido")
    digest = hashlib.sha256()
    for chunk in upload.chunks():
        digest.update(chunk)
    upload.seek(0)
    return {"original_name": name, "mime_type": mime_type, "sha256": digest.hexdigest()}


@transaction.atomic
def upload_synthetic_document(
    *,
    actor,
    instructor,
    requirement,
    upload,
    vehicle=None,
    credential_uf="",
    private_identifier="",
    issued_at=None,
    valid_until=None,
    supersedes=None,
):
    if actor != instructor.person.account:
        raise DocumentPermissionDenied("Somente o titular pode enviar o próprio documento")
    if (
        requirement.uf != instructor.service_area.uf
        or requirement.category not in instructor.categories
    ):
        raise DocumentValidationError("Requisito incompatível com território/categoria")
    if requirement.document_type == requirement.DocumentType.VEHICLE_EVIDENCE and not vehicle:
        raise DocumentValidationError("Documento de veículo exige veículo relacionado")
    metadata = inspect_document(upload, data_mode=DataMode.SYNTHETIC)
    if requirement.requires_validity and not valid_until:
        raise DocumentValidationError("Validade é obrigatória para este requisito")
    version = (supersedes.version + 1) if supersedes else 1
    document = InstructorDocument.objects.create(
        instructor=instructor,
        vehicle=vehicle,
        requirement=requirement,
        file=upload,
        size_bytes=upload.size,
        scan_status=InstructorDocument.ScanStatus.CLEAN,
        data_mode=DataMode.SYNTHETIC,
        credential_uf=credential_uf,
        private_identifier=private_identifier,
        issued_at=issued_at,
        valid_until=valid_until,
        supersedes=supersedes,
        version=version,
        **metadata,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.instructor_document.uploaded",
        target_type="InstructorDocument",
        target_id=document.id,
        metadata={
            "requirement_id": str(requirement.id),
            "version": version,
            "data_mode": DataMode.SYNTHETIC,
            "sha256": document.sha256,
        },
    )
    return document


def can_review_document(actor):
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and actor.has_perm("marketplace.review_instructor_document")
    )


@transaction.atomic
def review_document(*, actor, document, decision, reason, source):
    if not can_review_document(actor):
        raise DocumentPermissionDenied("Permissão explícita de revisão é obrigatória")
    locked = (
        InstructorDocument.objects.select_for_update()
        .select_related("instructor__person__account")
        .get(pk=document.pk)
    )
    if actor == locked.instructor.person.account:
        raise DocumentPermissionDenied("O titular não pode revisar o próprio documento")
    if locked.status not in {
        InstructorDocument.Status.PENDING,
        InstructorDocument.Status.UNDER_REVIEW,
    }:
        raise DocumentValidationError("Documento não está em estado revisável")
    if decision not in {InstructorDocument.Status.APPROVED, InstructorDocument.Status.REJECTED}:
        raise DocumentValidationError("Decisão inválida")
    if decision == InstructorDocument.Status.APPROVED:
        if locked.scan_status != InstructorDocument.ScanStatus.CLEAN:
            raise DocumentValidationError("Documento sem análise de conteúdo aprovada")
        if locked.valid_until and locked.valid_until < timezone.localdate():
            raise DocumentValidationError("Documento vencido não pode ser aprovado")
    before = locked.status
    locked.status = decision
    locked.reviewed_by = actor
    locked.reviewed_at = timezone.now()
    locked.review_reason = reason
    locked.review_source = source
    locked.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
            "review_reason",
            "review_source",
        ]
    )
    if locked.vehicle:
        locked.vehicle.verification_status = decision
        locked.vehicle.save(update_fields=["verification_status"])
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.instructor_document.reviewed",
        target_type="InstructorDocument",
        target_id=locked.id,
        reason_code=reason,
        metadata={
            "before": before,
            "after": decision,
            "version": locked.version,
            "source": source,
            "uf": locked.credential_uf or locked.requirement.uf,
        },
    )
    return locked


@transaction.atomic
def expire_documents(*, actor=None):
    today = timezone.localdate()
    documents = list(
        InstructorDocument.objects.select_for_update().filter(
            status=InstructorDocument.Status.APPROVED, valid_until__lt=today
        )
    )
    for document in documents:
        document.status = InstructorDocument.Status.EXPIRED
        document.save(update_fields=["status"])
        if document.vehicle:
            document.vehicle.verification_status = InstructorVehicle.VerificationStatus.EXPIRED
            document.vehicle.save(update_fields=["verification_status"])
        AuditEvent.objects.create(
            actor=actor,
            action="marketplace.instructor_document.expired",
            target_type="InstructorDocument",
            target_id=document.id,
            metadata={"valid_until": document.valid_until.isoformat()},
        )
    return len(documents)


@transaction.atomic
def upload_synthetic_profile_photo(
    *, actor, instructor, upload, publication_authorized, notice_version
):
    if actor != instructor.person.account:
        raise DocumentPermissionDenied("Somente o titular pode enviar a própria foto")
    if not publication_authorized or not notice_version:
        raise DocumentValidationError("Autorização e versão do notice são obrigatórias")
    metadata = inspect_document(upload, data_mode=DataMode.SYNTHETIC)
    if metadata["mime_type"] not in {"image/png", "image/jpeg"}:
        raise DocumentValidationError("Foto deve ser PNG ou JPEG")
    photo = ProfilePhoto.objects.create(
        instructor=instructor,
        file=upload,
        size_bytes=upload.size,
        publication_authorized_at=timezone.now(),
        publication_notice_version=notice_version,
        data_mode=DataMode.SYNTHETIC,
        **metadata,
    )
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.profile_photo.uploaded",
        target_type="ProfilePhoto",
        target_id=photo.id,
        metadata={
            "publication_authorized": True,
            "notice_version": notice_version,
            "data_mode": DataMode.SYNTHETIC,
        },
    )
    return photo


@transaction.atomic
def review_profile_photo(*, actor, photo, decision, reason):
    if not (
        actor
        and actor.is_authenticated
        and actor.can_operate
        and actor.has_perm("marketplace.review_profile_photo")
    ):
        raise DocumentPermissionDenied("Permissão explícita para revisar foto é obrigatória")
    locked = (
        ProfilePhoto.objects.select_for_update()
        .select_related("instructor__person__account")
        .get(pk=photo.pk)
    )
    if actor == locked.instructor.person.account:
        raise DocumentPermissionDenied("O titular não pode revisar a própria foto")
    if locked.status != ProfilePhoto.Status.PENDING:
        raise DocumentValidationError("Foto não está pendente")
    if decision not in {
        ProfilePhoto.Status.APPROVED,
        ProfilePhoto.Status.REJECTED,
        ProfilePhoto.Status.REPLACEMENT_REQUESTED,
    }:
        raise DocumentValidationError("Decisão de foto inválida")
    if decision == ProfilePhoto.Status.APPROVED and not locked.publication_authorized_at:
        raise DocumentValidationError("Foto sem autorização separada para publicação")
    before = locked.status
    locked.status = decision
    locked.reviewed_by = actor
    locked.reviewed_at = timezone.now()
    locked.review_reason = reason
    locked.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_reason"])
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.profile_photo.reviewed",
        target_type="ProfilePhoto",
        target_id=locked.id,
        reason_code=reason,
        metadata={"before": before, "after": decision},
    )
    return locked


def documents_satisfy_active_requirements(profile):
    today = timezone.localdate()
    requirements = (
        profile.documents.model._meta.get_field("requirement")
        .related_model.objects.filter(
            uf=profile.service_area.uf,
            category__in=profile.categories,
            provider_type="INSTRUCTOR",
            required=True,
            active_from__lte=today,
        )
        .filter(models.Q(active_until__isnull=True) | models.Q(active_until__gte=today))
    )
    for requirement in requirements:
        if (
            not profile.documents.filter(
                requirement=requirement,
                status=InstructorDocument.Status.APPROVED,
                scan_status=InstructorDocument.ScanStatus.CLEAN,
            )
            .filter(models.Q(valid_until__isnull=True) | models.Q(valid_until__gte=today))
            .exists()
        ):
            return False
    return True
