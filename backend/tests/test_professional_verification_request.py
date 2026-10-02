from uuid import uuid4

import pytest
from django.contrib import admin as django_admin
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.test import override_settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    ProfessionalVerificationRequest,
)
from apps.discovery.services import InvalidWorkflowTransition, approve_publication
from apps.discovery.verification_services import (
    approve_verification_request,
    start_verification_review,
)
from apps.people.models import Person, RoleAssignment
from apps.territories.models import Country, FederativeUnit, RegulatoryReadiness
from apps.territories.policies import (
    INSTRUCTOR_PROVIDER_TYPE,
    INSTRUCTOR_PUBLICATION_CAPABILITY,
)

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
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.SUBMITTED
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
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.UNDER_REVIEW
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
    assert profile.profile_status == InstructorProfile.Status.UNDER_REVIEW


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_admin_can_record_consultation_and_approve_in_one_audited_step():
    _, profile = instructor("quick-review-owner")
    analyst = reviewer("quick-review-analyst")
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.SUBMITTED
    )
    start_verification_review(actor=analyst, verification_request=item)
    item.refresh_from_db()
    admin_config = django_admin.site._registry[ProfessionalVerificationRequest]
    assert admin_config.triage_status(item) == "3 pendência(s)"
    assert admin_config.actions == ("start_review_action",)
    web = Client()
    web.force_login(analyst)
    url = reverse("admin:discovery_verification_request_transition", args=[item.pk, "approve"])
    page = web.get(url)
    assert page.status_code == 200
    assert "Registrar consulta e aprovar verificação interna" in page.content.decode()
    data = {
        "verification_method": "Consulta manual",
        "verification_source": "Fonte oficial conferida",
        "internal_notes": "Evidência consistente.",
    }
    assert web.post(url, data).status_code == 200  # Attestation is mandatory.
    item.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert not item.verification_source
    data["consultation_confirmed"] = "on"
    assert web.post(url, data).status_code == 302
    item.refresh_from_db()
    profile.refresh_from_db()
    assert item.status == item.Status.VERIFIED
    assert admin_config.triage_status(item) == "Concluída"
    assert item.checked_at is not None and item.decision_by == analyst
    assert profile.verification_status == profile.VerificationStatus.VERIFIED
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert (
        AuditEvent.objects.filter(
            action="discovery.professional_verification.review_metadata_updated", target_id=item.pk
        ).count()
        == 1
    )


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_completed_verification_admin_hides_save_and_handles_stale_post_without_writing():
    _, profile = instructor("completed-review-owner")
    analyst = reviewer("completed-review-analyst")
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.SUBMITTED
    )
    web = Client()
    web.force_login(analyst)
    change_url = reverse("admin:discovery_professionalverificationrequest_change", args=[item.pk])
    approval_url = reverse(
        "admin:discovery_verification_request_transition", args=[item.pk, "approve"]
    )
    assert b'name="_save"' not in web.get(change_url).content
    assert web.post(change_url, {"verification_method": "Antes da análise"}).status_code == 302
    item.refresh_from_db()
    assert not item.verification_method
    start_verification_review(actor=analyst, verification_request=item)
    item.refresh_from_db()
    assert web.get(change_url).status_code == 200
    assert b'name="_save"' in web.get(change_url).content
    assert (
        web.post(
            approval_url,
            {
                "verification_method": "Consulta manual",
                "verification_source": "Fonte oficial conferida",
                "consultation_confirmed": "on",
            },
        ).status_code
        == 302
    )
    item.refresh_from_db()
    assert item.status == item.Status.VERIFIED

    page = web.get(change_url)
    assert page.status_code == 200
    assert b'name="_save"' not in page.content
    assert "verification_method" in django_admin.site._registry[
        ProfessionalVerificationRequest
    ].get_readonly_fields(page.wsgi_request, item)
    audit_count = AuditEvent.objects.filter(target_id=item.pk).count()
    stale_save = web.post(
        change_url,
        {
            "verification_method": "Tentativa tardia",
            "verification_source": "Outra fonte",
            "_save": "Salvar",
        },
    )
    assert stale_save.status_code == 302
    assert stale_save.url == change_url
    item.refresh_from_db()
    assert item.verification_method == "Consulta manual"
    assert item.verification_source == "Fonte oficial conferida"
    assert AuditEvent.objects.filter(target_id=item.pk).count() == audit_count

    other = reviewer("completed-review-other")
    web.force_login(other)
    assert web.post(change_url, {"verification_method": "Não autorizado"}).status_code == 403
    item.refresh_from_db()
    assert item.verification_method == "Consulta manual"
    assert AuditEvent.objects.filter(target_id=item.pk).count() == audit_count


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_one_step_approval_rolls_back_metadata_when_required_document_is_missing():
    _, profile = instructor("quick-review-missing")
    analyst = reviewer("quick-review-missing-analyst")
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile,
        status=ProfessionalVerificationRequest.Status.SUBMITTED,
        requirements_snapshot=[{"id": str(uuid4()), "required": True}],
    )
    start_verification_review(actor=analyst, verification_request=item)
    web = Client()
    web.force_login(analyst)
    url = reverse("admin:discovery_verification_request_transition", args=[item.pk, "approve"])
    assert (
        web.post(
            url,
            {
                "verification_method": "Consulta manual",
                "verification_source": "Fonte oficial conferida",
                "consultation_confirmed": "on",
            },
        ).status_code
        == 200
    )
    item.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert item.checked_at is None and not item.verification_source
    assert not AuditEvent.objects.filter(
        action="discovery.professional_verification.review_metadata_updated", target_id=item.pk
    ).exists()


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_rejection_cannot_change_reason_for_another_reviewer_and_uses_structured_code():
    _, profile = instructor("quick-reject-owner")
    analyst = reviewer("quick-reject-analyst")
    other = reviewer("quick-reject-other")
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.SUBMITTED
    )
    start_verification_review(actor=analyst, verification_request=item)
    web = Client()
    url = reverse("admin:discovery_verification_request_transition", args=[item.pk, "reject"])
    web.force_login(other)
    assert web.post(url, {"rejection_reason_code": "DOCUMENT_MISMATCH"}).status_code == 200
    item.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert not item.rejection_reason_code
    web.force_login(analyst)
    assert web.post(url, {"rejection_reason_code": "DOCUMENT_MISMATCH"}).status_code == 302
    item.refresh_from_db()
    assert item.status == item.Status.REJECTED
    assert item.rejection_reason_code == "DOCUMENT_MISMATCH"
    assert item.decision_by == analyst


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_verified_real_request_requires_territorial_gate_then_manual_publication():
    owner, profile = instructor("publication-owner")
    admin = reviewer("publication-reviewer")
    admin.user_permissions.add(Permission.objects.get(codename="manage_instructor_publication"))
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.22, -30.03, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    client = APIClient()
    client.force_authenticate(owner)
    assert (
        client.patch(
            "/api/v1/instructor/verification/", {"cpf": "52998224725"}, format="json"
        ).status_code
        == 200
    )
    assert (
        client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code == 201
    )
    item = ProfessionalVerificationRequest.objects.get(profile=profile)
    start_verification_review(actor=admin, verification_request=item)
    item.refresh_from_db()
    item.verification_method = "Consulta manual"
    item.verification_source = "Fonte autorizada"
    item.checked_at = timezone.now()
    item.save(update_fields=["verification_method", "verification_source", "checked_at"])
    approve_verification_request(actor=admin, verification_request=item)
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.UNDER_REVIEW
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    with pytest.raises(InvalidWorkflowTransition, match="UF não possui autorização"):
        approve_publication(actor=admin, profile=profile, reason="ADMIN_REVIEWED_PUBLICATION")
    country, _ = Country.objects.get_or_create(code="BR", defaults={"name": "Brasil"})
    rs, _ = FederativeUnit.objects.get_or_create(
        code="RS",
        defaults={"country": country, "name": "Rio Grande do Sul", "ibge_code": "43"},
    )
    RegulatoryReadiness.objects.create(
        federative_unit=rs,
        provider_type=INSTRUCTOR_PROVIDER_TYPE,
        capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        status=RegulatoryReadiness.Status.APPROVED,
        valid_from=timezone.localdate(),
        source_url="https://publicacoeslegais.detran.rs.gov.br/portaria-detran-rs-n-99-2026",
        source_reference="Portaria DETRAN/RS 99/2026",
        source_authority="DETRAN-RS",
        source_consulted_at=timezone.localdate(),
        evidence="Fonte e autorização individual conferidas no teste.",
        reviewed_by=admin,
        reviewed_at=timezone.now(),
        approved_by=admin,
        approved_at=timezone.now(),
    )
    approve_publication(actor=admin, profile=profile, reason="ADMIN_REVIEWED_PUBLICATION")
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.APPROVED
    assert profile.publication_status == InstructorProfile.PublicationStatus.APPROVED
    assert AuditEvent.objects.filter(
        action="discovery.publication_approve", target_id=profile.id
    ).exists()


@pytest.mark.django_db
@override_settings(**VERIFICATION_ENABLED)
def test_admin_publication_button_confirms_reason_and_preserves_regulatory_gate():
    owner, profile = instructor("admin-publication-owner")
    manager = reviewer("admin-publication-manager")
    manager.user_permissions.add(
        Permission.objects.get(codename="manage_instructor_publication"),
        Permission.objects.get(codename="change_instructorprofile"),
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Porto Alegre",
        uf="RS",
        public_service_location=Point(-51.22, -30.03, srid=4326),
        radius_km=10,
        location_authorized=True,
    )
    api = APIClient()
    api.force_authenticate(owner)
    assert (
        api.patch(
            "/api/v1/instructor/verification/", {"cpf": "52998224725"}, format="json"
        ).status_code
        == 200
    )
    assert api.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code == 201
    item = ProfessionalVerificationRequest.objects.get(profile=profile)
    start_verification_review(actor=manager, verification_request=item)
    item.refresh_from_db()
    item.verification_method = "Consulta manual"
    item.verification_source = "Fonte autorizada"
    item.checked_at = timezone.now()
    item.save(update_fields=["verification_method", "verification_source", "checked_at"])
    approve_verification_request(actor=manager, verification_request=item)

    url = reverse("admin:discovery_instructor_publication_transition", args=[profile.pk, "publish"])
    web = Client()
    web.force_login(manager)
    assert web.get(url).status_code == 200
    assert web.post(url, {"reason": "  "}).status_code == 302
    assert web.post(url, {"reason": "Revisão manual concluída"}).status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED

    country, _ = Country.objects.get_or_create(code="BR", defaults={"name": "Brasil"})
    rs, _ = FederativeUnit.objects.get_or_create(
        code="RS",
        defaults={"country": country, "name": "Rio Grande do Sul", "ibge_code": "43"},
    )
    RegulatoryReadiness.objects.create(
        federative_unit=rs,
        provider_type=INSTRUCTOR_PROVIDER_TYPE,
        capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        status=RegulatoryReadiness.Status.APPROVED,
        valid_from=timezone.localdate(),
        source_url="https://publicacoeslegais.detran.rs.gov.br/portaria-detran-rs-n-99-2026",
        source_reference="Portaria DETRAN/RS 99/2026",
        source_authority="DETRAN-RS",
        source_consulted_at=timezone.localdate(),
        evidence="Fonte e autorização individual conferidas no teste.",
        reviewed_by=manager,
        reviewed_at=timezone.now(),
        approved_by=manager,
        approved_at=timezone.now(),
    )
    assert web.post(url, {"reason": "Revisão manual concluída"}).status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == InstructorProfile.PublicationStatus.APPROVED
    suspend = reverse(
        "admin:discovery_instructor_publication_transition", args=[profile.pk, "suspend"]
    )
    assert web.post(suspend, {"reason": "Suspensão administrativa"}).status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == InstructorProfile.PublicationStatus.SUSPENDED
    unpublish = reverse(
        "admin:discovery_instructor_publication_transition", args=[profile.pk, "unpublish"]
    )
    assert web.post(unpublish, {"reason": "Despublicação administrativa"}).status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    unauthorized = reviewer("admin-publication-unauthorized")
    web.force_login(unauthorized)
    assert web.get(url).status_code == 403


@pytest.mark.django_db
@override_settings(**{**VERIFICATION_ENABLED, "REAL_PROFESSIONAL_VERIFICATION": False})
def test_feature_is_fail_closed_when_capability_is_disabled():
    account, _ = instructor()
    client = APIClient()
    client.force_authenticate(account)
    assert client.get("/api/v1/instructor/verification/").status_code == 403
