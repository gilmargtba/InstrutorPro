from datetime import timedelta

import pytest
from django.contrib import admin
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.admin import AccountAdmin
from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, ProfessionalVerification
from apps.marketplace.models import DataMode, StudentProfile
from apps.people.models import Person, RoleAssignment
from apps.privacy.models import PrivacyRequest
from apps.territories.models import Country, FederativeUnit


def account_with_person(username):
    account = Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="safe-test-password",
    )
    return account, Person.objects.create(account=account)


def authenticated(account):
    client = APIClient()
    client.force_authenticate(account)
    return client


@pytest.mark.django_db
def test_student_edits_only_own_allowed_data_and_is_audited():
    brazil = Country.objects.create(code="BR", name="Brasil")
    rs = FederativeUnit.objects.create(
        country=brazil, code="RS", name="Rio Grande do Sul", ibge_code="43"
    )
    sc = FederativeUnit.objects.create(
        country=brazil, code="SC", name="Santa Catarina", ibge_code="42"
    )
    account, person = account_with_person("student-owner")
    other, other_person = account_with_person("student-other")
    RoleAssignment.objects.create(person=person, role="STUDENT", grant_reason="TEST")
    student = StudentProfile.objects.create(
        person=person, display_name="Antes", city="Porto Alegre", uf=rs, data_mode=DataMode.REAL
    )
    StudentProfile.objects.create(
        person=other_person,
        display_name="Outro",
        city="Florianópolis",
        uf=sc,
        data_mode=DataMode.REAL,
    )

    response = authenticated(account).patch(
        "/api/v1/account/me/",
        {
            "phone": "+5551999999999",
            "student_display_name": "Depois",
            "student_city": "Caxias do Sul",
            "student_uf": "RS",
            "intended_category": "B",
        },
        format="json",
    )

    assert response.status_code == 200
    student.refresh_from_db()
    other_person.student_profile.refresh_from_db()
    assert (student.display_name, student.city) == ("Depois", "Caxias do Sul")
    assert other_person.student_profile.display_name == "Outro"
    assert AuditEvent.objects.filter(
        actor=account, action="account.own_data.updated", target_id=account.id
    ).exists()


@pytest.mark.django_db
def test_critical_account_fields_are_rejected_and_unchanged():
    account, person = account_with_person("protected-owner")
    response = authenticated(account).patch(
        "/api/v1/account/me/",
        {"roles": ["ADMIN"], "publication_status": "APPROVED", "plan": "PRO"},
        format="json",
    )
    assert response.status_code == 400
    assert not person.role_assignments.exists()


@pytest.mark.django_db
def test_sensitive_instructor_edit_forces_reverification_and_unpublication():
    account, person = account_with_person("instructor-owner")
    RoleAssignment.objects.create(person=person, role="INSTRUCTOR", grant_reason="TEST")
    profile = InstructorProfile.objects.create(
        person=person,
        display_name="Instrutora",
        categories=["B"],
        transmission_options=["MANUAL"],
        profile_status=InstructorProfile.Status.APPROVED,
        verification_status=InstructorProfile.VerificationStatus.VERIFIED,
        verified_until=timezone.now() + timedelta(days=30),
        publication_status=InstructorProfile.PublicationStatus.APPROVED,
    )

    response = authenticated(account).patch(
        "/api/v1/account/me/", {"categories": ["A", "B"]}, format="json"
    )

    assert response.status_code == 200
    profile.refresh_from_db()
    assert profile.profile_status == InstructorProfile.Status.UNDER_REVIEW
    assert profile.verification_status == InstructorProfile.VerificationStatus.PENDING
    assert profile.publication_status == InstructorProfile.PublicationStatus.UNPUBLISHED
    assert profile.verified_until is None
    assert ProfessionalVerification.objects.filter(
        profile=profile, provider="OWNER_EDIT", status="PENDING"
    ).exists()


@pytest.mark.django_db
def test_privacy_request_is_private_audited_and_does_not_delete_account():
    owner, _ = account_with_person("privacy-owner")
    other, _ = account_with_person("privacy-other")
    owner_client = authenticated(owner)
    response = owner_client.post(
        "/api/v1/privacy/requests/",
        {"request_type": "DELETION", "details": "Quero análise da exclusão."},
        format="json",
    )
    assert response.status_code == 201
    assert Account.objects.filter(pk=owner.pk).exists()
    row = PrivacyRequest.objects.get(pk=response.data["id"])
    assert row.status == PrivacyRequest.Status.OPEN
    assert AuditEvent.objects.filter(
        actor=owner, action="privacy.request.created", target_id=row.id
    ).exists()
    assert authenticated(other).get("/api/v1/privacy/requests/").data == []
    assert owner_client.get("/api/v1/privacy/requests/").data[0]["id"] == str(row.id)


@pytest.mark.django_db
def test_privacy_notice_is_public_minimal_and_versioned():
    response = APIClient().get("/api/v1/privacy/notice/")
    assert response.status_code == 200
    assert response.data["product"] == "InstrutorProCNH"
    assert response.data["controller_cnpj"] == "10.280.826/0001-05"
    assert response.data["privacy_contact"] == "focusgtba@gmail.com"
    assert "cpf" not in response.data
    assert "legal_representative" not in response.data


@pytest.mark.django_db
def test_admin_allowed_change_is_audited_and_critical_fields_are_read_only():
    administrator = Account.objects.create_superuser(
        username="privacy-admin",
        email="privacy-admin@example.invalid",
        password="safe-test-password",
    )
    affected, _ = account_with_person("admin-affected")
    request = RequestFactory().post("/admin/accounts/account/")
    request.user = administrator
    model_admin = AccountAdmin(Account, admin.site)
    assert {"email", "is_active", "is_staff"}.issubset(
        set(model_admin.get_readonly_fields(request, affected))
    )

    affected.first_name = "Nome corrigido"
    model_admin.save_model(request, affected, form=None, change=True)

    event = AuditEvent.objects.get(
        actor=administrator,
        action="accounts.account.admin_changed",
        target_id=affected.id,
    )
    assert event.metadata["before"]["first_name"] == ""
    assert event.metadata["after"]["first_name"] == "Nome corrigido"
