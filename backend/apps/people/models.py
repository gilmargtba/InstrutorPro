import uuid

from django.conf import settings
from django.db import models


class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="person"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class RoleAssignment(models.Model):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Aluno"
        INSTRUCTOR = "INSTRUCTOR", "Instrutor"
        DOCTOR = "DOCTOR", "Médico"
        PSYCHOLOGIST = "PSYCHOLOGIST", "Psicólogo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.CharField(max_length=20, choices=Role.choices)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="granted_role_assignments",
    )
    grant_reason = models.CharField(max_length=100)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="revoked_role_assignments",
    )
    revoke_reason = models.CharField(max_length=100, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "role"],
                condition=models.Q(revoked_at__isnull=True),
                name="uq_active_person_role",
            )
        ]
        permissions = [("manage_role_assignments", "Can grant and revoke personal roles")]

    def __str__(self):
        return f"{self.person_id}:{self.role}"

    @property
    def status(self):
        return "ACTIVE" if self.revoked_at is None else "REVOKED"
