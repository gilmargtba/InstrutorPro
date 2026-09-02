from django.conf import settings
from django.contrib.admin import AdminSite
from django_otp.admin import OTPAdminSite


class InstrutorProOTPAdminSite(OTPAdminSite):
    site_header = "Administração InstrutorProCNH"
    site_title = "Admin InstrutorProCNH"
    index_title = "Painel administrativo"

    @property
    def login_form(self):
        if settings.ADMIN_MFA_REQUIRED:
            return OTPAdminSite.login_form
        return None

    @property
    def login_template(self):
        if settings.ADMIN_MFA_REQUIRED:
            return OTPAdminSite.login_template
        return None

    def has_permission(self, request):
        if settings.ADMIN_MFA_REQUIRED:
            return OTPAdminSite.has_permission(self, request)
        return AdminSite.has_permission(self, request)
