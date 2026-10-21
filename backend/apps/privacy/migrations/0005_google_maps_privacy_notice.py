from django.db import migrations
from django.utils import timezone


NEW_VERSION = "2026-10-21"
PREVIOUS_VERSION = "2026-09-16"


def publish_google_maps_notice(apps, schema_editor):
    PrivacyNotice = apps.get_model("privacy", "PrivacyNotice")
    PrivacyNotice.objects.filter(is_current=True).update(is_current=False)
    PrivacyNotice.objects.update_or_create(
        version=NEW_VERSION,
        defaults={
            "title": "Política de Privacidade e Proteção de Dados",
            "published_at": timezone.now(),
            "is_current": True,
        },
    )


def restore_previous_notice(apps, schema_editor):
    PrivacyNotice = apps.get_model("privacy", "PrivacyNotice")
    PrivacyNotice.objects.filter(version=NEW_VERSION, is_current=True).update(is_current=False)
    PrivacyNotice.objects.filter(version=PREVIOUS_VERSION).update(is_current=True)


class Migration(migrations.Migration):
    dependencies = [("privacy", "0004_alter_legalacceptancerecord_options_and_more")]

    operations = [
        migrations.RunPython(publish_google_maps_notice, restore_previous_notice),
    ]
