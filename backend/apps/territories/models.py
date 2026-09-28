import uuid

from django.db import models, transaction


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "país"
        verbose_name_plural = "países"

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
        verbose_name = "unidade federativa"
        verbose_name_plural = "unidades federativas"
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
    source_reference = models.CharField(max_length=255, blank=True)
    source_authority = models.CharField(max_length=255, blank=True)
    source_consulted_at = models.DateField(null=True, blank=True)
    evidence = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="regulatory_reviews",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="regulatory_approvals",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "prontidão regulatória"
        verbose_name_plural = "registros de prontidão regulatória"
        constraints = [
            models.UniqueConstraint(
                fields=["federative_unit", "provider_type", "capability"],
                name="uq_regulatory_readiness_scope",
            )
        ]

    def __str__(self):
        return f"{self.federative_unit_id}:{self.provider_type}:{self.capability}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            super().save(*args, **kwargs)
            RegulatoryReadinessHistory.objects.create(
                readiness=self,
                status=self.status,
                valid_from=self.valid_from,
                valid_until=self.valid_until,
                source_url=self.source_url,
                source_reference=self.source_reference,
                source_authority=self.source_authority,
                source_consulted_at=self.source_consulted_at,
                evidence=self.evidence,
                notes=self.notes,
                reviewed_by=self.reviewed_by,
                reviewed_at=self.reviewed_at,
                approved_by=self.approved_by,
                approved_at=self.approved_at,
            )


class RegulatoryReadinessHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    readiness = models.ForeignKey(
        RegulatoryReadiness, on_delete=models.PROTECT, related_name="history"
    )
    status = models.CharField(max_length=20, choices=RegulatoryReadiness.Status.choices)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    source_url = models.URLField(blank=True)
    source_reference = models.CharField(max_length=255, blank=True)
    source_authority = models.CharField(max_length=255, blank=True)
    source_consulted_at = models.DateField(null=True, blank=True)
    evidence = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        "accounts.Account", null=True, on_delete=models.PROTECT, related_name="+"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey("accounts.Account", null=True, on_delete=models.PROTECT)
    approved_at = models.DateTimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_at"]
        verbose_name = "histórico de prontidão regulatória"
        verbose_name_plural = "histórico de prontidão regulatória"

    def __str__(self):
        return f"{self.readiness_id}:{self.status}:{self.recorded_at}"

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValueError("Regulatory readiness history is append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Regulatory readiness history is append-only")
