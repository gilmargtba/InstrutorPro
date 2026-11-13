from django.db import migrations


def prepare_disabled_interest_policy(apps, schema_editor):
    PrivacyNotice = apps.get_model("privacy", "PrivacyNotice")
    AvailabilityInterestPolicy = apps.get_model("marketplace", "AvailabilityInterestPolicy")
    notice = PrivacyNotice.objects.filter(version="2026-11-13").first()
    if notice:
        AvailabilityInterestPolicy.objects.get_or_create(
            pk=1,
            defaults={
                "enabled": False,
                "retention_days": 90,
                "privacy_notice": notice,
                "consent_version": "availability-interest-2026-11-13",
                "consent_text": (
                    "Autorizo a equipe InstrutorProCNH a usar meu nome, WhatsApp e localidade "
                    "para me avisar manualmente quando houver instrutor disponível "
                    "na área escolhida. "
                    "Posso retirar este pedido pelo canal de privacidade."
                ),
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("marketplace", "0018_availability_interest_scope"),
        ("privacy", "0007_availability_interest_notice"),
    ]

    operations = [migrations.RunPython(prepare_disabled_interest_policy, migrations.RunPython.noop)]
