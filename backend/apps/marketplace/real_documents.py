"""Private, fail-closed ingestion of professional verification evidence."""

import hashlib
import socket
import struct
from pathlib import Path
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorServiceArea, ProfessionalVerificationRequest

from .capabilities import enabled
from .models import DataMode, DocumentRequirement, InstructorDocument


class DocumentUploadError(ValueError):
    pass


ALLOWED_FORMATS = {
    ".pdf": ("application/pdf", b"%PDF-"),
    ".png": ("image/png", b"\x89PNG\r\n\x1a\n"),
    ".jpg": ("image/jpeg", b"\xff\xd8\xff"),
    ".jpeg": ("image/jpeg", b"\xff\xd8\xff"),
}


def upload_available():
    root = Path(settings.MEDIA_ROOT).resolve()
    base = Path(settings.BASE_DIR).resolve()
    return bool(
        enabled("REAL_DOCUMENT_UPLOADS")
        and getattr(settings, "PROFESSIONAL_DOCUMENT_UPLOAD_MODE", "DISABLED") == "PRODUCTION"
        and getattr(settings, "REAL_DOCUMENT_UPLOAD_ENABLED", False)
        and getattr(settings, "CLAMD_HOST", "")
        and root != base
        and not root.is_relative_to(base / "staticfiles")
    )


def applicable_requirements(profile):
    try:
        uf = profile.service_area.uf
    except InstructorServiceArea.DoesNotExist:
        return DocumentRequirement.objects.none()
    today = timezone.localdate()
    return DocumentRequirement.objects.filter(
        provider_type="INSTRUCTOR",
        uf=uf,
        category__in=profile.categories,
        active_from__lte=today,
        approval_recorded_at__isnull=False,
    ).filter(Q(active_until__isnull=True) | Q(active_until__gte=today))


def inspect_real_upload(upload):
    name = upload.name
    if not name or name != Path(name).name or "\\" in name or any(ord(c) < 32 for c in name):
        raise DocumentUploadError("Nome de arquivo inválido.")
    if len(name) > 180 or name.count(".") != 1:
        raise DocumentUploadError("Use um nome simples com uma única extensão.")
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_FORMATS:
        raise DocumentUploadError("Formato não permitido. Envie PDF, JPEG ou PNG.")
    max_bytes = settings.INSTRUCTOR_DOCUMENT_MAX_BYTES
    if upload.size <= 0 or upload.size > max_bytes:
        raise DocumentUploadError("O arquivo excede o tamanho permitido.")
    mime, signature = ALLOWED_FORMATS[suffix]
    if upload.content_type != mime:
        raise DocumentUploadError("O tipo declarado não corresponde ao arquivo.")
    header = upload.read(16)
    upload.seek(0)
    if not header.startswith(signature):
        raise DocumentUploadError("O conteúdo não corresponde ao formato informado.")
    digest = hashlib.sha256()
    for chunk in upload.chunks():
        digest.update(chunk)
    upload.seek(0)
    return {"original_name": name, "mime_type": mime, "sha256": digest.hexdigest()}


def scan_with_clamd(file):
    """Return CLEAN/BLOCKED. Scanner errors raise and never release the file."""
    host = getattr(settings, "CLAMD_HOST", "")
    if not host:
        raise DocumentUploadError("Análise antimalware indisponível.")
    try:
        with socket.create_connection(
            (host, int(getattr(settings, "CLAMD_PORT", 3310))), timeout=5
        ) as connection:
            connection.settimeout(30)
            connection.sendall(b"zINSTREAM\0")
            for chunk in file.chunks():
                connection.sendall(struct.pack("!I", len(chunk)) + chunk)
            connection.sendall(struct.pack("!I", 0))
            response_bytes = bytearray()
            while len(response_bytes) < 4096:
                part = connection.recv(4096 - len(response_bytes))
                if not part:
                    break
                response_bytes.extend(part)
                if b"\0" in part:
                    break
            response = response_bytes.decode("utf-8", errors="replace")
    except (OSError, TimeoutError, ValueError) as exc:
        raise DocumentUploadError("Análise antimalware indisponível.") from exc
    finally:
        file.seek(0)
    if response.endswith(" OK\0") or response.endswith(" OK\n"):
        return InstructorDocument.ScanStatus.CLEAN
    if " FOUND" in response:
        return InstructorDocument.ScanStatus.BLOCKED
    raise DocumentUploadError("Análise antimalware inconclusiva.")


def _audit(actor, document, action, request_id=None):
    try:
        rid = UUID(str(request_id)) if request_id else None
    except (TypeError, ValueError):
        rid = None
    AuditEvent.objects.create(
        actor=actor,
        action=f"marketplace.professional_document.{action}",
        target_type="marketplace.InstructorDocument",
        target_id=document.pk,
        request_id=rid,
        metadata={"verification_request_id": str(document.verification_request_id)},
    )


def upload_professional_document(
    *, actor, verification_request, requirement, upload, request_id=None
):
    if not upload_available():
        raise DocumentUploadError("Envio de documentos indisponível.")
    metadata = inspect_real_upload(upload)
    with transaction.atomic():
        item = (
            ProfessionalVerificationRequest.objects.select_for_update()
            .select_related("profile__person__account")
            .get(pk=verification_request.pk)
        )
        if actor != item.profile.person.account or item.status != item.Status.DRAFT:
            raise DocumentUploadError("Somente o titular pode enviar durante o rascunho.")
        if not applicable_requirements(item.profile).filter(pk=requirement.pk).exists():
            raise DocumentUploadError("Documento não solicitado para esta configuração.")
        if item.documents.filter(requirement=requirement).exists():
            raise DocumentUploadError("Remova o documento anterior antes de substituí-lo.")
        document = InstructorDocument.objects.create(
            instructor=item.profile,
            verification_request=item,
            requirement=requirement,
            file=upload,
            size_bytes=upload.size,
            data_mode=DataMode.REAL,
            **metadata,
        )
        _audit(actor, document, "uploaded", request_id)
        _audit(None, document, "scan_started", request_id)
    try:
        result = scan_with_clamd(document.file)
    except (DocumentUploadError, OSError):
        return document  # Quarantine is retained; submit remains blocked.
    with transaction.atomic():
        ProfessionalVerificationRequest.objects.select_for_update().get(pk=item.pk)
        try:
            locked = InstructorDocument.objects.select_for_update().get(pk=document.pk)
        except InstructorDocument.DoesNotExist:
            return document  # Owner removed this draft while scan was running.
        if locked.scan_status != locked.ScanStatus.PENDING:
            return locked
        old_key = locked.file.name
        if result == locked.ScanStatus.CLEAN:
            target = (
                f"professional-documents/{locked.verification_request_id}/"
                f"{locked.id}{Path(old_key).suffix}"
            )
            try:
                with locked.file.open("rb") as source:
                    new_key = locked.file.storage.save(target, source)
            except (OSError, ValueError):
                return locked  # Promotion failure never marks the file clean.
            locked.file.name = new_key
        locked.scan_status = result
        locked.scanned_at = timezone.now()
        locked.save(update_fields=["file", "scan_status", "scanned_at"])
        _audit(None, locked, "scan_clean" if result == locked.ScanStatus.CLEAN else "scan_blocked")
        transaction.on_commit(lambda: locked.file.storage.delete(old_key))
        return locked


def remove_draft_document(*, actor, document, request_id=None):
    with transaction.atomic():
        if document.verification_request_id is None:
            raise DocumentUploadError("Documento não pode ser removido nesta etapa.")
        item = ProfessionalVerificationRequest.objects.select_for_update().get(
            pk=document.verification_request_id
        )
        locked = InstructorDocument.objects.select_for_update().get(pk=document.pk)
        if (
            locked.verification_request_id != item.pk
            or item.status != item.Status.DRAFT
            or actor != item.profile.person.account
            or locked.data_mode != DataMode.REAL
        ):
            raise DocumentUploadError("Documento não pode ser removido nesta etapa.")
        _audit(actor, locked, "removed", request_id)
        storage, key = locked.file.storage, locked.file.name
        locked.delete()
        transaction.on_commit(lambda: storage.delete(key))
