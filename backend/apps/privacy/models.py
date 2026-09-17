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
