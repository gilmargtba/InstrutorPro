from datetime import date

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile

from .models import FederativeUnit, RegulatoryReadiness, RegulatoryReadinessHistory
from .policies import INSTRUCTOR_PROVIDER_TYPE, INSTRUCTOR_PUBLICATION_CAPABILITY
from .services import approve_instructor_publication_uf


@admin.register(FederativeUnit)
class FederativeUnitAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "readiness_badge",
        "norm",
        "last_review",
        "source",
        "published_count",
    )
    search_fields = ("code", "name")
    ordering = ("code",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _readiness(self, obj):
        return next(
            (
                item
                for item in obj.regulatory_readiness.all()
                if item.provider_type == INSTRUCTOR_PROVIDER_TYPE
                and item.capability == INSTRUCTOR_PUBLICATION_CAPABILITY
            ),
            None,
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("regulatory_readiness")

    @admin.display(description="Status")
    def readiness_badge(self, obj):
        item = self._readiness(obj)
        if item and item.status == RegulatoryReadiness.Status.APPROVED:
            return "PRONTO"
        if item and item.status == RegulatoryReadiness.Status.SUSPENDED:
            return "BLOQUEADO"
        return "EM REVISÃO"

    @admin.display(description="Norma")
    def norm(self, obj):
        item = self._readiness(obj)
        return item.source_reference if item else "—"

    @admin.display(description="Última revisão")
    def last_review(self, obj):
        item = self._readiness(obj)
        return item.reviewed_at if item and item.reviewed_at else "—"

    @admin.display(description="Fonte")
    def source(self, obj):
        item = self._readiness(obj)
        if not item or not item.source_url:
            return "—"
        return format_html(
            '<a href="{}" rel="noopener noreferrer">Fonte oficial</a>', item.source_url
        )

    @admin.display(description="Instrutores publicados")
    def published_count(self, obj):
        return InstructorProfile.objects.filter(
            is_demo=False,
            verification_status=InstructorProfile.VerificationStatus.VERIFIED,
            publication_status=InstructorProfile.PublicationStatus.APPROVED,
            service_area__uf=obj.code,
        ).count()


class RegulatoryReadinessHistoryInline(admin.TabularInline):
    model = RegulatoryReadinessHistory
    extra = 0
    can_delete = False
    fields = (
        "recorded_at",
        "status",
        "source_reference",
        "valid_from",
        "valid_until",
        "reviewed_by",
        "approved_by",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(RegulatoryReadiness)
class RegulatoryReadinessAdmin(admin.ModelAdmin):
    list_display = (
        "uf",
        "status_badge",
        "source_reference",
        "reviewed_at",
        "source_link",
        "approve_link",
    )
    list_filter = ("status", "provider_type", "capability")
    search_fields = ("federative_unit__code", "source_reference")
    readonly_fields = (
        "federative_unit",
        "provider_type",
        "capability",
        "status",
        "reviewed_by",
        "reviewed_at",
        "approved_by",
        "approved_at",
    )
    fields = (
        "federative_unit",
        "provider_type",
        "capability",
        "status",
        "source_url",
        "source_reference",
        "notes",
        "valid_from",
        "valid_until",
        "reviewed_by",
        "reviewed_at",
        "approved_by",
        "approved_at",
    )
    inlines = (RegulatoryReadinessHistoryInline,)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="UF", ordering="federative_unit__code")
    def uf(self, obj):
        return obj.federative_unit.code

    @admin.display(description="Status")
    def status_badge(self, obj):
        return {"APPROVED": "PRONTO", "SUSPENDED": "BLOQUEADO"}.get(obj.status, "EM REVISÃO")

    @admin.display(description="Fonte")
    def source_link(self, obj):
        if not obj.source_url:
            return "—"
        return format_html(
            '<a href="{}" rel="noopener noreferrer">Fonte oficial</a>', obj.source_url
        )

    @admin.display(description="Confirmar")
    def approve_link(self, obj):
        if obj.status != RegulatoryReadiness.Status.REVIEW_REQUIRED:
            return "—"
        return format_html(
            '<a href="{}">Revisar e aprovar</a>',
            reverse("admin:territories_readiness_approve", args=[obj.pk]),
        )

    def save_model(self, request, obj, form, change):
        if not request.user.has_perm("territories.change_regulatoryreadiness"):
            raise PermissionDenied
        if change and form.changed_data:
            obj.status = RegulatoryReadiness.Status.REVIEW_REQUIRED
            obj.reviewed_by = None
            obj.reviewed_at = None
            obj.approved_by = None
            obj.approved_at = None
            obj.save()
            AuditEvent.objects.create(
                actor=request.user,
                action="territories.regulatory_readiness_evidence_update",
                target_type="RegulatoryReadiness",
                target_id=obj.id,
                reason_code="EVIDENCE_CHANGED",
                metadata={"uf": obj.federative_unit.code, "fields": form.changed_data},
            )

    def get_urls(self):
        return [
            path(
                "<uuid:object_id>/approve/",
                self.admin_site.admin_view(self.approve_view),
                name="territories_readiness_approve",
            )
        ] + super().get_urls()

    def approve_view(self, request, object_id):
        item = self.get_object(request, object_id)
        if item is None:
            raise Http404
        if not request.user.has_perm("territories.change_regulatoryreadiness"):
            raise PermissionDenied
        back = reverse("admin:territories_regulatoryreadiness_change", args=[item.pk])
        if request.method == "POST":
            try:
                effective_from = date.fromisoformat(request.POST.get("valid_from", ""))
                if request.POST.get("confirm_current_source") != "on":
                    raise ValidationError("Confirme a fonte oficial e sua vigência.")
                approve_instructor_publication_uf(
                    actor=request.user,
                    readiness_id=item.pk,
                    valid_from=effective_from,
                    reason=request.POST.get("reason", ""),
                )
                self.message_user(
                    request, "UF aprovada por decisão humana auditada.", messages.SUCCESS
                )
            except (ValueError, ValidationError) as exc:
                self.message_user(request, str(exc), messages.ERROR)
            return HttpResponseRedirect(back)
        return TemplateResponse(
            request,
            "admin/territories/confirm_readiness.html",
            {
                **self.admin_site.each_context(request),
                "title": "Confirmar prontidão regulatória",
                "item": item,
                "back_url": back,
                "opts": self.model._meta,
            },
        )
