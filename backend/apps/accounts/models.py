import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Account(AbstractUser):
    class LifecycleStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativa"
        BLOCKED = "BLOCKED", "Bloqueada"
        DEACTIVATED = "DEACTIVATED", "Desativada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    lifecycle_status = models.CharField(
        max_length=20,
        choices=LifecycleStatus.choices,
        default=LifecycleStatus.ACTIVE,
    )
    lifecycle_changed_at = models.DateTimeField(default=timezone.now)
    lifecycle_changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="account_lifecycle_changes",
    )
    lifecycle_reason = models.CharField(max_length=100, default="ACCOUNT_CREATED")
    lifecycle_version = models.PositiveBigIntegerField(default=0)

    class Meta:
        permissions = [("manage_account_lifecycle", "Can manage account lifecycle")]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(lifecycle_status="ACTIVE", is_active=True)
                    | models.Q(
                        lifecycle_status__in=["BLOCKED", "DEACTIVATED"],
                        is_active=False,
                    )
                ),
                name="account_lifecycle_matches_is_active",
            )
        ]

    @property
    def can_operate(self):
        return self.lifecycle_status == self.LifecycleStatus.ACTIVE and self.is_active


class ExternalIdentity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="external_identities"
    )
    provider = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "subject"], name="uq_identity_provider_subject"
            ),
            models.UniqueConstraint(
                fields=["account", "provider"], name="uq_identity_account_provider"
            ),
        ]

    def __str__(self):
        return f"{self.provider}:{self.id}"
