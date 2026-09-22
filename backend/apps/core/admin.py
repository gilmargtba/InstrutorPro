from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import get_user_model


class AdminUsernameEmailAuthenticationForm(AdminAuthenticationForm):
    """Password-only Admin login accepting the account username or unique email."""

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": "Usuário/e-mail ou senha inválidos.",
        "inactive": "Usuário/e-mail ou senha inválidos.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].label = "Usuário ou e-mail"

    def clean(self):
        identifier = (self.cleaned_data.get("username") or "").strip()
        if "@" in identifier:
            matches = list(
                get_user_model()
                .objects.filter(email__iexact=identifier)
                .values_list("username", flat=True)[:2]
            )
            if len(matches) == 1:
                self.cleaned_data["username"] = matches[0]
        return super().clean()


class InstrutorProAdminSite(AdminSite):
    site_header = "Administração InstrutorProCNH"
    site_title = "Admin InstrutorProCNH"
    index_title = "Painel administrativo"

    login_form = AdminUsernameEmailAuthenticationForm
    index_template = "admin/instrutorpro_index.html"

    def has_permission(self, request):
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
            and getattr(request.user, "can_operate", False)
        )

    def login(self, request, extra_context=None):
        response = super().login(request, extra_context)
        if request.user.is_authenticated and request.user.is_staff:
            request.session.set_expiry(settings.ADMIN_SESSION_COOKIE_AGE)
        return response

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)
        if not settings.REAL_PAYMENTS:
            app_list = [app for app in app_list if app["app_label"] != "payments"]
        business_names = {
            "discovery": "Instrutores e publicação",
            "marketplace": "Marketplace",
            "privacy": "Privacidade",
            "audit": "Sistema e auditoria",
            "accounts": "Acessos",
            "organizations": "Organização",
        }
        priority = {name: index for index, name in enumerate(business_names)}
        for app in app_list:
            app["name"] = business_names.get(app["app_label"], app["name"])
        return sorted(app_list, key=lambda app: priority.get(app["app_label"], 99))

    def index(self, request, extra_context=None):
        from apps.discovery.models import InstructorProfile, ProfessionalVerificationRequest

        requests = ProfessionalVerificationRequest.objects.all()
        counts = {
            "instructors": InstructorProfile.objects.count(),
            "pending": requests.filter(status=requests.model.Status.SUBMITTED).count(),
            "under_review": requests.filter(status=requests.model.Status.UNDER_REVIEW).count(),
            "verified": InstructorProfile.objects.filter(
                verification_status=InstructorProfile.VerificationStatus.VERIFIED
            ).count(),
            "published": InstructorProfile.objects.filter(
                publication_status=InstructorProfile.PublicationStatus.APPROVED
            ).count(),
            "rejected": requests.filter(status=requests.model.Status.REJECTED).count(),
        }
        return super().index(request, {**(extra_context or {}), "business_counts": counts})
