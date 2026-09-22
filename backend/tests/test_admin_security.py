from io import StringIO

import pytest
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django_otp.plugins.otp_static.models import StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, ProfessionalVerificationRequest
from apps.people.models import Person


@pytest.mark.django_db
def test_staff_can_access_admin_with_password_only(client):
    account = Account.objects.create_superuser(
        username="secure-admin", email="admin@example.invalid", password="strong-test-password"
    )
    response = client.post(
        reverse("admin:login"),
        {
            "username": account.username,
            "password": "strong-test-password",
            "next": reverse("admin:index"),
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("admin:index")
    assert AuditEvent.objects.filter(
        actor=account, action="accounts.admin.login_succeeded"
    ).exists()


@pytest.mark.django_db
def test_admin_accepts_unique_email(client):
    account = Account.objects.create_user(
        username="email-admin",
        email="email-admin@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    response = client.post(
        reverse("admin:login"),
        {
            "username": account.email.upper(),
            "password": "strong-test-password",
            "next": reverse("admin:index"),
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("admin:index")


@pytest.mark.django_db
def test_mfa_enrollment_is_one_time_and_audited():
    account = Account.objects.create_superuser(
        username="enroll-admin",
        email="enroll@example.invalid",
        password="strong-test-password",
    )
    output = StringIO()
    call_command("enroll_admin_mfa", account.username, stdout=output)
    assert "otpauth://totp/" in output.getvalue()
    assert TOTPDevice.objects.filter(user=account, confirmed=True).count() == 1
    assert StaticToken.objects.filter(device__user=account).count() == 10
    assert AuditEvent.objects.filter(action="accounts.admin_mfa_enrolled").count() == 1


@pytest.mark.django_db
def test_mfa_replacement_revokes_old_device_and_codes():
    account = Account.objects.create_superuser(
        username="replace-admin",
        email="replace@example.invalid",
        password="strong-test-password",
    )
    old_device = TOTPDevice.objects.create(user=account, name="old", confirmed=True)
    old_static = account.staticdevice_set.create(name="old recovery")
    StaticToken.objects.create(device=old_static, token="old-token")
    output = StringIO()
    call_command("enroll_admin_mfa", account.username, "--replace", stdout=output)
    assert not TOTPDevice.objects.filter(pk=old_device.pk).exists()
    assert TOTPDevice.objects.filter(user=account, confirmed=True).count() == 1
    assert StaticToken.objects.filter(device__user=account).count() == 10
    assert "Chave manual" in output.getvalue()
    assert AuditEvent.objects.filter(action="accounts.admin_mfa_rotated").count() == 1


@pytest.mark.django_db
def test_admin_login_form_has_no_otp_field(client):
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200
    assert set(response.context["form"].fields) == {"username", "password"}
    assert response.context["form"].fields["username"].label == "Usuário ou e-mail"


@pytest.mark.django_db
def test_admin_password_only_does_not_depend_on_mfa_setting(client):
    account = Account.objects.create_user(
        username="preproduction-reviewer",
        email="reviewer@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    response = client.post(
        reverse("admin:login"),
        {
            "username": account.username,
            "password": "strong-test-password",
            "next": reverse("admin:index"),
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("admin:index")


@pytest.mark.django_db
def test_admin_login_rejects_post_without_csrf_token():
    csrf_client = Client(enforce_csrf_checks=True)
    response = csrf_client.post(
        reverse("admin:login"),
        {"username": "unknown", "password": "not-a-password"},
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_rejects_invalid_password_with_generic_message_and_audit(client):
    Account.objects.create_user(
        username="valid-admin",
        email="valid-admin@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    response = client.post(
        reverse("admin:login"),
        {"username": "valid-admin", "password": "wrong-password"},
    )
    assert response.status_code == 200
    assert "Usuário/e-mail ou senha inválidos." in response.content.decode()
    event = AuditEvent.objects.get(action="accounts.admin.login_failed")
    assert event.actor is None
    assert event.metadata == {"identifier_supplied": True}


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("username", "is_staff", "is_active"),
    [("instructor", False, True), ("student", False, True), ("inactive-admin", True, False)],
)
def test_admin_denies_nonstaff_and_inactive_accounts(client, username, is_staff, is_active):
    account = Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="strong-test-password",
        is_staff=is_staff,
    )
    if not is_active:
        account.lifecycle_status = Account.LifecycleStatus.BLOCKED
        account.is_active = False
        account.save(update_fields=["lifecycle_status", "is_active"])
    response = client.post(
        reverse("admin:login"),
        {"username": username, "password": "strong-test-password"},
    )
    assert response.status_code == 200
    assert reverse("admin:index") not in response.headers.get("Location", "")


@pytest.mark.django_db
def test_admin_dashboard_and_logout_are_available_and_audited(client):
    account = Account.objects.create_superuser(
        username="dashboard-admin",
        email="dashboard@example.invalid",
        password="strong-test-password",
    )
    client.force_login(account)
    response = client.get(reverse("admin:index"))
    assert response.status_code == 200
    assert "Painel administrativo" in response.content.decode()
    assert "Verificação profissional" in response.content.decode()
    assert "/admin/payments/" not in response.content.decode()
    client.post(reverse("admin:logout"))
    assert AuditEvent.objects.filter(actor=account, action="accounts.admin.logout").exists()


@pytest.mark.django_db
def test_admin_login_rotates_session_and_applies_short_expiry(client):
    account = Account.objects.create_user(
        username="session-admin",
        email="session-admin@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    session = client.session
    session["pre_login_marker"] = True
    session.save()
    old_key = session.session_key
    response = client.post(
        reverse("admin:login"),
        {
            "username": account.username,
            "password": "strong-test-password",
            "next": reverse("admin:index"),
        },
    )
    assert response.status_code == 302
    assert client.session.session_key != old_key
    assert client.session.get_expiry_age() <= settings.ADMIN_SESSION_COOKIE_AGE
    assert settings.AXES_FAILURE_LIMIT == 5
    assert settings.AXES_COOLOFF_TIME == 1


@pytest.mark.django_db
def test_verification_queue_is_searchable_filterable_and_does_not_expose_cpf(client):
    owner = Account.objects.create_user(
        username="queue-owner",
        email="queue-owner@example.invalid",
        password="strong-test-password",
    )
    person = Person.objects.create(account=owner, cpf_last2="15")
    profile = InstructorProfile.objects.create(
        person=person, display_name="Instrutora da Fila", is_demo=False
    )
    ProfessionalVerificationRequest.objects.create(
        profile=profile,
        status=ProfessionalVerificationRequest.Status.SUBMITTED,
    )
    administrator = Account.objects.create_superuser(
        username="queue-admin",
        email="queue-admin@example.invalid",
        password="strong-test-password",
    )
    client.force_login(administrator)
    url = reverse("admin:discovery_professionalverificationrequest_changelist")
    response = client.get(url, {"q": "Instrutora", "status__exact": "SUBMITTED"})
    content = response.content.decode()
    assert response.status_code == 200
    assert "Instrutora da Fila" in content
    assert "Enviada" in content
    assert "529.982.247-25" not in content


@pytest.mark.django_db
def test_verification_transition_button_confirms_and_audits_review_start(client):
    owner = Account.objects.create_user(
        username="transition-owner",
        email="transition-owner@example.invalid",
        password="strong-test-password",
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner),
        display_name="Instrutor em Transição",
        is_demo=False,
    )
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile,
        status=ProfessionalVerificationRequest.Status.SUBMITTED,
    )
    analyst = Account.objects.create_user(
        username="transition-analyst",
        email="transition-analyst@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    analyst.user_permissions.add(
        Permission.objects.get(codename="review_professional_verification")
    )
    client.force_login(analyst)
    url = reverse(
        "admin:discovery_verification_request_transition", args=[item.pk, "start"]
    )
    assert client.get(url).status_code == 200
    assert client.post(url).status_code == 302
    item.refresh_from_db()
    assert item.status == ProfessionalVerificationRequest.Status.UNDER_REVIEW
    assert item.reviewer == analyst
    assert AuditEvent.objects.filter(
        action="discovery.professional_verification.review_started", target_id=item.pk
    ).exists()


@pytest.mark.django_db
def test_admin_groups_are_idempotent_and_do_not_create_or_elevate_users():
    before = Account.objects.count()
    call_command("configure_admin_groups")
    call_command("configure_admin_groups")
    assert Account.objects.count() == before
    analyst = Group.objects.get(name="Analista de verificação")
    support = Group.objects.get(name="Suporte")
    assert analyst.permissions.filter(codename="review_professional_verification").exists()
    assert not support.permissions.filter(codename="reveal_protected_identifier").exists()


@pytest.mark.django_db
def test_admin_prod_access_grants_only_explicit_permissions():
    account = Account.objects.create_user(
        username="controlled-admin",
        email="controlled@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    call_command("grant_admin_prod_access", account.username)
    granted = set(account.user_permissions.values_list("codename", flat=True))
    assert granted == {
        "manage_platform_organization",
        "validate_platform_organization",
        "manage_instructor_publication",
        "review_professional_verification",
        "reveal_protected_identifier",
        "view_security_audit",
    }
    assert granted < set(Permission.objects.values_list("codename", flat=True))
    assert AuditEvent.objects.filter(action="accounts.admin_prod_access_granted").count() == 1


@pytest.mark.django_db
def test_recovery_code_rotation_revokes_previous_codes_and_is_audited():
    account = Account.objects.create_user(
        username="rotate-admin",
        email="rotate@example.invalid",
        password="strong-test-password",
        is_staff=True,
    )
    TOTPDevice.objects.create(user=account, name="test", confirmed=True)
    old_device = account.staticdevice_set.create(name="old")
    old_token = StaticToken.objects.create(device=old_device, token="old-token")
    output = StringIO()
    call_command("rotate_admin_recovery_codes", account.username, stdout=output)
    assert not StaticToken.objects.filter(pk=old_token.pk).exists()
    assert StaticToken.objects.filter(device__user=account).count() == 10
    assert "old-token" not in output.getvalue()
    assert (
        AuditEvent.objects.filter(action="accounts.admin_mfa_recovery_codes_rotated").count() == 1
    )
