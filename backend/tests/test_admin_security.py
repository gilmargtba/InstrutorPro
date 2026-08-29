from io import StringIO

import pytest
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_static.models import StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Account
from apps.audit.models import AuditEvent


@pytest.mark.django_db
def test_admin_requires_mfa_even_for_staff_superuser(client):
    account = Account.objects.create_superuser(
        username="secure-admin", email="admin@example.invalid", password="strong-test-password"
    )
    client.force_login(account)
    response = client.get(reverse("admin:index"))
    assert response.status_code == 302
    assert reverse("admin:login") in response.url


@pytest.mark.django_db
def test_verified_totp_session_can_access_admin(client):
    account = Account.objects.create_superuser(
        username="otp-admin", email="otp@example.invalid", password="strong-test-password"
    )
    device = TOTPDevice.objects.create(user=account, name="test", confirmed=True)
    client.force_login(account)
    session = client.session
    session[DEVICE_ID_SESSION_KEY] = device.persistent_id
    session.save()
    assert client.get(reverse("admin:index")).status_code == 200


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
def test_admin_login_form_requests_otp(client):
    response = client.get(reverse("admin:login"))
    assert response.status_code == 200
    assert "otp_token" in response.context["form"].fields


@pytest.mark.django_db
def test_admin_login_rejects_post_without_csrf_token():
    csrf_client = Client(enforce_csrf_checks=True)
    response = csrf_client.post(
        reverse("admin:login"),
        {"username": "unknown", "password": "not-a-password", "otp_token": "000000"},
    )
    assert response.status_code == 403


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
