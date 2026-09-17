from django.contrib import admin

from apps.audit.models import AuditEvent

from .models import Person, RoleAssignment


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "phone", "birth_date", "created_at")
    search_fields = ("account__email", "account__username", "phone")
    readonly_fields = ("account", "created_at")

    def save_model(self, request, obj, form, change):
        before = None
        if change:
            previous = Person.objects.get(pk=obj.pk)
            before = {"phone": previous.phone, "birth_date": previous.birth_date}
        super().save_model(request, obj, form, change)
        after = {"phone": obj.phone, "birth_date": obj.birth_date}
        if before and before != after:
            AuditEvent.objects.create(
                actor=request.user,
                action="people.person.admin_changed",
                target_type="people.Person",
                target_id=obj.id,
                request_id=getattr(request, "request_id", None),
                metadata={"changed_fields": list(form.changed_data)},
            )


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("person", "role", "status", "granted_at", "revoked_at")
    list_filter = ("role",)
    search_fields = ("person__account__email", "person__account__username")
    readonly_fields = tuple(field.name for field in RoleAssignment._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("people.view_roleassignment")

    def has_delete_permission(self, request, obj=None):
        return False
