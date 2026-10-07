"""Private, reviewed profile photographs for real instructors."""

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import DataMode, ProfilePhoto
from .real_documents import (
    DocumentUploadError,
    inspect_real_upload,
    scan_with_clamd,
    upload_available,
)

PHOTO_NOTICE_VERSION = "INSTRUCTOR-PROFILE-PHOTO-1"


def photo_upload_available():
    return upload_available()


def photo_status(profile):
    latest = profile.profile_photos.filter(data_mode=DataMode.REAL).order_by("-uploaded_at").first()
    return {
        "upload_available": photo_upload_available(),
        "latest_status": latest.status if latest else None,
        "latest_photo_id": str(latest.id) if latest else None,
        "private_preview_url": (
            f"/api/v1/marketplace/profile-photos/{latest.id}/download/" if latest else None
        ),
        "notice_version": PHOTO_NOTICE_VERSION,
    }


def upload_real_profile_photo(*, actor, profile, upload, publication_authorized, request_id=None):
    if not photo_upload_available():
        raise DocumentUploadError("Envio de foto indisponível.")
    if actor != profile.person.account or profile.is_demo:
        raise DocumentUploadError("Somente o titular pode enviar a própria foto.")
    if not publication_authorized:
        raise DocumentUploadError("Autorize separadamente o uso público da foto.")
    if upload.size > min(settings.INSTRUCTOR_DOCUMENT_MAX_BYTES, 5 * 1024 * 1024):
        raise DocumentUploadError("A foto deve ter no máximo 5 MB.")
    metadata = inspect_real_upload(upload)
    if metadata["mime_type"] not in {"image/png", "image/jpeg"}:
        raise DocumentUploadError("A foto deve ser JPEG ou PNG.")
    try:
        scan_result = scan_with_clamd(upload)
    except (DocumentUploadError, OSError) as exc:
        raise DocumentUploadError("Análise antimalware indisponível.") from exc
    if scan_result != "CLEAN":
        raise DocumentUploadError("A foto não passou na análise de segurança.")
    with transaction.atomic():
        locked = type(profile).objects.select_for_update().get(pk=profile.pk)
        if locked.profile_photos.filter(
            data_mode=DataMode.REAL, status=ProfilePhoto.Status.PENDING
        ).exists():
            raise DocumentUploadError("Já existe uma foto aguardando revisão.")
        photo = ProfilePhoto.objects.create(
            instructor=locked,
            file=upload,
            size_bytes=upload.size,
            data_mode=DataMode.REAL,
            publication_authorized_at=timezone.now(),
            publication_notice_version=PHOTO_NOTICE_VERSION,
            **metadata,
        )
        AuditEvent.objects.create(
            actor=actor,
            action="marketplace.profile_photo.uploaded",
            target_type="ProfilePhoto",
            target_id=photo.id,
            request_id=request_id,
            metadata={"data_mode": DataMode.REAL, "notice_version": PHOTO_NOTICE_VERSION},
        )
    return photo
