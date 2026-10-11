"""Transactional e-mail after a human professional-verification decision."""

import logging
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import InstructorProfile, ProfessionalVerificationRequest
from .publication_notifications import email_available

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
STALE_SENDING_AFTER = timedelta(minutes=30)


def queue_verification_approval_notice(request_id):
    """A broker outage must not undo a committed human approval."""
    try:
        from .tasks import deliver_verification_approval_notice_task

        deliver_verification_approval_notice_task.delay(str(request_id))
    except Exception:
        logger.exception("Could not enqueue verification notice for request %s", request_id)


def deliver_verification_approval_notice(request_id):
    if not email_available():
        return "EMAIL_UNAVAILABLE"

    with transaction.atomic():
        record = (
            ProfessionalVerificationRequest.objects.select_for_update()
            .select_related("profile__person__account")
            .get(pk=request_id)
        )
        if record.approval_notice_status == record.NoticeStatus.SENDING and (
            not record.approval_notice_attempted_at
            or record.approval_notice_attempted_at > timezone.now() - STALE_SENDING_AFTER
        ):
            return "IN_PROGRESS"
        if record.approval_notice_status not in {
            record.NoticeStatus.PENDING,
            record.NoticeStatus.SENDING,
        }:
            return record.approval_notice_status
        profile = record.profile
        latest_request_id = (
            ProfessionalVerificationRequest.objects.filter(profile=profile)
            .order_by("-created_at", "-pk")
            .values_list("pk", flat=True)
            .first()
        )
        if (
            record.status != record.Status.VERIFIED
            or profile.is_demo
            or profile.verification_status != InstructorProfile.VerificationStatus.VERIFIED
            or latest_request_id != record.pk
            or not record.approval_notice_recipient
        ):
            record.approval_notice_status = record.NoticeStatus.SKIPPED
            record.save(update_fields=["approval_notice_status"])
            return "SKIPPED"
        record.approval_notice_status = record.NoticeStatus.SENDING
        record.approval_notice_attempts += 1
        record.approval_notice_attempted_at = timezone.now()
        record.save(
            update_fields=[
                "approval_notice_status",
                "approval_notice_attempts",
                "approval_notice_attempted_at",
            ]
        )
        recipient = record.approval_notice_recipient

    try:
        sent = send_mail(
            "Sua verificação profissional foi aprovada — InstrutorProCNH",
            "Sua verificação profissional interna foi aprovada após análise. "
            "A publicação do seu perfil na busca é uma etapa separada e depende "
            "dos demais critérios da plataforma. Acompanhe a situação no seu painel: "
            f"{settings.FRONTEND_PUBLIC_URL}/profissional/instrutor/status\n\n"
            "Esta aprovação interna não é credenciamento ou autorização emitida "
            "por órgão de trânsito.",
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        if sent != 1:
            raise RuntimeError("EMAIL_NOT_ACCEPTED")
    except Exception:
        logger.exception("Verification notice delivery failed for request %s", request_id)
        with transaction.atomic():
            record = ProfessionalVerificationRequest.objects.select_for_update().get(pk=request_id)
            if record.approval_notice_status == record.NoticeStatus.SENDING:
                record.approval_notice_status = (
                    record.NoticeStatus.FAILED
                    if record.approval_notice_attempts >= MAX_ATTEMPTS
                    else record.NoticeStatus.PENDING
                )
                record.save(update_fields=["approval_notice_status"])
        return "DELIVERY_FAILED"

    with transaction.atomic():
        record = ProfessionalVerificationRequest.objects.select_for_update().get(pk=request_id)
        if record.approval_notice_status == record.NoticeStatus.SENDING:
            record.approval_notice_status = record.NoticeStatus.SENT
            record.approval_notice_sent_at = timezone.now()
            record.save(update_fields=["approval_notice_status", "approval_notice_sent_at"])
            AuditEvent.objects.create(
                action="discovery.verification_approval_notice.sent",
                target_type="discovery.ProfessionalVerificationRequest",
                target_id=record.pk,
                reason_code="TRANSACTIONAL_EMAIL",
                metadata={"channel": "EMAIL"},
            )
    return "SENT"


def due_verification_approval_notice_ids(limit=50):
    stale = timezone.now() - STALE_SENDING_AFTER
    return list(
        ProfessionalVerificationRequest.objects.filter(
            Q(approval_notice_status=ProfessionalVerificationRequest.NoticeStatus.PENDING)
            | Q(
                approval_notice_status=ProfessionalVerificationRequest.NoticeStatus.SENDING,
                approval_notice_attempted_at__lt=stale,
            )
        )
        .order_by("created_at")
        .values_list("pk", flat=True)[:limit]
    )
