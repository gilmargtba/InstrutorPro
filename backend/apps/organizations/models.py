import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models

from apps.people.models import Person

from .validators import normalize_cnpj, validate_cnpj


class PlatformOrganization(models.Model):
    class ValidationStatus(models.TextChoices):
        INCOMPLETE = "INCOMPLETE", "Incompleta"
        PENDING_VALIDATION = "PENDING_VALIDATION", "Pendente de validação"
        VALIDATED = "VALIDATED", "Validada"

    REQUIRED_FOR_VALIDATION = (
        "cnpj",
        "legal_name",
        "business_address",
        "legal_representative",
        "operational_contact",
        "privacy_contact",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    cnpj = models.CharField(
        "CNPJ",
        max_length=14,
        blank=True,
        validators=[validate_cnpj],
        help_text="Somente números; a formatação é aceita no painel.",
    )
    legal_name = models.CharField("razão social", max_length=200, blank=True)
    trade_name = models.CharField("nome fantasia", max_length=200, blank=True)
    business_address = models.TextField("endereço empresarial", blank=True)
    legal_representative = models.CharField("representante legal", max_length=200, blank=True)
    operational_contact = models.CharField("contato operacional", max_length=254, blank=True)
    privacy_contact = models.CharField(
        "canal de privacidade/LGPD",
        max_length=254,
        blank=True,
        validators=[
            EmailValidator(message="Informe um e-mail válido para o canal de privacidade.")
        ],
    )
    phone = models.CharField("telefone", max_length=32, blank=True)
    dpo_name = models.CharField("Encarregado/DPO", max_length=200, blank=True)
    dpo_contact = models.CharField("contato do Encarregado/DPO", max_length=254, blank=True)
    dpo_appointment_reference = models.CharField(
        "referência do ato de nomeação do DPO", max_length=200, blank=True
    )
    validation_status = models.CharField(
        "status",
        max_length=24,
        choices=ValidationStatus.choices,
        default=ValidationStatus.INCOMPLETE,
    )
    validated_at = models.DateTimeField("validada em", null=True, blank=True)
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="validada por",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="validated_platform_organizations",
    )
    version = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "organização / controlador"
        verbose_name_plural = "organização / controlador"
        permissions = [
            ("manage_platform_organization", "Pode configurar a organização controladora"),
            ("validate_platform_organization", "Pode validar a organização controladora"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cnpj="") | models.Q(cnpj__regex=r"^\d{14}$"),
                name="organization_cnpj_digits_or_blank",
            )
        ]

    def __str__(self):
        return self.legal_name or "Organização controladora"

    def is_complete(self) -> bool:
        return all(bool(getattr(self, field, "").strip()) for field in self.REQUIRED_FOR_VALIDATION)

    def clean(self):
        super().clean()
        self.cnpj = normalize_cnpj(self.cnpj)
        if self.validation_status == self.ValidationStatus.VALIDATED and not self.is_complete():
            raise ValidationError("Todos os campos obrigatórios devem existir antes da validação.")


class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name


class ClinicMembership(models.Model):
    class Authorization(models.TextChoices):
        RESPONSIBLE = "RESPONSIBLE", "Responsável"
        ADMINISTRATOR = "ADMINISTRATOR", "Administrador"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="memberships")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="clinic_memberships")
    authorization = models.CharField(max_length=20, choices=Authorization.choices)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["clinic", "person"], name="uq_clinic_person")
        ]

    def __str__(self):
        return f"{self.clinic_id}:{self.person_id}"
