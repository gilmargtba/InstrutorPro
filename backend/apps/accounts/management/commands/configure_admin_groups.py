from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

GROUP_PERMISSIONS = {
    "Administrador da plataforma": {
        "accounts.view_account",
        "audit.view_auditevent",
        "organizations.manage_platform_organization",
        "organizations.validate_platform_organization",
        "discovery.view_instructorprofile",
        "discovery.change_instructorprofile",
        "discovery.view_professionalverificationrequest",
        "discovery.change_professionalverificationrequest",
        "discovery.manage_instructor_publication",
        "discovery.review_professional_verification",
        "discovery.reveal_protected_identifier",
        "audit.view_security_audit",
        "marketplace.view_instructoroffer",
        "privacy.manage_privacy_requests",
    },
    "Analista de verificação": {
        "discovery.view_instructorprofile",
        "discovery.view_professionalverificationrequest",
        "discovery.change_professionalverificationrequest",
        "discovery.review_professional_verification",
        "discovery.reveal_protected_identifier",
    },
    "Suporte": {
        "accounts.view_account",
        "discovery.view_instructorprofile",
        "discovery.view_professionalverificationrequest",
        "audit.view_security_audit",
    },
}


class Command(BaseCommand):
    help = "Cria grupos administrativos de menor privilégio sem criar ou elevar usuários."

    def handle(self, *args, **options):
        for group_name, labels in GROUP_PERMISSIONS.items():
            permissions = []
            for label in sorted(labels):
                app_label, codename = label.split(".", 1)
                try:
                    permission = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
                except Permission.DoesNotExist as exc:
                    raise CommandError(f"Permissão não encontrada: {label}") from exc
                permissions.append(permission)
            group, _ = Group.objects.get_or_create(name=group_name)
            group.permissions.set(permissions)
            self.stdout.write(f"{group_name}={len(permissions)} permissões")
        self.stdout.write(self.style.SUCCESS("ADMIN_GROUPS_CONFIGURED=YES"))
