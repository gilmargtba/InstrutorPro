import pytest
from django.contrib.auth.models import Permission
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    ProfessionalVerificationRequest,
)
from apps.discovery.services import InvalidWorkflowTransition
from apps.discovery.verification_services import (
    approve_verification_request,
    start_verification_review,
)
from apps.people.models import Person, RoleAssignment

VERIFICATION_ENABLED = {
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "PROFESSIONAL_VERIFICATION_MODE": "PRODUCTION",
    "REAL_PROFESSIONAL_VERIFICATION": True,
    "PII_FIELD_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    "PII_FINGERPRINT_KEY": "test-only-fingerprint-key-with-32-bytes-minimum",
}


def instructor(username="instructor"):
    account = Account.objects.create_user(
        username=username, email=f"{username}@example.invalid", password="test-password-123"
    )
    person = Person.objects.create(account=account)
    RoleAssignment.objects.create(
        person=person,
        role=RoleAssignment.Role.INSTRUCTOR,
        granted_by=account,
        grant_reason="TEST",
    )
    profile = InstructorProfile.objects.create(
        person=person, display_name="Instrutor Teste", is_demo=False
    )
    return account, profile


def reviewer(username="reviewer"):
    account = Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="test-password-123",
        is_staff=True,
    )
    account.user_permissions.add(
        Permission.objects.get(codename="review_professional_verification")
    )
    return account


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_owner_submits_cpf_encrypted_and_receives_only_masked_value():
    account, profile = instructor()
    client = APIClient()
    client.force_authenticate(account)

    saved = client.patch(
        "/api/v1/instructor/verification/", {"cpf": "529.982.247-25"}, format="json"
    )
    assert saved.status_code == 200
    profile.person.refresh_from_db()
    assert "52998224725" not in profile.person.cpf_ciphertext
    assert len(profile.person.cpf_fingerprint) == 64
    assert saved.json()["cpf_masked"] == "***.***.***-25"
    assert "cpf_ciphertext" not in saved.json()
    assert "cpf_fingerprint" not in saved.json()

    submitted = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    repeated = client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    assert submitted.status_code == 201
    assert repeated.status_code == 200
    assert ProfessionalVerificationRequest.objects.filter(profile=profile).count() == 1
    assert (
        AuditEvent.objects.filter(action="discovery.professional_verification.submitted").count()
        == 1
    )

    changed = client.patch(
        "/api/v1/instructor/verification/", {"cpf": "111.444.777-35"}, format="json"
    )
    assert changed.status_code == 400
    profile.person.refresh_from_db()
    assert profile.person.cpf_last2 == "25"


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_cpf_is_validated_and_unique_by_blind_index():
    first, _ = instructor("first")
    second, _ = instructor("second")
    client = APIClient()
    client.force_authenticate(first)
    assert (
        client.patch(
            "/api/v1/instructor/verification/", {"cpf": "52998224725"}, format="json"
        ).status_code
        == 200
    )
    client.force_authenticate(second)
    duplicate = client.patch(
        "/api/v1/instructor/verification/", {"cpf": "529.982.247-25"}, format="json"
    )
    invalid = client.patch(
        "/api/v1/instructor/verification/", {"cpf": "111.111.111-11"}, format="json"
    )
    assert duplicate.status_code == 400
    assert invalid.status_code == 400


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_admin_review_requires_assignment_and_metadata_and_does_not_publish():
    owner, profile = instructor()
    client = APIClient()
    client.force_authenticate(owner)
    client.patch("/api/v1/instructor/verification/", {"cpf": "52998224725"}, format="json")
    client.post("/api/v1/instructor/verification/submit/", {}, format="json")
    item = ProfessionalVerificationRequest.objects.get(profile=profile)
    admin = reviewer()
    other = reviewer("other-reviewer")

    start_verification_review(actor=admin, verification_request=item)
    item.refresh_from_db()
    with pytest.raises(InvalidWorkflowTransition):
        start_verification_review(actor=other, verification_request=item)
    with pytest.raises(InvalidWorkflowTransition):
        approve_verification_request(actor=admin, verification_request=item)

    item.verification_method = "Consulta manual"
    item.verification_source = "Fonte oficial autorizada"
    item.checked_at = timezone.now()
    item.save(update_fields=["verification_method", "verification_source", "checked_at"])
    approve_verification_request(actor=admin, verification_request=item)
    profile.refresh_from_db()
    item.refresh_from_db()
    assert item.status == ProfessionalVerificationRequest.Status.VERIFIED
    assert profile.verification_status == InstructorProfile.VerificationStatus.VERIFIED
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    assert profile.profile_status == InstructorProfile.Status.DRAFT


@pytest.mark.django_db
@override_settings(**{**VERIFICATION_ENABLED, "REAL_PROFESSIONAL_VERIFICATION": False})
def test_feature_is_fail_closed_when_capability_is_disabled():
    account, _ = instructor()
    client = APIClient()
    client.force_authenticate(account)
    assert client.get("/api/v1/instructor/verification/").status_code == 403
