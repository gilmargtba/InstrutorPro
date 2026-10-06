from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import escape, format_html

from apps.audit.models import AuditEvent
from apps.marketplace.models import InstructorDocument
from apps.people.identifiers import decrypt_identifier, mask_cpf

from .admin_approval import approval_panel, execute_approval_action
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
    can_manage_publication,
    reject_publication,
    revoke_service_location_authorization,
    start_review,
    suspend_publication,
    unpublish_professional,
    verify_professional,
)
from .verification_services import (
    record_review_and_approve,
    reject_verification_request,
    review_checklist,
    start_verification_review,
)


def request_id(request):
    return request.headers.get("X-Request-ID")


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    change_form_template = "admin/discovery/instructor_change_form.html"
    list_display = (
        "nome_publico",
        "situacao_perfil",
        "situacao_verificacao",
        "situacao_publicacao",
        "publication_action",
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
    list_filter = ("profile_status", "verification_status", "publication_status", "is_demo")
    readonly_fields = (
        "profile_status",
        "verification_status",
        "verified_until",
        "publication_status",
        "is_demo",
        "publication_actions",
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

    @admin.display(description="Publicação")
    def publication_action(self, obj):
        if obj.is_demo:
            return "—"
        url = reverse("admin:discovery_instructorprofile_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Abrir aprovação e publicação</a>', url)

    @admin.display(description="Ações de publicação")
    def publication_actions(self, obj):
        if not obj or obj.is_demo:
            return "Use o fluxo DEMO somente para perfis sintéticos."
        base = "admin:discovery_instructor_publication_transition"
        if obj.profile_status == "UNDER_REVIEW" and obj.verification_status == "VERIFIED":
            return "Use o painel Aprovação e publicação acima."
        if obj.publication_status == "APPROVED":
            suspend = reverse(base, args=[obj.pk, "suspend"])
            unpublish = reverse(base, args=[obj.pk, "unpublish"])
            return format_html(
                '<span class="workflow-buttons"><a class="button" href="{}">Suspender</a>'
                '<a class="button" href="{}">Despublicar</a></span>',
                suspend,
                unpublish,
            )
        if obj.publication_status == "SUSPENDED":
            url = reverse(base, args=[obj.pk, "unpublish"])
            return format_html('<a class="button" href="{}">Despublicar</a>', url)
        return "Aguardando verificação ou gate territorial de publicação."

    def get_urls(self):
        return [
            path(
                "<uuid:object_id>/approval-action/",
                self.admin_site.admin_view(self.approval_action_view),
                name="discovery_instructor_approval_action",
            ),
            path(
                "<uuid:object_id>/publication/<str:operation>/",
                self.admin_site.admin_view(self.publication_transition_view),
                name="discovery_instructor_publication_transition",
            ),
        ] + super().get_urls()

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        if object_id:
            profile = self.get_object(request, object_id)
            if profile and not profile.is_demo and self.has_view_permission(request, profile):
                panel = approval_panel(profile, request.user)
                panel["action_url"] = reverse(
                    "admin:discovery_instructor_approval_action", args=[profile.pk]
                )
                panel["profile_url"] = (
                    f"{settings.FRONTEND_PUBLIC_URL}/aluno/instrutores/{profile.pk}"
                )
                if panel["active_categories"] and panel["area"]:
                    area = panel["area"]
                    query = urlencode(
                        {
                            "local": f"{area.city}, {area.uf}",
                            "uf": area.uf,
                            "categoria": panel["active_categories"][0],
                            "raio": max(area.radius_km, 10),
                        }
                    )
                    panel["search_url"] = (
                        f"{settings.FRONTEND_PUBLIC_URL}/aluno/instrutores/mapa?{query}"
                    )
                extra_context = {**(extra_context or {}), "approval_panel": panel}
        return super().changeform_view(request, object_id, form_url, extra_context)

    def approval_action_view(self, request, object_id):
        if request.method != "POST":
            raise Http404
        profile = self.get_object(request, object_id)
        if profile is None or profile.is_demo:
            raise Http404
        if not self.has_change_permission(request, profile):
            raise PermissionDenied
        try:
            record = execute_approval_action(
                actor=request.user,
                profile=profile,
                data=request.POST,
                request_id=getattr(request, "request_id", None),
            )
            self.message_user(request, "Decisão registrada com auditoria.", messages.SUCCESS)
            if record and record.notice_status == PublicationDecision.NoticeStatus.PENDING:
                self.message_user(
                    request,
                    "Perfil publicado; aviso por e-mail pendente de entrega.",
                    messages.INFO,
                )
        except (InvalidWorkflowTransition, WorkflowPermissionDenied, ValidationError) as exc:
            self.message_user(request, str(exc), messages.ERROR)
        return HttpResponseRedirect(
            reverse("admin:discovery_instructorprofile_change", args=[profile.pk])
        )

    def publication_transition_view(self, request, object_id, operation):
        services = {
            "publish": ("Publicar perfil", approve_publication),
            "suspend": ("Suspender perfil", suspend_publication),
            "unpublish": ("Despublicar perfil", unpublish_professional),
        }
        if operation not in services:
            raise Http404
        profile = self.get_object(request, object_id)
        if profile is None or profile.is_demo:
            raise Http404
        if not can_manage_publication(request.user):
            raise PermissionDenied
        label, service = services[operation]
        back = reverse("admin:discovery_instructorprofile_change", args=[profile.pk])
        if request.method == "POST":
            reason = request.POST.get("reason", "").strip()
            if not reason:
                self.message_user(request, "Informe o motivo da decisão.", messages.ERROR)
            else:
                try:
                    record = service(
                        actor=request.user,
                        profile=profile,
                        reason=reason,
                        request_id=getattr(request, "request_id", None),
                    )
                    self.message_user(request, f"{label}: decisão auditada.", messages.SUCCESS)
                    if record.notice_status == PublicationDecision.NoticeStatus.PENDING:
                        self.message_user(
                            request,
                            "Aviso por e-mail pendente; acompanhe em Decisões de publicação.",
                            messages.INFO,
                        )
                except (WorkflowPermissionDenied, InvalidWorkflowTransition) as exc:
                    self.message_user(request, str(exc), messages.ERROR)
            return HttpResponseRedirect(back)
        return TemplateResponse(
            request,
            "admin/discovery/confirm_publication_transition.html",
            {
                **self.admin_site.each_context(request),
                "title": label,
                "profile": profile,
                "operation": operation,
                "back_url": back,
                "opts": self.model._meta,
            },
        )

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
        self._run(r, q.filter(is_demo=True), start_review, "ADMIN_DEMO_REVIEW")

    @admin.action(description="Verificar DEMO")
    def verify_action(self, r, q):
        self._run(r, q.filter(is_demo=True), verify_professional, "ADMIN_DEMO_VERIFICATION")

    @admin.action(description="Aprovar publicação DEMO")
    def approve_action(self, r, q):
        self._run(r, q.filter(is_demo=True), approve_publication, "ADMIN_DEMO_APPROVAL")

    @admin.action(description="Rejeitar publicação DEMO")
    def reject_action(self, r, q):
        self._run(r, q.filter(is_demo=True), reject_publication, "ADMIN_DEMO_REJECTION")

    @admin.action(description="Suspender publicação DEMO")
    def suspend_action(self, r, q):
        self._run(r, q.filter(is_demo=True), suspend_publication, "ADMIN_DEMO_SUSPENSION")

    @admin.action(description="Despublicar DEMO")
    def unpublish_action(self, r, q):
        self._run(r, q.filter(is_demo=True), unpublish_professional, "ADMIN_DEMO_UNPUBLISH")

    @admin.action(description="Revogar localização de atendimento")
    def revoke_location_action(self, r, q):
        self._run(
            r, q, revoke_service_location_authorization, "ADMIN_DEMO_LOCATION_REVOCATION", area=True
        )


@admin.register(InstructorServiceArea)
class InstructorServiceAreaAdmin(admin.ModelAdmin):
    readonly_fields = ("location_authorized",)


class SubmittedDocumentInline(admin.TabularInline):
    model = InstructorDocument
    fk_name = "verification_request"
    verbose_name_plural = "Documentos enviados"
    fields = (
        "document_label",
        "original_name",
        "uploaded_at",
        "security_status",
        "authorized_view",
    )
    readonly_fields = fields
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.can_operate or not request.user.has_perm(
            "marketplace.review_instructor_document"
        ):
            return queryset.none()
        return queryset.filter(
            verification_request__reviewer=request.user,
            verification_request__status=ProfessionalVerificationRequest.Status.UNDER_REVIEW,
            scan_status=InstructorDocument.ScanStatus.CLEAN,
        ).select_related("requirement")

    @admin.display(description="Segurança")
    def security_status(self, obj):
        return "Pronto"

    @admin.display(description="Arquivo privado")
    def authorized_view(self, obj):
        return format_html(
            '<a href="{}">Visualizar com autorização e auditoria</a>',
            reverse("instructor-document-download", kwargs={"pk": obj.pk}),
        )

    def has_view_permission(self, request, obj=None):
        return request.user.can_operate and request.user.has_perm(
            "marketplace.review_instructor_document"
        )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class VerificationApprovalForm(forms.Form):
    reviewed_document_ids = forms.MultipleChoiceField(
        label="Documentos conferidos e aprovados nesta decisão",
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text=(
            "Abra cada arquivo privado e marque apenas o que você conferiu. "
            "Documentos já aprovados não precisam ser marcados novamente."
        ),
    )
    verification_method = forms.CharField(
        label="Método da consulta",
        max_length=40,
        help_text=(
            "Descreva como você conferiu a evidência; não declare autorização oficial sem prova."
        ),
    )
    verification_source = forms.CharField(
        label="Fonte consultada",
        max_length=80,
        help_text="Informe órgão e referência/URL da fonte efetivamente consultada.",
    )
    internal_notes = forms.CharField(
        label="Notas internas (sem CPF completo)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    consultation_confirmed = forms.BooleanField(
        label="Confirmo que consultei esta fonte agora e revisei os documentos aplicáveis.",
        required=True,
    )

    def __init__(self, *args, pending_documents=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reviewed_document_ids"].choices = [
            (str(document.pk), f"{document.document_label} — {document.original_name}")
            for document in pending_documents
        ]
        if not pending_documents:
            del self.fields["reviewed_document_ids"]


class VerificationRejectionForm(forms.Form):
    rejection_reason_code = forms.ChoiceField(
        label="Motivo estruturado da rejeição",
        choices=[
            ("", "Selecione um motivo"),
            ("REQUIREMENT_MISSING", "Requisito obrigatório ausente"),
            ("DOCUMENT_UNREADABLE", "Documento ilegível"),
            ("DOCUMENT_MISMATCH", "Documento divergente"),
            ("DOCUMENT_EXPIRED", "Documento vencido"),
            ("OFFICIAL_AUTHORIZATION_NOT_CONFIRMED", "Autorização não confirmada"),
            ("OFFICIAL_AUTHORIZATION_INACTIVE", "Autorização inativa"),
            ("VEHICLE_REQUIREMENT_NOT_MET", "Requisito de veículo não atendido"),
            ("INFORMATION_INCONSISTENT", "Informações inconsistentes"),
            ("REVIEW_CONFLICT", "Conflito na revisão"),
            ("POLICY_VERSION_CONFLICT", "Versão da regra conflitante"),
        ],
    )


@admin.register(ProfessionalVerificationRequest)
class ProfessionalVerificationRequestAdmin(admin.ModelAdmin):
    review_metadata_fields = (
        "verification_method",
        "verification_source",
        "checked_at",
        "internal_notes",
        "rejection_reason_code",
    )
    inlines = (SubmittedDocumentInline,)
    list_display = (
        "instructor_name",
        "service_uf",
        "service_city",
        "submitted_date",
        "status_badge",
        "reviewer",
        "triage_status",
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
    actions = ("start_review_action",)
    readonly_fields = (
        "profile",
        "previous_verified_request",
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
        "review_checklist_display",
    )
    fieldsets = (
        (
            "Dados do instrutor",
            {"fields": ("profile", "service_city", "service_uf", "previous_verified_request")},
        ),
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
        (
            "Decisão",
            {"fields": ("review_checklist_display", "public_message", "workflow_actions")},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("profile__person__account", "profile__service_area", "reviewer")
            .prefetch_related("documents")
        )

    def _can_edit_review_metadata(self, request, obj):
        return bool(
            obj
            and self.has_change_permission(request, obj)
            and obj.status == obj.Status.UNDER_REVIEW
            and obj.reviewer_id == request.user.id
        )

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and not self._can_edit_review_metadata(request, obj):
            return (*fields, *self.review_metadata_fields)
        return fields

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        obj = self.get_object(request, object_id) if object_id else None
        if (
            obj
            and self.has_change_permission(request, obj)
            and not self._can_edit_review_metadata(request, obj)
        ):
            if request.method == "POST":
                if obj.reviewer_id and obj.reviewer_id != request.user.id:
                    raise PermissionDenied(
                        "Somente o revisor responsável pode registrar a análise."
                    )
                self.message_user(
                    request,
                    "Esta solicitação não pode ser editada nesta etapa; "
                    "nenhuma alteração foi gravada.",
                    messages.WARNING,
                )
                return HttpResponseRedirect(
                    reverse("admin:discovery_professionalverificationrequest_change", args=[obj.pk])
                )
            extra_context = {
                **(extra_context or {}),
                "show_save": False,
                "show_save_and_continue": False,
                "show_save_and_add_another": False,
            }
        return super().changeform_view(request, object_id, form_url, extra_context)

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

    @admin.display(description="Triagem")
    def triage_status(self, obj):
        if obj.status == obj.Status.SUBMITTED:
            return "Aguardando revisor"
        if obj.status != obj.Status.UNDER_REVIEW:
            return "Concluída" if obj.status != obj.Status.DRAFT else "Rascunho"
        missing = review_checklist(obj)
        return f"{len(missing)} pendência(s)" if missing else "Conferência humana necessária"

    @admin.display(description="Checklist antes da decisão")
    def review_checklist_display(self, obj):
        if not obj:
            return ""
        if obj.status == obj.Status.SUBMITTED:
            return "Assuma a solicitação antes de analisar as evidências."
        if obj.status != obj.Status.UNDER_REVIEW:
            return "Solicitação fora da etapa de análise."
        missing = review_checklist(obj)
        return (
            "; ".join(missing) if missing else "Campos completos; decisão humana ainda obrigatória."
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
            "approve": ("Aprovar verificação", None),
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
        review_documents = (
            list(item.documents.all())
            if operation == "approve"
            and item.reviewer_id == request.user.id
            and request.user.has_perm("marketplace.review_instructor_document")
            else []
        )
        pending_documents = [
            document
            for document in review_documents
            if document.scan_status == InstructorDocument.ScanStatus.CLEAN
            and document.status
            in {
                InstructorDocument.Status.PENDING,
                InstructorDocument.Status.UNDER_REVIEW,
            }
        ]
        form_class = {
            "approve": VerificationApprovalForm,
            "reject": VerificationRejectionForm,
        }.get(operation)
        initial = (
            {
                "verification_method": item.verification_method,
                "verification_source": item.verification_source,
                "internal_notes": item.internal_notes,
            }
            if operation == "approve"
            else {"rejection_reason_code": item.rejection_reason_code}
        )
        form = (
            form_class(
                request.POST if request.method == "POST" else None,
                initial=initial,
                **({"pending_documents": pending_documents} if operation == "approve" else {}),
            )
            if form_class
            else None
        )
        if request.method == "POST":
            if form is None or form.is_valid():
                try:
                    if operation == "approve":
                        record_review_and_approve(
                            actor=request.user,
                            verification_request=item,
                            method=form.cleaned_data["verification_method"],
                            source=form.cleaned_data["verification_source"],
                            notes=form.cleaned_data["internal_notes"],
                            consultation_confirmed=form.cleaned_data["consultation_confirmed"],
                            reviewed_document_ids=form.cleaned_data.get(
                                "reviewed_document_ids", ()
                            ),
                            request_id=getattr(request, "request_id", None),
                        )
                    elif operation == "reject":
                        reject_verification_request(
                            actor=request.user,
                            verification_request=item,
                            reason_code=form.cleaned_data["rejection_reason_code"],
                            request_id=getattr(request, "request_id", None),
                        )
                    else:
                        service(
                            actor=request.user,
                            verification_request=item,
                            request_id=getattr(request, "request_id", None),
                        )
                    self.message_user(
                        request, f"{label} concluída com auditoria.", messages.SUCCESS
                    )
                    return HttpResponseRedirect(back)
                except (WorkflowPermissionDenied, InvalidWorkflowTransition) as exc:
                    if form is None:
                        self.message_user(request, str(exc), messages.ERROR)
                        return HttpResponseRedirect(back)
                    form.add_error(None, str(exc))
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
                "form": form,
                "review_checklist": review_checklist(item),
                "review_documents": review_documents,
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


@admin.register(LocationPublicationAuthorization, ProfessionalVerification)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PublicationDecision)
class PublicationDecisionAdmin(WorkflowHistoryAdmin):
    list_display = ("profile", "decision", "notice_status", "notice_sent_at", "created_at")
    list_filter = ("decision", "notice_status")
    readonly_fields = (
        "profile",
        "decision",
        "actor",
        "reason",
        "verification",
        "before",
        "after",
        "notice_status",
        "notice_recipient",
        "notice_attempts",
        "notice_attempted_at",
        "notice_sent_at",
        "created_at",
    )

    def has_view_permission(self, request, obj=None):
        return can_manage_publication(request.user) or super().has_view_permission(request, obj)


admin.site.site_header = "Administração InstrutorProCNH"
admin.site.site_title = "Admin InstrutorProCNH"
admin.site.index_title = "Painel administrativo"
