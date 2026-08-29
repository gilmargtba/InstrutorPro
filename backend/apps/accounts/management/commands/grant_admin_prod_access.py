from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Account
from apps.audit.models import AuditEvent

PERMISSIONS = (
    ("organizations", "manage_platform_organization"),
    ("organizations", "validate_platform_organization"),
    ("discovery", "manage_instructor_publication"),
    ("audit", "view_security_audit"),
)


class Command(BaseCommand):
    help = "Grant the explicit ADMIN-PROD-01 permissions to an existing active staff account"

    def add_arguments(self, parser):
        parser.add_argument("username")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            account = Account.objects.get(username=options["username"])
        except Account.DoesNotExist as exc:
            raise CommandError("Conta não encontrada") from exc
        if not account.is_staff or not account.can_operate:
            raise CommandError("A conta deve ser staff ativa")

        permissions = [
            Permission.objects.get(content_type__app_label=app, codename=codename)
            for app, codename in PERMISSIONS
        ]
        account.user_permissions.add(*permissions)
        AuditEvent.objects.create(
            actor=account,
            action="accounts.admin_prod_access_granted",
            target_type="accounts.Account",
            target_id=account.id,
            reason_code="ADMIN_PROD_01",
            metadata={"permissions": [f"{app}.{code}" for app, code in PERMISSIONS]},
        )
        self.stdout.write(self.style.SUCCESS("Permissões ADMIN-PROD-01 concedidas e auditadas"))
