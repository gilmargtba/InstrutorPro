from urllib.parse import parse_qs, urlparse

import segno
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
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Revoke the existing TOTP device and recovery codes before enrolling again",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        try:
            account = Account.objects.get(username=username)
        except Account.DoesNotExist as exc:
            raise CommandError("Conta não encontrada") from exc
        if not account.is_staff or not account.can_operate or not account.has_usable_password():
            raise CommandError("A conta deve ser staff ativa e possuir senha utilizável")
        existing = TOTPDevice.objects.filter(user=account, confirmed=True)
        if existing.exists() and not options["replace"]:
            raise CommandError("A conta já possui dispositivo TOTP confirmado")

        replaced_devices = existing.count()
        if options["replace"]:
            TOTPDevice.objects.filter(user=account).delete()
            StaticDevice.objects.filter(user=account).delete()

        device = TOTPDevice.objects.create(user=account, name="InstrutorPro Admin", confirmed=True)
        recovery = StaticDevice.objects.create(user=account, name="Códigos de recuperação")
        recovery_codes = []
        for _ in range(10):
            token = StaticToken.random_token()
            StaticToken.objects.create(device=recovery, token=token)
            recovery_codes.append(token)

        AuditEvent.objects.create(
            actor=account,
            action=(
                "accounts.admin_mfa_rotated"
                if options["replace"]
                else "accounts.admin_mfa_enrolled"
            ),
            target_type="accounts.Account",
            target_id=account.id,
            reason_code="ADMIN_PROD_01",
            metadata={
                "method": "TOTP",
                "replaced_devices": replaced_devices,
                "recovery_codes_issued": len(recovery_codes),
            },
        )
        manual_secret = parse_qs(urlparse(device.config_url).query)["secret"][0]
        self.stdout.write("Adicione uma conta TOTP no aplicativo autenticador.")
        self.stdout.write("Nome da conta: InstrutorPro Admin")
        self.stdout.write("Chave manual (sensível; não compartilhe):")
        self.stdout.write(manual_secret)
        self.stdout.write("URI alternativa (sensível; não compartilhe):")
        self.stdout.write(device.config_url)
        self.stdout.write("QR Code sensível — escaneie diretamente com o aplicativo:")
        segno.make(device.config_url).terminal(compact=True)
        self.stdout.write("\nCódigos de recuperação (guarde offline; exibidos uma única vez):")
        for token in recovery_codes:
            self.stdout.write(token)
