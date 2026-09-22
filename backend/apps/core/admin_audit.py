from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from apps.audit.models import AuditEvent


def _is_admin_request(request):
    return bool(request and request.path.startswith("/admin/"))


def _request_id(request):
    return getattr(request, "request_id", None) if request else None


@receiver(user_logged_in, dispatch_uid="instrutorpro_admin_login_audit")
def audit_admin_login(sender, request, user, **kwargs):
    if _is_admin_request(request) and user.is_staff:
        AuditEvent.objects.create(
            actor=user,
            action="accounts.admin.login_succeeded",
            target_type="accounts.Account",
            target_id=user.pk,
            request_id=_request_id(request),
        )


@receiver(user_login_failed, dispatch_uid="instrutorpro_admin_login_failed_audit")
def audit_admin_login_failed(sender, credentials, request, **kwargs):
    if _is_admin_request(request):
        AuditEvent.objects.create(
            action="accounts.admin.login_failed",
            target_type="accounts.Account",
            request_id=_request_id(request),
            reason_code="INVALID_CREDENTIALS",
            metadata={"identifier_supplied": bool(credentials.get("username"))},
        )


@receiver(user_logged_out, dispatch_uid="instrutorpro_admin_logout_audit")
def audit_admin_logout(sender, request, user, **kwargs):
    if _is_admin_request(request) and user and user.is_staff:
        AuditEvent.objects.create(
            actor=user,
            action="accounts.admin.logout",
            target_type="accounts.Account",
            target_id=user.pk,
            request_id=_request_id(request),
        )
