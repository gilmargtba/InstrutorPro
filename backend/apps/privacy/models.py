import hashlib
import uuid

from django.conf import settings
from django.db import models


class PrivacyNotice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=40, unique=True)
    title = models.CharField(max_length=160)
    published_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=models.Q(is_current=True),
                name="uq_current_privacy_notice",
            )
        ]

    def __str__(self):
        return f"{self.version} - {self.title}"


class LegalDocument(models.Model):
    class Type(models.TextChoices):
        TERMS = "TERMS", "Termos de Uso"

    class Audience(models.TextChoices):
        STUDENT = "STUDENT", "Aluno"
        INSTRUCTOR = "INSTRUCTOR", "Instrutor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=20, choices=Type.choices)
    audience = models.CharField(max_length=20, choices=Audience.choices)
    version = models.CharField(max_length=40)
    title = models.CharField(max_length=180)
    content = models.TextField()
    content_sha256 = models.CharField(max_length=64, editable=False)
    effective_at = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["document_type", "audience", "version"],
                name="uq_legal_document_version",
            ),
            models.UniqueConstraint(
                fields=["document_type", "audience"],
                condition=models.Q(is_active=True),
                name="uq_active_legal_document_audience",
            ),
        ]

    def __str__(self):
        return f"{self.document_type}:{self.audience}:{self.version}"

    def save(self, *args, **kwargs):
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).first()
            immutable_fields = (
                "document_type",
                "audience",
                "version",
                "title",
                "content",
                "effective_at",
            )
            if (
                previous
                and previous.is_active
                and any(
                    getattr(previous, field) != getattr(self, field) for field in immutable_fields
                )
            ):
                raise ValueError("Published legal documents are immutable; create a new version")
        self.content_sha256 = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)


class LegalAcceptanceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="legal_acceptances"
    )
    terms_document = models.ForeignKey(
        LegalDocument, on_delete=models.PROTECT, related_name="acceptances"
    )
    privacy_notice = models.ForeignKey(
        PrivacyNotice, on_delete=models.PROTECT, related_name="legal_acceptances"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    request_id = models.UUIDField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["account", "terms_document", "privacy_notice"],
                name="uq_account_legal_acceptance_versions",
            )
        ]

    def __str__(self):
        return f"{self.account_id}:{self.terms_document_id}:{self.privacy_notice_id}"

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Legal acceptance records are immutable")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Legal acceptance records are immutable")


class PrivacyRequest(models.Model):
    class Type(models.TextChoices):
        ACCESS = "ACCESS", "Acesso"
        CORRECTION = "CORRECTION", "Correção"
        DELETION = "DELETION", "Exclusão"
        PORTABILITY = "PORTABILITY", "Portabilidade"
        CONSENT_REVOCATION = "CONSENT_REVOCATION", "Revogação de consentimento"
        OTHER = "OTHER", "Outro"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Aberta"
        IN_REVIEW = "IN_REVIEW", "Em análise"
        COMPLETED = "COMPLETED", "Concluída"
        REJECTED = "REJECTED", "Não atendida integralmente"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="privacy_requests"
    )
    request_type = models.CharField(max_length=24, choices=Type.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    details = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_privacy_requests",
    )
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_at"]
        permissions = [("manage_privacy_requests", "Can manage privacy requests")]

    def __str__(self):
        return f"{self.request_type}:{self.id}"
