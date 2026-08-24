import uuid

from django.db import models


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FederativeUnit(models.Model):
    class CommercialStatus(models.TextChoices):
        PREPARATION = "PREPARATION", "Preparação"
        FIRST_WAVE = "FIRST_WAVE", "Primeira onda"
        ACTIVE = "ACTIVE", "Ativa"
        PAUSED = "PAUSED", "Pausada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name="federative_units")
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)
    ibge_code = models.CharField(max_length=2, unique=True)
    commercial_status = models.CharField(
        max_length=20,
        choices=CommercialStatus.choices,
        default=CommercialStatus.PREPARATION,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class RegulatoryReadiness(models.Model):
    class Status(models.TextChoices):
        NOT_REVIEWED = "NOT_REVIEWED", "Não revisada"
        RESEARCHING = "RESEARCHING", "Em pesquisa"
        REVIEW_REQUIRED = "REVIEW_REQUIRED", "Revisão necessária"
        APPROVED = "APPROVED", "Aprovada"
        SUSPENDED = "SUSPENDED", "Suspensa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    federative_unit = models.ForeignKey(
        FederativeUnit, on_delete=models.PROTECT, related_name="regulatory_readiness"
    )
    provider_type = models.CharField(max_length=50)
    capability = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_REVIEWED)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    source_url = models.URLField(blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="regulatory_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["federative_unit", "provider_type", "capability"],
                name="uq_regulatory_readiness_scope",
            )
        ]

    def __str__(self):
        return f"{self.federative_unit_id}:{self.provider_type}:{self.capability}"
