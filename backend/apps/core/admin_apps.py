from django.contrib.admin.apps import AdminConfig


class InstrutorProAdminConfig(AdminConfig):
    default_site = "apps.core.admin.InstrutorProAdminSite"

    def ready(self):
        super().ready()
        from . import admin_audit  # noqa: F401
