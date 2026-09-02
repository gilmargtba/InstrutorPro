import uuid
from pathlib import Path

from django.contrib.gis.db import models
from django.db.models import Q


def private_document_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"quarantine/{instance.instructor_id}/{uuid.uuid4().hex}{suffix}"


def private_profile_photo_path(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"profile-photo-quarantine/{instance.instructor_id}/{uuid.uuid4().hex}{suffix}"


class DataMode(models.TextChoices):
    SYNTHETIC = "SYNTHETIC", "Sintético"
    REAL = "REAL", "Real"


class StudentProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.OneToOneField(
        "people.Person", on_delete=models.PROTECT, related_name="student_profile"
    )
    display_name = models.CharField(max_length=120)
    city = models.CharField(max_length=100)
    uf = models.ForeignKey("territories.FederativeUnit", on_delete=models.PROTECT)
    intended_category = models.CharField(max_length=8, default="B")
    preferred_transmission = models.CharField(max_length=12, default="INDIFFERENT")
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["uf", "city", "data_mode"])]


class InstructorOnboardingDraft(models.Model):
    """Progress marker for the synthetic onboarding; domain entities remain source of truth."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.OneToOneField(
        "discovery.InstructorProfile", on_delete=models.CASCADE, related_name="onboarding_draft"
    )
    current_step = models.PositiveSmallIntegerField(default=1)
    completed_steps = models.JSONField(default=list)
    region = models.CharField(max_length=100, blank=True)
    credential_identifier = models.CharField(max_length=160, blank=True)
    credential_issued_at = models.DateField(null=True, blank=True)
    credential_valid_until = models.DateField(null=True, blank=True)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(current_step__gte=1) & Q(current_step__lte=7),
                name="ck_onboarding_draft_step",
            )
        ]


class StudentDemand(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativa"
        CANCELLED = "CANCELLED", "Cancelada"
        EXPIRED = "EXPIRED", "Expirada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name="demands")
    category = models.CharField(max_length=8)
    city = models.CharField(max_length=100)
    uf = models.ForeignKey("territories.FederativeUnit", on_delete=models.PROTECT)
    region = models.CharField(max_length=100, blank=True)
    private_centroid = models.PointField(geography=True, srid=4326, null=True, blank=True)
    radius_km = models.PositiveSmallIntegerField(default=10)
    transmission = models.CharField(max_length=12, blank=True)
    availability = models.CharField(max_length=160, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["status", "data_mode", "uf", "city"])]


class InstructorVehicle(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        UNDER_REVIEW = "UNDER_REVIEW", "Em análise"
        APPROVED = "APPROVED", "Aprovado"
        REJECTED = "REJECTED", "Rejeitado"
        EXPIRED = "EXPIRED", "Vencido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.OneToOneField(
        "discovery.InstructorProfile", on_delete=models.CASCADE, related_name="vehicle"
    )
    category = models.CharField(max_length=8)
    make = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    year = models.PositiveSmallIntegerField()
    transmission = models.CharField(max_length=12)
    ownership_type = models.CharField(max_length=24, default="AVAILABLE_TO_INSTRUCTOR")
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)


class DocumentRequirement(models.Model):
    class DocumentType(models.TextChoices):
        INSTRUCTOR_AUTHORIZATION = "INSTRUCTOR_AUTHORIZATION", "Autorização/credencial de instrutor"
        INSTRUCTOR_COURSE = "INSTRUCTOR_COURSE", "Certificado de curso de instrutor"
        VEHICLE_EVIDENCE = "VEHICLE_EVIDENCE", "Documento/evidência do veículo"
        OTHER = "OTHER", "Outro requisito territorial"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uf = models.CharField(max_length=2)
    category = models.CharField(max_length=8)
    provider_type = models.CharField(max_length=24, default="INSTRUCTOR")
    rule_version = models.CharField(max_length=40)
    document_type = models.CharField(max_length=40, choices=DocumentType.choices)
    label = models.CharField(max_length=160)
    required = models.BooleanField(default=True)
    requires_validity = models.BooleanField(default=False)
    active_from = models.DateField()
    active_until = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["uf", "category", "provider_type", "rule_version", "document_type"],
                name="uq_document_requirement_rule",
            ),
            models.CheckConstraint(
                condition=Q(active_until__isnull=True)
                | Q(active_until__gte=models.F("active_from")),
                name="ck_document_requirement_dates",
            ),
        ]


class InstructorDocument(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        UNDER_REVIEW = "UNDER_REVIEW", "Em análise"
        APPROVED = "APPROVED", "Aprovado"
        REJECTED = "REJECTED", "Rejeitado"
        EXPIRED = "EXPIRED", "Vencido"

    class ScanStatus(models.TextChoices):
        PENDING = "PENDING", "Aguardando análise"
        CLEAN = "CLEAN", "Fixture segura"
        BLOCKED = "BLOCKED", "Bloqueado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        "discovery.InstructorProfile", on_delete=models.PROTECT, related_name="documents"
    )
    vehicle = models.ForeignKey(
        InstructorVehicle,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="documents",
    )
    requirement = models.ForeignKey(
        DocumentRequirement, on_delete=models.PROTECT, related_name="documents"
    )
    issuer = models.CharField(max_length=160, blank=True)
    credential_uf = models.CharField(max_length=2, blank=True)
    private_identifier = models.CharField(max_length=160, blank=True)
    issued_at = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to=private_document_path, max_length=300)
    original_name = models.CharField(max_length=180)
    mime_type = models.CharField(max_length=80)
    size_bytes = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    scan_status = models.CharField(
        max_length=20, choices=ScanStatus.choices, default=ScanStatus.PENDING
    )
    version = models.PositiveSmallIntegerField(default=1)
    supersedes = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="replacements"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_instructor_documents",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_reason = models.CharField(max_length=240, blank=True)
    review_source = models.CharField(max_length=240, blank=True)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)

    class Meta:
        indexes = [models.Index(fields=["instructor", "status", "valid_until"])]
        permissions = [("review_instructor_document", "Can review instructor documents")]
        constraints = [
            models.CheckConstraint(
                condition=Q(valid_until__isnull=True)
                | Q(issued_at__isnull=True)
                | Q(valid_until__gte=models.F("issued_at")),
                name="ck_instructor_document_dates",
            )
        ]


class ProfilePhoto(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        APPROVED = "APPROVED", "Aprovada"
        REJECTED = "REJECTED", "Rejeitada"
        REPLACEMENT_REQUESTED = "REPLACEMENT_REQUESTED", "Substituição solicitada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        "discovery.InstructorProfile", on_delete=models.PROTECT, related_name="profile_photos"
    )
    file = models.FileField(upload_to=private_profile_photo_path, max_length=300)
    original_name = models.CharField(max_length=180)
    mime_type = models.CharField(max_length=80)
    size_bytes = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    publication_authorized_at = models.DateTimeField(null=True, blank=True)
    publication_notice_version = models.CharField(max_length=80, blank=True)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        "accounts.Account",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_profile_photos",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_reason = models.CharField(max_length=240, blank=True)

    class Meta:
        permissions = [("review_profile_photo", "Can review instructor profile photos")]
        indexes = [models.Index(fields=["instructor", "status", "uploaded_at"])]


class PracticalTrainingRequirement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uf = models.CharField(max_length=2)
    category = models.CharField(max_length=8)
    process_type = models.CharField(max_length=40)
    rule_version = models.CharField(max_length=40)
    minimum_minutes = models.PositiveIntegerField()
    source_reference = models.CharField(max_length=300)
    active_from = models.DateField()
    active_until = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["uf", "category", "process_type", "rule_version"],
                name="uq_practical_training_rule",
            ),
            models.CheckConstraint(
                condition=Q(minimum_minutes__gt=0), name="ck_training_minimum_positive"
            ),
            models.CheckConstraint(
                condition=Q(active_until__isnull=True)
                | Q(active_until__gte=models.F("active_from")),
                name="ck_training_requirement_dates",
            ),
        ]


class PlatformLesson(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Agendada na plataforma"
        COMPLETED = "COMPLETED", "Concluída na plataforma"
        CANCELLED = "CANCELLED", "Cancelada na plataforma"

    class OfficialRecordStatus(models.TextChoices):
        NOT_INTEGRATED = "NOT_INTEGRATED", "Sem integração oficial"
        EXTERNALLY_DECLARED = "EXTERNALLY_DECLARED", "Registro externo apenas declarado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile, on_delete=models.PROTECT, related_name="platform_lessons"
    )
    instructor = models.ForeignKey(
        "discovery.InstructorProfile",
        on_delete=models.PROTECT,
        related_name="platform_lessons",
    )
    vehicle = models.ForeignKey(
        InstructorVehicle, on_delete=models.PROTECT, related_name="platform_lessons"
    )
    requirement = models.ForeignKey(
        PracticalTrainingRequirement,
        on_delete=models.PROTECT,
        related_name="platform_lessons",
    )
    starts_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices)
    official_record_status = models.CharField(
        max_length=24,
        choices=OfficialRecordStatus.choices,
        default=OfficialRecordStatus.NOT_INTEGRATED,
    )
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(duration_minutes__gt=0), name="ck_platform_lesson_duration_positive"
            )
        ]


class InstructorPrerequisiteAcceptance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        "discovery.InstructorProfile",
        on_delete=models.PROTECT,
        related_name="prerequisite_acceptances",
    )
    policy_version = models.CharField(max_length=40)
    accepted_at = models.DateTimeField(auto_now_add=True)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["instructor", "policy_version"], name="uq_instructor_prerequisite_version"
            )
        ]


class LessonRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        ACCEPTED = "ACCEPTED", "Aceita"
        REJECTED = "REJECTED", "Rejeitada"
        CANCELLED = "CANCELLED", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile, on_delete=models.PROTECT, related_name="lesson_requests"
    )
    instructor = models.ForeignKey(
        "discovery.InstructorProfile", on_delete=models.PROTECT, related_name="lesson_requests"
    )
    category = models.CharField(max_length=8)
    preferred_period = models.CharField(max_length=80, blank=True)
    message = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["instructor", "status", "created_at"])]
