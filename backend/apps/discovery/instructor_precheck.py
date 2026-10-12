"""Advisory, deterministic triage; never decides verification or publication."""

import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.marketplace.models import DataMode, InstructorDocument
from apps.people.identifiers import (
    ProtectedIdentifierConfigurationError,
    decrypt_identifier,
    normalize_cpf,
)

from .models import InstructorProfile, InstructorServiceArea, ProfessionalVerificationRequest

logger = logging.getLogger(__name__)

PRECHECK_MESSAGES = {
    "REGISTRATION_INCOMPLETE": "Complete os dados da conta e do perfil profissional.",
    "CPF_INVALID": "Informe um CPF válido na identificação privada.",
    "CPF_CHECK_UNAVAILABLE": "A conferência do CPF está temporariamente indisponível; aguarde.",
    "CNH_MISSING": "Anexe sua CNH selecionando o tipo de documento CNH.",
    "DOCUMENT_MISSING": "Anexe ao menos um documento profissional para análise.",
    "PROFESSIONAL_CREDENTIAL_MISSING": (
        "Anexe sua credencial ou certificado profissional para análise."
    ),
    "FILE_INVALID": "Substitua o arquivo inválido; use PDF, JPEG ou PNG de até 5 MB.",
    "FILE_SCAN_PENDING": "Aguarde a análise de segurança do arquivo.",
    "FILE_BLOCKED": "Remova o arquivo recusado e envie outro documento.",
    "CATEGORIES_MISSING": "Selecione ao menos uma categoria que você atende.",
    "OFFER_MISSING": "Cadastre uma oferta ativa para uma das categorias selecionadas.",
    "LOCATION_MISSING": "Informe município e UF de atendimento.",
    "SERVICE_AREA_MISSING": "Autorize a área pública aproximada de atendimento no mapa.",
    "WHATSAPP_MISSING": "Informe seu WhatsApp profissional.",
}


class InstructorValidationService:
    @staticmethod
    def issues(item):
        profile = InstructorProfile.objects.select_related("person__account").get(
            pk=item.profile_id
        )
        person = profile.person
        account = person.account
        issues = []
        if (
            not profile.display_name.strip()
            or not account.is_active
            or account.lifecycle_status != "ACTIVE"
            or not person.role_assignments.filter(
                role="INSTRUCTOR", revoked_at__isnull=True
            ).exists()
        ):
            issues.append("REGISTRATION_INCOMPLETE")
        try:
            normalize_cpf(decrypt_identifier(person.cpf_ciphertext))
        except ProtectedIdentifierConfigurationError:
            logger.exception("Protected CPF could not be checked for request %s", item.pk)
            issues.append("CPF_CHECK_UNAVAILABLE")
        except ValueError:
            issues.append("CPF_INVALID")

        documents = list(item.documents.filter(data_mode=DataMode.REAL))
        if not documents:
            issues.append("DOCUMENT_MISSING")
        if not any(
            document.document_type == InstructorDocument.DocumentType.DRIVER_LICENSE
            and document.scan_status == InstructorDocument.ScanStatus.CLEAN
            for document in documents
        ):
            issues.append("CNH_MISSING")
        if not any(
            document.document_type
            in {
                InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL,
                InstructorDocument.DocumentType.PROFESSIONAL_CERTIFICATE,
            }
            and document.scan_status == InstructorDocument.ScanStatus.CLEAN
            for document in documents
        ):
            issues.append("PROFESSIONAL_CREDENTIAL_MISSING")
        if any(
            document.size_bytes <= 0
            or document.size_bytes > settings.INSTRUCTOR_DOCUMENT_MAX_BYTES
            or document.mime_type not in {"application/pdf", "image/jpeg", "image/png"}
            or len(document.sha256) != 64
            for document in documents
        ):
            issues.append("FILE_INVALID")
        if any(
            document.scan_status == InstructorDocument.ScanStatus.PENDING for document in documents
        ):
            issues.append("FILE_SCAN_PENDING")
        if any(
            document.scan_status == InstructorDocument.ScanStatus.BLOCKED for document in documents
        ):
            issues.append("FILE_BLOCKED")

        categories = set(profile.categories or []) & set("ABCDE")
        if not categories:
            issues.append("CATEGORIES_MISSING")
        if not profile.offers.filter(
            category__in=categories, data_mode=DataMode.REAL, is_active=True
        ).exists():
            issues.append("OFFER_MISSING")
        try:
            area = profile.service_area
        except InstructorServiceArea.DoesNotExist:
            area = None
        if not area or not area.city.strip() or len(area.uf) != 2:
            issues.append("LOCATION_MISSING")
        if not area or not area.location_authorized or not area.public_service_location:
            issues.append("SERVICE_AREA_MISSING")
        contact = getattr(profile, "contact_channel", None)
        if not contact or not contact.is_active or contact.data_mode != DataMode.REAL:
            issues.append("WHATSAPP_MISSING")
        # Structural checks cannot establish document readability, identity or official validity.
        return issues

    @classmethod
    @transaction.atomic
    def run(cls, request_id):
        item = ProfessionalVerificationRequest.objects.select_for_update().get(pk=request_id)
        if item.status not in {item.Status.SUBMITTED, item.Status.UNDER_REVIEW}:
            return item.precheck_status
        issues = cls.issues(item)
        status = (
            item.PrecheckStatus.NEEDS_CORRECTION
            if issues
            else item.PrecheckStatus.READY_FOR_HUMAN_REVIEW
        )
        changed = status != item.precheck_status or issues != item.precheck_issues
        item.precheck_status = status
        item.precheck_issues = issues
        item.precheck_checked_at = timezone.now()
        item.save(
            update_fields=[
                "precheck_status",
                "precheck_issues",
                "precheck_checked_at",
                "updated_at",
            ]
        )
        if changed:
            AuditEvent.objects.create(
                action="discovery.instructor_precheck.completed",
                target_type="discovery.ProfessionalVerificationRequest",
                target_id=item.pk,
                reason_code=status,
                metadata={"issue_codes": issues},
            )
        return status


def queue_instructor_precheck(request_id):
    try:
        from .tasks import run_instructor_precheck_task

        run_instructor_precheck_task.delay(str(request_id))
    except Exception:
        logger.exception("Could not enqueue instructor precheck for request %s", request_id)


def due_precheck_ids(limit=50):
    stale = timezone.now() - timedelta(minutes=15)
    return list(
        ProfessionalVerificationRequest.objects.filter(
            status__in=[
                ProfessionalVerificationRequest.Status.SUBMITTED,
                ProfessionalVerificationRequest.Status.UNDER_REVIEW,
            ],
        )
        .filter(
            precheck_status__in=[
                ProfessionalVerificationRequest.PrecheckStatus.NOT_STARTED,
                ProfessionalVerificationRequest.PrecheckStatus.IN_PROGRESS,
                ProfessionalVerificationRequest.PrecheckStatus.NEEDS_CORRECTION,
            ]
        )
        .filter(Q(precheck_checked_at__isnull=True) | Q(precheck_checked_at__lt=stale))
        .order_by("precheck_checked_at", "submitted_at")
        .values_list("pk", flat=True)[:limit]
    )
