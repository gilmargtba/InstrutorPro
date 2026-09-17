from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.audit.models import AuditEvent

from .models import Account, ExternalIdentity


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = ("email", "username", "lifecycle_status", "is_staff", "is_active")
    list_filter = ("lifecycle_status", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)
    readonly_fields = (
        "lifecycle_status",
        "lifecycle_changed_at",
        "lifecycle_changed_by",
        "lifecycle_reason",
        "lifecycle_version",
        "last_login",
        "date_joined",
        "is_active",
        "is_staff",
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Cadastro", {"fields": ("email", "first_name", "last_name")}),
        (
            "Situação protegida",
            {
                "fields": (
                    "lifecycle_status",
                    "lifecycle_changed_at",
                    "lifecycle_changed_by",
                    "lifecycle_reason",
                    "lifecycle_version",
                    "is_active",
                )
            },
        ),
        ("Administração", {"fields": ("is_staff",)}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            fields.append("email")
        return fields

    def save_model(self, request, obj, form, change):
        before = None
        if change:
            previous = Account.objects.get(pk=obj.pk)
            before = {
                "email": previous.email,
                "first_name": previous.first_name,
                "last_name": previous.last_name,
                "is_staff": previous.is_staff,
            }
        super().save_model(request, obj, form, change)
        after = {
            "email": obj.email,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "is_staff": obj.is_staff,
        }
        if before and before != after:
            AuditEvent.objects.create(
                actor=request.user,
                action="accounts.account.admin_changed",
                target_type="accounts.Account",
                target_id=obj.id,
                request_id=getattr(request, "request_id", None),
                metadata={"before": before, "after": after},
            )


@admin.register(ExternalIdentity)
class ExternalIdentityAdmin(admin.ModelAdmin):
    list_display = ("provider", "account", "is_active", "created_at")
    search_fields = ("account__email", "subject")
    readonly_fields = ("account", "provider", "subject", "is_active", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
