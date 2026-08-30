import uuid

from django.contrib.gis.db import models


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
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["uf", "city", "data_mode"])]


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.OneToOneField(
        "discovery.InstructorProfile", on_delete=models.CASCADE, related_name="vehicle"
    )
    category = models.CharField(max_length=8)
    make = models.CharField(max_length=60)
    model = models.CharField(max_length=60)
    year = models.PositiveSmallIntegerField()
    transmission = models.CharField(max_length=12)
    data_mode = models.CharField(max_length=12, choices=DataMode.choices)


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
