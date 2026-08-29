from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.accounts.models import Account
from apps.audit.models import AuditEvent


class Command(BaseCommand):
    help = "Revoke existing admin MFA recovery codes and issue ten replacements"

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
        if not TOTPDevice.objects.filter(user=account, confirmed=True).exists():
            raise CommandError("A conta não possui dispositivo TOTP confirmado")

        previous_count = StaticToken.objects.filter(device__user=account).count()
        StaticDevice.objects.filter(user=account).delete()
        recovery = StaticDevice.objects.create(user=account, name="Códigos de recuperação")
        replacement_codes = []
        for _ in range(10):
            token = StaticToken.random_token()
            StaticToken.objects.create(device=recovery, token=token)
            replacement_codes.append(token)

        AuditEvent.objects.create(
            actor=account,
            action="accounts.admin_mfa_recovery_codes_rotated",
            target_type="accounts.Account",
            target_id=account.id,
            reason_code="ADMIN_PROD_01",
            metadata={"revoked_count": previous_count, "replacement_count": 10},
        )
        self.stdout.write("Novos códigos de recuperação (guarde offline; exibidos uma única vez):")
        for token in replacement_codes:
            self.stdout.write(token)
