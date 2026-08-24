from django.contrib import admin, messages

from .models import (
    InstructorProfile,
    InstructorServiceArea,
    LocationPublicationAuthorization,
    ProfessionalVerification,
    PublicationDecision,
)
from .services import (
    InvalidWorkflowTransition,
    WorkflowPermissionDenied,
    approve_publication,
    reject_publication,
    revoke_service_location_authorization,
    start_review,
    suspend_publication,
    unpublish_professional,
    verify_professional,
)


def request_id(request):
    return request.headers.get("X-Request-ID")


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "nome_publico",
        "situacao_perfil",
        "situacao_verificacao",
        "situacao_publicacao",
        "map_visible",
    )
    actions = (
        "start_review_action",
        "verify_action",
        "approve_action",
        "reject_action",
        "suspend_action",
        "unpublish_action",
        "revoke_location_action",
    )
    readonly_fields = (
        "profile_status",
        "verification_status",
        "verified_until",
        "publication_status",
        "is_demo",
    )

    @admin.display(description="Nome público", ordering="display_name")
    def nome_publico(self, obj):
        return obj.display_name

    @admin.display(description="Situação do perfil", ordering="profile_status")
    def situacao_perfil(self, obj):
        return obj.get_profile_status_display()

    @admin.display(description="Situação da verificação", ordering="verification_status")
    def situacao_verificacao(self, obj):
        return obj.get_verification_status_display()

    @admin.display(description="Situação da publicação", ordering="publication_status")
    def situacao_publicacao(self, obj):
        return obj.get_publication_status_display()

    @admin.display(description="Visível no mapa", boolean=True)
    def map_visible(self, obj):
        from .selectors import published_instructor_profiles

        return published_instructor_profiles().filter(pk=obj.pk).exists()

    def _run(self, request, queryset, service, reason, area=False):
        ok = 0
        for profile in queryset:
            try:
                kwargs = {
                    "actor": request.user,
                    "reason": reason,
                    "request_id": request_id(request),
                }
                if area:
                    kwargs["service_area"] = profile.service_area
                else:
                    kwargs["profile"] = profile
                service(**kwargs)
                ok += 1
            except (
                WorkflowPermissionDenied,
                InvalidWorkflowTransition,
                InstructorServiceArea.DoesNotExist,
            ) as exc:
                self.message_user(request, f"{profile.display_name}: {exc}", messages.ERROR)
        if ok:
            self.message_user(
                request, f"{ok} transição(ões) concluída(s) e auditada(s).", messages.SUCCESS
            )

    @admin.action(description="Iniciar revisão DEMO")
    def start_review_action(self, r, q):
        self._run(r, q, start_review, "ADMIN_DEMO_REVIEW")

    @admin.action(description="Verificar DEMO")
    def verify_action(self, r, q):
        self._run(r, q, verify_professional, "ADMIN_DEMO_VERIFICATION")

    @admin.action(description="Aprovar publicação DEMO")
    def approve_action(self, r, q):
        self._run(r, q, approve_publication, "ADMIN_DEMO_APPROVAL")

    @admin.action(description="Rejeitar publicação DEMO")
    def reject_action(self, r, q):
        self._run(r, q, reject_publication, "ADMIN_DEMO_REJECTION")

    @admin.action(description="Suspender publicação DEMO")
    def suspend_action(self, r, q):
        self._run(r, q, suspend_publication, "ADMIN_DEMO_SUSPENSION")

    @admin.action(description="Despublicar DEMO")
    def unpublish_action(self, r, q):
        self._run(r, q, unpublish_professional, "ADMIN_DEMO_UNPUBLISH")

    @admin.action(description="Revogar localização de atendimento")
    def revoke_location_action(self, r, q):
        self._run(
            r, q, revoke_service_location_authorization, "ADMIN_DEMO_LOCATION_REVOCATION", area=True
        )


@admin.register(InstructorServiceArea)
class InstructorServiceAreaAdmin(admin.ModelAdmin):
    readonly_fields = ("location_authorized",)


@admin.register(LocationPublicationAuthorization, ProfessionalVerification, PublicationDecision)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Administração InstrutorPro"
admin.site.site_title = "Admin InstrutorPro"
admin.site.index_title = "Painel administrativo"
