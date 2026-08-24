import uuid

from django.db import models

from apps.people.models import Person


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
