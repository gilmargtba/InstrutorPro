import pytest
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError
from django.urls import reverse

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.organizations.models import PlatformOrganization
from apps.organizations.services import (
    OrganizationPermissionDenied,
    OrganizationValidationError,
    OrganizationVersionConflict,
    save_platform_organization,
    validate_platform_organization,
)
from apps.organizations.validators import validate_cnpj

COMPLETE_DATA = {
    "cnpj": "00.000.000/0001-91",
    "legal_name": "Organização Sintética Ltda",
    "trade_name": "Organização Sintética",
    "business_address": "Endereço empresarial sintético, 100",
    "legal_representative": "Responsável Sintético",
    "operational_contact": "operacao@example.invalid",
    "privacy_contact": "privacidade@example.invalid",
    "phone": "",
    "dpo_name": "",
    "dpo_contact": "",
    "dpo_appointment_reference": "",
}


def actor_with_permission(codename, username):
    actor = Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="test-only",
        is_staff=True,
    )
    actor.user_permissions.add(
        Permission.objects.get(content_type__app_label="organizations", codename=codename)
    )
    return actor


@pytest.mark.django_db
def test_cnpj_accepts_formatted_valid_value_and_rejects_invalid_value():
    validate_cnpj("00.000.000/0001-91")
    with pytest.raises(ValidationError, match="CNPJ válido"):
        validate_cnpj("11.111.111/1111-11")


@pytest.mark.django_db
def test_manager_creates_incomplete_configuration_and_audit_is_minimized():
    manager = actor_with_permission("manage_platform_organization", "organization-manager")

    organization = save_platform_organization(
        actor=manager,
        data={"cnpj": "00.000.000/0001-91", "privacy_contact": "privacy@example.invalid"},
        expected_version=0,
        reason="TEST_CREATE",
    )

    assert organization.cnpj == "00000000000191"
    assert organization.validation_status == PlatformOrganization.ValidationStatus.INCOMPLETE
    event = AuditEvent.objects.get(action="organizations.platform_organization_created")
    assert event.actor == manager
    assert event.metadata["after"]["cnpj"] == "**********0191"
    assert event.metadata["after"]["privacy_contact"] == "[REDACTED]"
    assert "privacy@example.invalid" not in str(event.metadata)


@pytest.mark.django_db
def test_complete_configuration_is_pending_until_separate_human_validation():
    manager = actor_with_permission("manage_platform_organization", "organization-editor")

    organization = save_platform_organization(
        actor=manager,
        data=COMPLETE_DATA,
        expected_version=0,
        reason="TEST_COMPLETE_CREATE",
    )

    assert (
        organization.validation_status == PlatformOrganization.ValidationStatus.PENDING_VALIDATION
    )
    assert organization.validated_at is None
    assert organization.validated_by is None


@pytest.mark.django_db
def test_validation_requires_explicit_permission_and_complete_fields():
    manager = actor_with_permission("manage_platform_organization", "manager-only")
    validator = actor_with_permission("validate_platform_organization", "validator-only")
    organization = save_platform_organization(
        actor=manager,
        data={"cnpj": "00.000.000/0001-91"},
        expected_version=0,
        reason="TEST_INCOMPLETE",
    )

    with pytest.raises(OrganizationPermissionDenied):
        validate_platform_organization(
            actor=manager,
            organization=organization,
            expected_version=organization.version,
            reason="TEST_WRONG_PERMISSION",
        )
    with pytest.raises(OrganizationValidationError, match="campos obrigatórios"):
        validate_platform_organization(
            actor=validator,
            organization=organization,
            expected_version=organization.version,
            reason="TEST_INCOMPLETE_VALIDATION",
        )


@pytest.mark.django_db
def test_validation_and_later_edit_are_versioned_and_audited():
    manager = actor_with_permission("manage_platform_organization", "organization-maintainer")
    validator = actor_with_permission("validate_platform_organization", "organization-validator")
    organization = save_platform_organization(
        actor=manager,
        data=COMPLETE_DATA,
        expected_version=0,
        reason="TEST_CREATE_PENDING",
    )

    organization = validate_platform_organization(
        actor=validator,
        organization=organization,
        expected_version=organization.version,
        reason="TEST_MANUAL_VALIDATION",
    )
    validated_version = organization.version
    assert organization.validation_status == PlatformOrganization.ValidationStatus.VALIDATED
    assert organization.validated_by == validator
    assert organization.validated_at is not None

    changed = {**COMPLETE_DATA, "trade_name": "Nome alterado"}
    organization = save_platform_organization(
        actor=manager,
        organization=organization,
        data=changed,
        expected_version=validated_version,
        reason="TEST_EDIT_AFTER_VALIDATION",
    )
    assert (
        organization.validation_status == PlatformOrganization.ValidationStatus.PENDING_VALIDATION
    )
    assert organization.validated_by is None
    assert organization.validated_at is None
    assert (
        AuditEvent.objects.filter(action="organizations.platform_organization_validated").count()
        == 1
    )
    update_event = AuditEvent.objects.get(action="organizations.platform_organization_updated")
    assert update_event.metadata["changed_fields"] == ["trade_name"]
    assert update_event.metadata["before"]["status"] == "VALIDATED"
    assert update_event.metadata["after"]["status"] == "PENDING_VALIDATION"


@pytest.mark.django_db
def test_stale_update_and_second_controller_are_rejected():
    manager = actor_with_permission("manage_platform_organization", "concurrency-manager")
    organization = save_platform_organization(
        actor=manager,
        data=COMPLETE_DATA,
        expected_version=0,
        reason="TEST_CREATE",
    )
    with pytest.raises(OrganizationVersionConflict, match="outra sessão"):
        save_platform_organization(
            actor=manager,
            organization=organization,
            data={**COMPLETE_DATA, "trade_name": "Stale"},
            expected_version=organization.version + 1,
            reason="TEST_STALE",
        )
    with pytest.raises(OrganizationVersionConflict, match="já foi criada"):
        save_platform_organization(
            actor=manager,
            data=COMPLETE_DATA,
            expected_version=0,
            reason="TEST_SECOND",
        )
    with pytest.raises(IntegrityError):
        PlatformOrganization.objects.create(singleton_key=1)


@pytest.mark.django_db
def test_superuser_without_explicit_permission_is_denied_by_policy():
    superuser = Account.objects.create_superuser(
        username="implicit-superuser",
        email="implicit-superuser@example.invalid",
        password="test-only",
    )
    with pytest.raises(OrganizationPermissionDenied):
        save_platform_organization(
            actor=superuser,
            data=COMPLETE_DATA,
            expected_version=0,
            reason="TEST_DENY_DEFAULT",
        )


@pytest.mark.django_db
def test_admin_reuses_existing_panel_and_denies_staff_without_permission(client):
    unauthorized = Account.objects.create_user(
        username="unauthorized-staff",
        email="unauthorized-staff@example.invalid",
        password="test-only",
        is_staff=True,
    )
    client.force_login(unauthorized)
    response = client.get(reverse("admin:organizations_platformorganization_changelist"))
    assert response.status_code == 403

    manager = actor_with_permission("manage_platform_organization", "admin-manager")
    client.force_login(manager)
    add_response = client.get(reverse("admin:organizations_platformorganization_add"))
    assert add_response.status_code == 200
    assert "Organização / Controlador" in add_response.content.decode()


@pytest.mark.django_db
def test_admin_can_save_pending_configuration_without_public_api(client):
    manager = actor_with_permission("manage_platform_organization", "admin-editor")
    client.force_login(manager)
    response = client.post(
        reverse("admin:organizations_platformorganization_add"),
        {**COMPLETE_DATA, "expected_version": 0, "_save": "Salvar"},
    )
    assert response.status_code == 302, response.context["adminform"].form.errors
    organization = PlatformOrganization.objects.get()
    assert (
        organization.validation_status == PlatformOrganization.ValidationStatus.PENDING_VALIDATION
    )

    public_response = client.get("/api/v1/organizations/")
    assert public_response.status_code == 404
    assert organization.cnpj.encode() not in public_response.content


@pytest.mark.django_db
def test_validator_can_validate_from_admin_action_without_edit_permission(client):
    manager = actor_with_permission("manage_platform_organization", "admin-save-manager")
    validator = actor_with_permission("validate_platform_organization", "admin-validator")
    organization = save_platform_organization(
        actor=manager,
        data=COMPLETE_DATA,
        expected_version=0,
        reason="TEST_ADMIN_ACTION_SETUP",
    )

    client.force_login(validator)
    response = client.post(
        reverse("admin:organizations_platformorganization_changelist"),
        {
            "action": "validate_selected",
            "_selected_action": [str(organization.pk)],
            "index": 0,
        },
    )

    assert response.status_code == 302
    organization.refresh_from_db()
    assert organization.validation_status == PlatformOrganization.ValidationStatus.VALIDATED
    assert organization.validated_by == validator
    assert AuditEvent.objects.filter(
        action="organizations.platform_organization_validated", actor=validator
    ).exists()


@pytest.mark.django_db
def test_bootstrap_command_grants_only_explicit_organization_permissions():
    account = Account.objects.create_user(
        username="real-admin-placeholder",
        email="real-admin-placeholder@example.invalid",
        password="test-only",
        is_staff=True,
    )

    call_command("grant_organization_admin", account.username)

    granted = set(
        account.user_permissions.filter(content_type__app_label="organizations").values_list(
            "codename", flat=True
        )
    )
    assert granted == {
        "manage_platform_organization",
        "validate_platform_organization",
    }
    event = AuditEvent.objects.get(action="organizations.platform_organization_permissions_granted")
    assert event.actor is None
    assert event.target_id == account.id
