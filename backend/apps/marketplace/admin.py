from django.contrib import admin

from .models import (
    InstructorPrerequisiteAcceptance,
    InstructorVehicle,
    LessonRequest,
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


admin.site.register(InstructorVehicle)
admin.site.register(InstructorPrerequisiteAcceptance)
