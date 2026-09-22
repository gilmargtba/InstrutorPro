from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import Account


class Command(BaseCommand):
    help = "Exibe estado e permissões de uma conta administrativa sem revelar segredos."

    def add_arguments(self, parser):
        parser.add_argument("identifier")

    def handle(self, *args, **options):
        identifier = options["identifier"].strip()
        account = Account.objects.filter(username=identifier).first()
        if account is None:
            account = Account.objects.filter(email__iexact=identifier).first()
        if account is None:
            raise CommandError("Conta não encontrada")
        permissions = sorted(account.get_all_permissions())
        self.stdout.write(f"ADMIN_USERNAME={account.username}")
        self.stdout.write(f"ADMIN_ACTIVE={str(account.is_active).lower()}")
        self.stdout.write(f"ADMIN_LIFECYCLE={account.lifecycle_status}")
        self.stdout.write(f"ADMIN_STAFF={str(account.is_staff).lower()}")
        self.stdout.write(f"ADMIN_SUPERUSER={str(account.is_superuser).lower()}")
        self.stdout.write("ADMIN_GROUPS=" + ",".join(account.groups.values_list("name", flat=True)))
        self.stdout.write("ADMIN_PERMISSIONS=" + ",".join(permissions))
