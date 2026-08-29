from django.contrib import admin

from .models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("occurred_at", "action", "actor", "target_type", "reason_code")
    list_filter = ("action", "target_type", "occurred_at")
    search_fields = ("action", "target_type", "reason_code")
    readonly_fields = (
        "id",
        "actor",
        "action",
        "target_type",
        "target_id",
        "request_id",
        "reason_code",
        "metadata",
        "occurred_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        user = request.user
        return bool(
            user.is_authenticated
            and user.can_operate
            and user.has_perm("audit.view_security_audit")
        )
