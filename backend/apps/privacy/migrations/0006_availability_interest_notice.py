from django.db import migrations
from django.utils import timezone


NEW_VERSION = "2026-11-13"


def publish_interest_notice(apps, schema_editor):
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
    PrivacyNotice.objects.filter(version="2026-10-21").update(is_current=True)


class Migration(migrations.Migration):
    dependencies = [("privacy", "0005_google_maps_privacy_notice")]

    operations = [migrations.RunPython(publish_interest_notice, restore_previous_notice)]
