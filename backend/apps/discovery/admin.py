from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import path, reverse
from django.utils.html import escape, format_html

from apps.audit.models import AuditEvent
from apps.people.identifiers import decrypt_identifier, mask_cpf

from .models import (
    InstructorProfile,
    InstructorServiceArea,
    LocationPublicationAuthorization,
    ProfessionalVerification,
    ProfessionalVerificationRequest,
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
from .verification_services import (
    approve_verification_request,
    reject_verification_request,
    start_verification_review,
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


@admin.register(ProfessionalVerificationRequest)
class ProfessionalVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "cpf_masked",
        "status",
        "submitted_at",
        "reviewer",
        "review_started_at",
    )
    list_filter = ("status", "submitted_at", "review_started_at")
    search_fields = ("profile__display_name", "profile__person__account__email")
    ordering = ("submitted_at", "created_at")
    actions = ("start_review_action", "approve_action", "reject_action")
    readonly_fields = (
        "profile",
        "status",
        "submitted_at",
        "review_started_at",
        "reviewer",
        "decided_at",
        "decision_by",
        "created_at",
        "updated_at",
        "cpf_masked",
        "reveal_cpf_link",
        "public_message",
    )
    fields = (
        "profile",
        "cpf_masked",
        "reveal_cpf_link",
        "status",
        "submitted_at",
        "review_started_at",
        "reviewer",
        "verification_method",
        "verification_source",
        "checked_at",
        "internal_notes",
        "rejection_reason_code",
        "public_message",
        "decided_at",
        "decision_by",
        "created_at",
        "updated_at",
    )

    @admin.display(description="CPF")
    def cpf_masked(self, obj):
        return mask_cpf(obj.profile.person.cpf_last2)

    @admin.display(description="Consulta excepcional do CPF")
    def reveal_cpf_link(self, obj):
        if not obj:
            return ""
        url = reverse("admin:discovery_verification_request_reveal_cpf", args=[obj.pk])
        return format_html('<a href="{}">Consultar com auditoria</a>', url)

    def get_urls(self):
        return [
            path(
                "<uuid:object_id>/reveal-cpf/",
                self.admin_site.admin_view(self.reveal_cpf_view),
                name="discovery_verification_request_reveal_cpf",
            )
        ] + super().get_urls()

    @staticmethod
    def _can_reveal(request):
        return bool(
            request
            and request.user.can_operate
            and request.user.has_perm("discovery.reveal_protected_identifier")
        )

    def reveal_cpf_view(self, request, object_id):
        if not self._can_reveal(request):
            raise PermissionDenied
        item = self.get_object(request, object_id)
        if item is None:
            return HttpResponse("Solicitação não encontrada.", status=404)
        back = reverse("admin:discovery_professionalverificationrequest_change", args=[item.pk])
        if request.method != "POST":
            token = get_token(request)
            return HttpResponse(
                "<h1>Consulta excepcional de CPF</h1>"
                "<p>O acesso será auditado. Use somente para a análise profissional autorizada.</p>"
                '<form method="post"><input type="hidden" name="csrfmiddlewaretoken" '
                f'value="{escape(token)}">'
                '<button type="submit">Consultar CPF</button></form>'
                f'<p><a href="{escape(back)}">Cancelar</a></p>'
            )
        AuditEvent.objects.create(
            actor=request.user,
            action="people.protected_identifier.revealed",
            target_type="discovery.ProfessionalVerificationRequest",
            target_id=item.id,
            request_id=getattr(request, "request_id", None),
            reason_code="ADMIN_PROFESSIONAL_VERIFICATION_REVIEW",
            metadata={"identifier_type": "CPF"},
        )
        cpf = decrypt_identifier(item.profile.person.cpf_ciphertext)
        formatted = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return HttpResponse(
            "<h1>CPF protegido</h1>"
            "<p>Não copie para notas, mensagens ou sistemas não autorizados.</p>"
            f"<strong>{escape(formatted)}</strong>"
            f'<p><a href="{escape(back)}">Voltar à solicitação</a></p>',
            headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.can_operate and request.user.has_perm(
            "discovery.review_professional_verification"
        )

    def save_model(self, request, obj, form, change):
        if obj.status != obj.Status.UNDER_REVIEW or obj.reviewer_id != request.user.id:
            raise PermissionDenied("Somente o revisor responsável pode registrar a análise.")
        allowed = {
            "verification_method",
            "verification_source",
            "checked_at",
            "internal_notes",
            "rejection_reason_code",
        }
        if set(form.changed_data) - allowed:
            raise PermissionDenied("Campo protegido não pode ser alterado diretamente.")
        super().save_model(request, obj, form, change)
        AuditEvent.objects.create(
            actor=request.user,
            action="discovery.professional_verification.review_metadata_updated",
            target_type="discovery.ProfessionalVerificationRequest",
            target_id=obj.id,
            request_id=getattr(request, "request_id", None),
            metadata={"changed_fields": sorted(form.changed_data)},
        )

    def _run(self, request, queryset, service):
        completed = 0
        for item in queryset:
            try:
                service(
                    actor=request.user,
                    verification_request=item,
                    request_id=getattr(request, "request_id", None),
                )
                completed += 1
            except (WorkflowPermissionDenied, InvalidWorkflowTransition) as exc:
                self.message_user(request, f"{item.profile}: {exc}", messages.ERROR)
        if completed:
            self.message_user(
                request, f"{completed} solicitação(ões) processada(s).", messages.SUCCESS
            )

    @admin.action(description="Assumir e iniciar análise")
    def start_review_action(self, request, queryset):
        self._run(request, queryset, start_verification_review)

    @admin.action(description="Aprovar verificação")
    def approve_action(self, request, queryset):
        self._run(request, queryset, approve_verification_request)

    @admin.action(description="Rejeitar verificação")
    def reject_action(self, request, queryset):
        self._run(request, queryset, reject_verification_request)


@admin.register(LocationPublicationAuthorization, ProfessionalVerification, PublicationDecision)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Administração InstrutorProCNH"
admin.site.site_title = "Admin InstrutorProCNH"
admin.site.index_title = "Painel administrativo"
