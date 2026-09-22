from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.template.response import TemplateResponse
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
        "instructor_name",
        "service_uf",
        "service_city",
        "submitted_date",
        "status_badge",
        "reviewer",
        "queue_action",
    )
    list_filter = (
        "status",
        "profile__service_area__uf",
        "profile__service_area__city",
        "submitted_at",
        "review_started_at",
    )
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
        "service_city",
        "service_uf",
        "workflow_actions",
        "public_message",
    )
    fieldsets = (
        ("Dados do instrutor", {"fields": ("profile", "service_city", "service_uf")}),
        ("Identificação privada", {"fields": ("cpf_masked", "reveal_cpf_link")}),
        (
            "Histórico da solicitação",
            {
                "fields": (
                    "status",
                    "submitted_at",
                    "review_started_at",
                    "reviewer",
                    "decided_at",
                    "decision_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            "Análise profissional",
            {
                "fields": (
                    "verification_method",
                    "verification_source",
                    "checked_at",
                    "internal_notes",
                    "rejection_reason_code",
                )
            },
        ),
        ("Decisão", {"fields": ("public_message", "workflow_actions")}),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("profile__person__account", "profile__service_area", "reviewer")
        )

    @admin.display(description="Instrutor", ordering="profile__display_name")
    def instructor_name(self, obj):
        return obj.profile.display_name

    @admin.display(description="UF", ordering="profile__service_area__uf")
    def service_uf(self, obj):
        try:
            return obj.profile.service_area.uf
        except InstructorServiceArea.DoesNotExist:
            return "—"

    @admin.display(description="Cidade", ordering="profile__service_area__city")
    def service_city(self, obj):
        try:
            return obj.profile.service_area.city
        except InstructorServiceArea.DoesNotExist:
            return "—"

    @admin.display(description="Enviada em", ordering="submitted_at")
    def submitted_date(self, obj):
        return obj.submitted_at

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        css = {
            obj.Status.SUBMITTED: "submitted",
            obj.Status.UNDER_REVIEW: "under_review",
            obj.Status.VERIFIED: "verified",
            obj.Status.REJECTED: "rejected",
        }.get(obj.status, "submitted")
        return format_html(
            '<span class="status-badge status-{}">{}</span>', css, obj.get_status_display()
        )

    @admin.display(description="Ação")
    def queue_action(self, obj):
        url = reverse("admin:discovery_professionalverificationrequest_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Abrir análise</a>', url)

    @admin.display(description="Ações do fluxo")
    def workflow_actions(self, obj):
        if not obj:
            return ""
        base = "admin:discovery_verification_request_transition"
        if obj.status == obj.Status.SUBMITTED:
            url = reverse(base, args=[obj.pk, "start"])
            return format_html(
                '<span class="workflow-buttons"><a class="button" href="{}">'
                "Iniciar análise</a></span>",
                url,
            )
        if obj.status == obj.Status.UNDER_REVIEW:
            approve = reverse(base, args=[obj.pk, "approve"])
            reject = reverse(base, args=[obj.pk, "reject"])
            return format_html(
                '<span class="workflow-buttons"><a class="button default" href="{}">Aprovar</a>'
                '<a class="button" href="{}">Rejeitar</a></span>',
                approve,
                reject,
            )
        return "Fluxo concluído"

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
                "<uuid:object_id>/transition/<str:operation>/",
                self.admin_site.admin_view(self.transition_view),
                name="discovery_verification_request_transition",
            ),
            path(
                "<uuid:object_id>/reveal-cpf/",
                self.admin_site.admin_view(self.reveal_cpf_view),
                name="discovery_verification_request_reveal_cpf",
            ),
        ] + super().get_urls()

    def transition_view(self, request, object_id, operation):
        services = {
            "start": ("Iniciar análise", start_verification_review),
            "approve": ("Aprovar verificação", approve_verification_request),
            "reject": ("Rejeitar verificação", reject_verification_request),
        }
        if operation not in services:
            raise Http404
        item = self.get_object(request, object_id)
        if item is None:
            raise Http404
        if not self.has_change_permission(request, item):
            raise PermissionDenied
        label, service = services[operation]
        back = reverse("admin:discovery_professionalverificationrequest_change", args=[item.pk])
        if request.method == "POST":
            if operation == "reject":
                item.rejection_reason_code = request.POST.get("rejection_reason_code", "").strip()
                item.save(update_fields=["rejection_reason_code", "updated_at"])
            try:
                service(
                    actor=request.user,
                    verification_request=item,
                    request_id=getattr(request, "request_id", None),
                )
                self.message_user(request, f"{label} concluída com auditoria.", messages.SUCCESS)
            except (WorkflowPermissionDenied, InvalidWorkflowTransition) as exc:
                self.message_user(request, str(exc), messages.ERROR)
            return HttpResponseRedirect(back)
        return TemplateResponse(
            request,
            "admin/discovery/confirm_verification_transition.html",
            {
                **self.admin_site.each_context(request),
                "title": label,
                "item": item,
                "operation": operation,
                "back_url": back,
                "opts": self.model._meta,
            },
        )

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
