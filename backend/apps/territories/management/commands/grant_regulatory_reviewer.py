from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Concede permissão de revisão à conta administrativa existente, sem criá-la."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("--apply", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        if username != getattr(settings, "REGULATORY_RESPONSIBLE_ADMIN", "gilmar"):
            raise CommandError("Somente a conta responsável designada pode receber esta permissão.")
        try:
            account = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist as exc:
            raise CommandError("Conta existente não encontrada; nada foi alterado.") from exc
        if not account.is_staff or not account.can_operate:
            raise CommandError("A conta deve ser administrativa, ativa e operacional.")
        permissions = list(
            Permission.objects.filter(
                content_type__app_label="territories",
                content_type__model__in=["regulatoryreadiness", "federativeunit"],
                codename__in=[
                    "change_regulatoryreadiness",
                    "view_regulatoryreadiness",
                    "view_federativeunit",
                ],
            )
        )
        if len(permissions) != 3:
            raise CommandError("Permissões esperadas não encontradas; aplique migrations antes.")
        self.stdout.write(f"ACCOUNT={account.username} IS_STAFF={account.is_staff} PERMISSIONS=3")
        if not options["apply"]:
            self.stdout.write("DRY_RUN=YES; use --apply para conceder as permissões.")
            return
        account.user_permissions.add(*permissions)
        self.stdout.write("REGULATORY_REVIEW_PERMISSION=GRANTED PASSWORD_CHANGED=NO")
