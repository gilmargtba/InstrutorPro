from django.contrib import admin, messages

from .forms import PlatformOrganizationAdminForm
from .models import PlatformOrganization
from .policies import can_manage_platform_organization, can_validate_platform_organization
from .services import (
    EDITABLE_FIELDS,
    OrganizationPermissionDenied,
    OrganizationValidationError,
    OrganizationVersionConflict,
    save_platform_organization,
    validate_platform_organization,
)


@admin.register(PlatformOrganization)
class PlatformOrganizationAdmin(admin.ModelAdmin):
    form = PlatformOrganizationAdminForm
    list_display = ("legal_name", "formatted_cnpj", "validation_status", "updated_at")
    readonly_fields = (
        "validation_status",
        "validated_at",
        "validated_by",
        "version",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Organização / Controlador",
            {
                "fields": (
                    "cnpj",
                    "legal_name",
                    "trade_name",
                    "business_address",
                    "legal_representative",
                    "operational_contact",
                    "privacy_contact",
                    "phone",
                    "expected_version",
                )
            },
        ),
        (
            "Encarregado/DPO — preencher somente quando formalmente definido",
            {"fields": ("dpo_name", "dpo_contact", "dpo_appointment_reference")},
        ),
        (
            "Validação",
            {
                "fields": (
                    "validation_status",
                    "validated_at",
                    "validated_by",
                    "version",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
    actions = ("validate_selected",)

    @admin.display(description="CNPJ")
    def formatted_cnpj(self, obj):
        if len(obj.cnpj) != 14:
            return "—"
        return f"{obj.cnpj[:2]}.{obj.cnpj[2:5]}.{obj.cnpj[5:8]}/{obj.cnpj[8:12]}-{obj.cnpj[12:]}"

    def has_module_permission(self, request):
        return can_manage_platform_organization(
            actor=request.user
        ) or can_validate_platform_organization(actor=request.user)

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return (
            can_manage_platform_organization(actor=request.user)
            and not PlatformOrganization.objects.exists()
        )

    def has_change_permission(self, request, obj=None):
        return can_manage_platform_organization(actor=request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_validate_permission(self, request, obj=None):
        return can_validate_platform_organization(actor=request.user)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not can_validate_platform_organization(actor=request.user):
            actions.pop("validate_selected", None)
        return actions

    def save_model(self, request, obj, form, change):
        data = {field: form.cleaned_data.get(field) for field in EDITABLE_FIELDS}
        saved = save_platform_organization(
            actor=request.user,
            organization=obj if change else None,
            data=data,
            expected_version=form.cleaned_data.get("expected_version") or 0,
            reason="ADMIN_CONFIGURATION_SAVE",
            request_id=getattr(request, "request_id", None),
        )
        for field in saved._meta.concrete_fields:
            setattr(obj, field.attname, getattr(saved, field.attname))
        obj._state.adding = False
        obj._state.db = saved._state.db

    @admin.action(
        description="Validar organização/controlador selecionado", permissions=("validate",)
    )
    def validate_selected(self, request, queryset):
        success = 0
        for organization in queryset:
            try:
                validate_platform_organization(
                    actor=request.user,
                    organization=organization,
                    expected_version=organization.version,
                    reason="ADMIN_MANUAL_VALIDATION",
                    request_id=getattr(request, "request_id", None),
                )
                success += 1
            except (
                OrganizationPermissionDenied,
                OrganizationValidationError,
                OrganizationVersionConflict,
            ) as exc:
                self.message_user(request, str(exc), messages.ERROR)
        if success:
            self.message_user(
                request,
                f"{success} organização(ões) validada(s) e auditada(s).",
                messages.SUCCESS,
            )
