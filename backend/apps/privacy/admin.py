from django.contrib import admin
from django.utils import timezone

from apps.audit.models import AuditEvent

from .models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice, PrivacyRequest


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "audience", "version", "effective_at", "is_active")
    list_filter = ("audience", "is_active")
    readonly_fields = ("content_sha256", "created_at")


@admin.register(LegalAcceptanceRecord)
class LegalAcceptanceRecordAdmin(admin.ModelAdmin):
    list_display = ("account", "terms_document", "privacy_notice", "accepted_at")
    readonly_fields = (
        "account",
        "terms_document",
        "privacy_notice",
        "accepted_at",
        "request_id",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PrivacyNotice)
class PrivacyNoticeAdmin(admin.ModelAdmin):
    list_display = ("version", "title", "published_at", "is_current")
    list_filter = ("is_current",)


@admin.register(PrivacyRequest)
class PrivacyRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "requester", "request_type", "status", "requested_at", "assigned_to")
    list_filter = ("request_type", "status")
    search_fields = ("requester__email", "requester__username")
    readonly_fields = ("requester", "request_type", "details", "requested_at", "completed_at")

    def has_module_permission(self, request):
        return request.user.has_perm("privacy.manage_privacy_requests")

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("privacy.manage_privacy_requests")

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("privacy.manage_privacy_requests")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        before = None
        if change:
            previous = PrivacyRequest.objects.get(pk=obj.pk)
            before = {"status": previous.status, "assigned_to": str(previous.assigned_to_id or "")}
        if obj.status in {PrivacyRequest.Status.COMPLETED, PrivacyRequest.Status.REJECTED}:
            obj.completed_at = obj.completed_at or timezone.now()
        else:
            obj.completed_at = None
        super().save_model(request, obj, form, change)
        after = {"status": obj.status, "assigned_to": str(obj.assigned_to_id or "")}
        if before and before != after:
            AuditEvent.objects.create(
                actor=request.user,
                action="privacy.request.admin_changed",
                target_type="privacy.PrivacyRequest",
                target_id=obj.id,
                request_id=getattr(request, "request_id", None),
                metadata={"before": before, "after": after},
            )
