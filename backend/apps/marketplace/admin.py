from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .documents import (
    DocumentPermissionDenied,
    DocumentValidationError,
    review_document,
    review_profile_photo,
)
from .models import (
    DocumentRequirement,
    InstructorDocument,
    InstructorPrerequisiteAcceptance,
    InstructorVehicle,
    LessonRequest,
    PlatformLesson,
    PracticalTrainingRequirement,
    ProfilePhoto,
    StudentDemand,
    StudentProfile,
)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "city", "uf", "intended_category", "data_mode", "created_at")
    list_filter = ("data_mode", "uf")


@admin.register(StudentDemand)
class StudentDemandAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "uf", "category", "status", "data_mode", "created_at")
    list_filter = ("status", "data_mode", "uf")
    readonly_fields = ("student", "private_centroid", "data_mode", "created_at", "updated_at")


@admin.register(LessonRequest)
class LessonRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "instructor", "category", "status", "data_mode", "created_at")
    list_filter = ("status", "data_mode")
    readonly_fields = ("student", "instructor", "data_mode", "created_at", "updated_at")


@admin.register(DocumentRequirement)
class DocumentRequirementAdmin(admin.ModelAdmin):
    list_display = ("label", "uf", "category", "rule_version", "required", "active_from")
    list_filter = ("uf", "category", "required", "document_type")


@admin.register(InstructorDocument)
class InstructorDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "original_name",
        "instructor",
        "requirement",
        "status",
        "scan_status",
        "valid_until",
        "version",
    )
    list_filter = ("status", "scan_status", "data_mode", "requirement__uf")
    readonly_fields = (
        "secure_download",
        "original_name",
        "mime_type",
        "size_bytes",
        "sha256",
        "uploaded_at",
        "version",
        "supersedes",
        "data_mode",
        "reviewed_by",
        "reviewed_at",
    )
    actions = ("approve_selected", "reject_selected")

    @admin.display(description="Arquivo privado")
    def secure_download(self, obj):
        if not obj or not obj.pk:
            return "—"
        url = reverse("instructor-document-download", kwargs={"pk": obj.pk})
        return format_html('<a href="{}">Baixar com autorização e auditoria</a>', url)

    def _review(self, request, queryset, decision, reason):
        completed = 0
        for document in queryset:
            try:
                review_document(
                    actor=request.user,
                    document=document,
                    decision=decision,
                    reason=reason,
                    source="ADMIN_MANUAL_REVIEW",
                )
                completed += 1
            except (DocumentPermissionDenied, DocumentValidationError) as exc:
                self.message_user(request, str(exc), level="error")
        self.message_user(request, f"{completed} documento(s) processado(s).")

    @admin.action(description="Aprovar documentos selecionados")
    def approve_selected(self, request, queryset):
        self._review(request, queryset, InstructorDocument.Status.APPROVED, "ADMIN_APPROVED")

    @admin.action(description="Rejeitar documentos selecionados")
    def reject_selected(self, request, queryset):
        self._review(request, queryset, InstructorDocument.Status.REJECTED, "ADMIN_REJECTED")


@admin.register(InstructorVehicle)
class InstructorVehicleAdmin(admin.ModelAdmin):
    list_display = (
        "instructor",
        "category",
        "make",
        "model",
        "ownership_type",
        "verification_status",
        "data_mode",
    )
    list_filter = ("verification_status", "data_mode", "category")


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ("instructor", "status", "publication_notice_version", "uploaded_at")
    list_filter = ("status", "data_mode")
    readonly_fields = (
        "secure_preview",
        "original_name",
        "mime_type",
        "size_bytes",
        "sha256",
        "publication_authorized_at",
        "publication_notice_version",
        "data_mode",
        "uploaded_at",
        "reviewed_by",
        "reviewed_at",
        "status",
    )
    actions = ("approve_photos", "reject_photos", "request_replacement")

    @admin.display(description="Foto privada")
    def secure_preview(self, obj):
        if not obj or not obj.pk:
            return "—"
        url = reverse("profile-photo-private-download", kwargs={"pk": obj.pk})
        return format_html(
            '<a href="{}" target="_blank">Visualizar com autorização e auditoria</a>',
            url,
        )

    def _review(self, request, queryset, decision, reason):
        for photo in queryset:
            try:
                review_profile_photo(
                    actor=request.user, photo=photo, decision=decision, reason=reason
                )
            except (DocumentPermissionDenied, DocumentValidationError) as exc:
                self.message_user(request, str(exc), level="error")

    @admin.action(description="Aprovar fotos selecionadas")
    def approve_photos(self, request, queryset):
        self._review(request, queryset, ProfilePhoto.Status.APPROVED, "ADMIN_PHOTO_APPROVED")

    @admin.action(description="Rejeitar fotos selecionadas")
    def reject_photos(self, request, queryset):
        self._review(request, queryset, ProfilePhoto.Status.REJECTED, "ADMIN_PHOTO_REJECTED")

    @admin.action(description="Solicitar substituição")
    def request_replacement(self, request, queryset):
        self._review(
            request,
            queryset,
            ProfilePhoto.Status.REPLACEMENT_REQUESTED,
            "ADMIN_PHOTO_REPLACEMENT_REQUESTED",
        )


admin.site.register(InstructorPrerequisiteAcceptance)
admin.site.register(PracticalTrainingRequirement)
admin.site.register(PlatformLesson)
