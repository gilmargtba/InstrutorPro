from django_otp.admin import OTPAdminSite


class InstrutorProOTPAdminSite(OTPAdminSite):
    site_header = "Administração InstrutorPro"
    site_title = "Admin InstrutorPro"
    index_title = "Painel administrativo — MFA obrigatório"
