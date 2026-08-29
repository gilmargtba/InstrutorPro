from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import Account
from apps.audit.models import AuditEvent


class Command(BaseCommand):
    help = "Concede as permissões explícitas de configuração e validação da organização."

    def add_arguments(self, parser):
        parser.add_argument("username")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        try:
            account = Account.objects.select_for_update().get(username=username)
        except Account.DoesNotExist as exc:
            raise CommandError("Conta não encontrada.") from exc
        if not account.is_staff or not account.can_operate:
            raise CommandError("A conta deve ser administrativa e estar ativa.")

        permissions = list(
            Permission.objects.filter(
                content_type__app_label="organizations",
                codename__in=(
                    "manage_platform_organization",
                    "validate_platform_organization",
                ),
            )
        )
        if len(permissions) != 2:
            raise CommandError("Permissões organizacionais não encontradas; aplique as migrations.")
        account.user_permissions.add(*permissions)
        AuditEvent.objects.create(
            action="organizations.platform_organization_permissions_granted",
            target_type="accounts.Account",
            target_id=account.id,
            reason_code="LOCAL_ADMIN_BOOTSTRAP",
            metadata={"permissions": sorted(permission.codename for permission in permissions)},
        )
        self.stdout.write(self.style.SUCCESS("Permissões organizacionais concedidas."))
