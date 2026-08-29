from django.contrib.admin.apps import AdminConfig


class InstrutorProAdminConfig(AdminConfig):
    default_site = "apps.core.admin.InstrutorProOTPAdminSite"
