from django.core.management.base import BaseCommand

from apps.organizations.models import PlatformOrganization


class Command(BaseCommand):
    help = "Configure only the controller fields explicitly authorized for Fatia 5."

    def handle(self, *args, **options):
        organization, _ = PlatformOrganization.objects.get_or_create(singleton_key=1)
        organization.cnpj = organization.cnpj or "10280826000105"
        organization.privacy_contact = organization.privacy_contact or "focusgtba@gmail.com"
        organization.validation_status = PlatformOrganization.ValidationStatus.INCOMPLETE
        organization.validated_at = None
        organization.validated_by = None
        organization.save()
        self.stdout.write("ORGANIZATION_CONFIG=INCOMPLETE")
