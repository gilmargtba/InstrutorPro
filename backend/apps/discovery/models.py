import uuid
from contextlib import contextmanager
from contextvars import ContextVar

from django.conf import settings
from django.contrib.gis.db import models

_critical_state_mutation = ContextVar("discovery_critical_state_mutation", default=False)


@contextmanager
def allow_critical_state_mutation():
    token = _critical_state_mutation.set(True)
    try:
        yield
    finally:
        _critical_state_mutation.reset(token)


class ProtectedStateModel(models.Model):
    protected_state_fields = ()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk and not _critical_state_mutation.get():
            previous = (
                type(self).objects.filter(pk=self.pk).values(*self.protected_state_fields).first()
            )
            if previous and any(
                previous[field] != getattr(self, field) for field in self.protected_state_fields
            ):
                raise ValueError("Critical state changes must use a discovery domain service")
        return super().save(*args, **kwargs)


class DemoInstructorServiceLocation(models.Model):
    """Synthetic discovery projection; never a regulatory/publication record."""

    class Transmission(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        AUTOMATIC = "AUTOMATIC", "Automático"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fixture_key = models.CharField(max_length=80, unique=True)
    display_name = models.CharField(max_length=120)
    city = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    public_service_location = models.PointField(geography=True, srid=4326)
    private_location = models.PointField(geography=True, srid=4326, null=True, blank=True)
    categories = models.JSONField(default=list)
    transmission = models.CharField(max_length=12, choices=Transmission.choices)
    vehicle_available = models.BooleanField(default=True)
    demo_rating = models.DecimalField(max_digits=2, decimal_places=1)
    demo_price = models.DecimalField(max_digits=8, decimal_places=2)
    availability_summary = models.CharField(max_length=160)
    is_demo = models.BooleanField(default=True, editable=False)

    class Meta:
        ordering = ["display_name"]
        indexes = [models.Index(fields=["uf", "city"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(is_demo=True), name="discovery_demo_rows_only"
            )
        ]


class InstructorProfile(ProtectedStateModel):
    protected_state_fields = (
        "profile_status",
        "verification_status",
        "verified_until",
        "publication_status",
    )

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        SUBMITTED = "SUBMITTED", "Enviado"
        UNDER_REVIEW = "UNDER_REVIEW", "Em revisão"
        APPROVED = "APPROVED", "Aprovado"
        REJECTED = "REJECTED", "Rejeitado"
        SUSPENDED = "SUSPENDED", "Suspenso"

    class VerificationStatus(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", "Não iniciada"
        PENDING = "PENDING", "Pendente"
        VERIFIED = "VERIFIED", "Verificada"
        REJECTED = "REJECTED", "Rejeitada"
        EXPIRED = "EXPIRED", "Expirada"
        REVOKED = "REVOKED", "Revogada"

    class PublicationStatus(models.TextChoices):
        UNPUBLISHED = "UNPUBLISHED", "Não publicado"
        APPROVED = "APPROVED", "Publicado"
        REJECTED = "REJECTED", "Rejeitado"
        SUSPENDED = "SUSPENDED", "Suspenso"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.OneToOneField(
        "people.Person", on_delete=models.PROTECT, related_name="instructor_profile"
    )
    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    categories = models.JSONField(default=list)
    transmission_options = models.JSONField(default=list)
    vehicle_available = models.BooleanField(default=True)
    service_radius_km = models.PositiveSmallIntegerField(default=10)
    demo_rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.8)
    demo_price = models.DecimalField(max_digits=8, decimal_places=2, default=90)
    availability_summary = models.CharField(
        max_length=160, default="Horários demonstrativos nesta semana"
    )
    profile_status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    verification_status = models.CharField(
        max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.NOT_STARTED
    )
    verified_until = models.DateTimeField(null=True, blank=True)
    publication_status = models.CharField(
        max_length=20, choices=PublicationStatus.choices, default=PublicationStatus.UNPUBLISHED
    )
    is_demo = models.BooleanField(default=True, editable=False)

    class Meta:
        permissions = [("manage_instructor_publication", "Can decide instructor publication")]
        verbose_name = "perfil de instrutor"
        verbose_name_plural = "perfis de instrutores"


class InstructorServiceArea(ProtectedStateModel):
    protected_state_fields = ("location_authorized",)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        InstructorProfile, on_delete=models.CASCADE, related_name="service_area"
    )
    city = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    public_service_location = models.PointField(geography=True, srid=4326)
    private_location = models.PointField(geography=True, srid=4326, null=True, blank=True)
    radius_km = models.PositiveSmallIntegerField(default=10)
    location_authorized = models.BooleanField(default=False)

    class Meta:
        verbose_name = "área de atendimento do instrutor"
        verbose_name_plural = "áreas de atendimento dos instrutores"


class LocationPublicationAuthorization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service_area = models.ForeignKey(
        InstructorServiceArea, on_delete=models.PROTECT, related_name="authorization_history"
    )
    purpose = models.CharField(max_length=160)
    policy_version = models.CharField(max_length=40)
    authorized_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="revoked_location_authorizations",
    )
    reason = models.CharField(max_length=100, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="location_authorizations"
    )

    class Meta:
        verbose_name = "autorização de publicação da localização"
        verbose_name_plural = "autorizações de publicação da localização"

    @property
    def status(self):
        return "GRANTED" if self.revoked_at is None else "REVOKED"


class ProfessionalVerification(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "NOT_STARTED", "Não iniciada"
        PENDING = "PENDING", "Pendente"
        VERIFIED = "VERIFIED", "Verificada"
        REJECTED = "REJECTED", "Rejeitada"
        EXPIRED = "EXPIRED", "Expirada"
        REVOKED = "REVOKED", "Revogada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        InstructorProfile, on_delete=models.PROTECT, related_name="verification_history"
    )
    provider = models.CharField(max_length=30, default="SYNTHETIC")
    status = models.CharField(max_length=20, choices=Status.choices)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_until = models.DateTimeField(null=True, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="professional_verifications",
    )
    reason = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "verificação profissional"
        verbose_name_plural = "verificações profissionais"


class PublicationDecision(models.Model):
    class Decision(models.TextChoices):
        APPROVE = "APPROVE", "Aprovar"
        REJECT = "REJECT", "Rejeitar"
        SUSPEND = "SUSPEND", "Suspender"
        UNPUBLISH = "UNPUBLISH", "Despublicar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        InstructorProfile, on_delete=models.PROTECT, related_name="publication_history"
    )
    decision = models.CharField(max_length=20, choices=Decision.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="publication_decisions"
    )
    reason = models.CharField(max_length=100)
    verification = models.ForeignKey(
        ProfessionalVerification, null=True, blank=True, on_delete=models.PROTECT
    )
    before = models.JSONField(default=dict)
    after = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "decisão de publicação"
        verbose_name_plural = "decisões de publicação"
