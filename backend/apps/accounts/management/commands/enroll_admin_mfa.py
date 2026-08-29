from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Account
from apps.audit.models import AuditEvent


class Command(BaseCommand):
    help = "Enroll an existing active staff account in TOTP MFA and issue recovery codes"

    def add_arguments(self, parser):
        parser.add_argument("username")

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist as exc:
            raise CommandError("Conta não encontrada") from exc
        if not account.is_staff or not account.can_operate or not account.has_usable_password():
            raise CommandError("A conta deve ser staff ativa e possuir senha utilizável")
        if TOTPDevice.objects.filter(user=account, confirmed=True).exists():
            raise CommandError("A conta já possui dispositivo TOTP confirmado")

        device = TOTPDevice.objects.create(user=account, name="InstrutorPro Admin", confirmed=True)
        recovery = StaticDevice.objects.create(user=account, name="Códigos de recuperação")
        recovery_codes = []
        for _ in range(10):
            token = StaticToken.random_token()
            StaticToken.objects.create(device=recovery, token=token)
            recovery_codes.append(token)

        AuditEvent.objects.create(
            actor=account,
            action="accounts.admin_mfa_enrolled",
            target_type="accounts.Account",
            target_id=account.id,
            reason_code="ADMIN_PROD_01",
            metadata={"method": "TOTP", "recovery_codes_issued": len(recovery_codes)},
        )
        self.stdout.write("Escaneie esta configuração no aplicativo autenticador:")
        self.stdout.write(device.config_url)
        self.stdout.write("\nCódigos de recuperação (guarde offline; exibidos uma única vez):")
        for token in recovery_codes:
            self.stdout.write(token)
