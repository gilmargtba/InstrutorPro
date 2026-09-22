from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.management.commands.configure_admin_groups import GROUP_PERMISSIONS
from apps.accounts.models import Account
from apps.audit.models import AuditEvent


class Command(BaseCommand):
    help = "Associa explicitamente uma conta staff ativa a um grupo administrativo existente."

    def add_arguments(self, parser):
        parser.add_argument("identifier")
        parser.add_argument("group", choices=sorted(GROUP_PERMISSIONS))

    @transaction.atomic
    def handle(self, *args, **options):
        identifier = options["identifier"].strip()
        account = Account.objects.filter(username=identifier).first()
        if account is None:
            account = Account.objects.filter(email__iexact=identifier).first()
        if account is None:
            raise CommandError("Conta não encontrada")
        if not account.is_staff or not account.can_operate:
            raise CommandError("A conta deve ser staff ativa")
        try:
            group = Group.objects.get(name=options["group"])
        except Group.DoesNotExist as exc:
            raise CommandError("Execute configure_admin_groups primeiro") from exc
        added = not account.groups.filter(pk=group.pk).exists()
        account.groups.add(group)
        if added:
            AuditEvent.objects.create(
                actor=account,
                action="accounts.admin_group.assigned",
                target_type="accounts.Account",
                target_id=account.pk,
                reason_code="OWNER_AUTHORIZED_ADMIN_ACCESS",
                metadata={"group": group.name},
            )
        self.stdout.write(f"ADMIN_GROUP_ASSIGNED={str(added).lower()}")
        self.stdout.write(f"ADMIN_USERNAME={account.username}")
        self.stdout.write(f"ADMIN_GROUP={group.name}")
        self.stdout.write(f"ADMIN_SUPERUSER={str(account.is_superuser).lower()}")
