from django.db import transaction

from apps.audit.models import AuditEvent

from .models import LessonRequest

TRANSITIONS = {
    LessonRequest.Status.PENDING: {
        LessonRequest.Status.ACCEPTED,
        LessonRequest.Status.REJECTED,
        LessonRequest.Status.CANCELLED,
    }
}


@transaction.atomic
def transition_lesson_request(*, lesson_request, new_status, actor):
    locked = LessonRequest.objects.select_for_update().get(pk=lesson_request.pk)
    if new_status not in TRANSITIONS.get(locked.status, set()):
        raise ValueError("Invalid lesson request transition")
    locked.status = new_status
    locked.save(update_fields=["status", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.lesson_request.status_changed",
        target_type="LessonRequest",
        target_id=locked.id,
        metadata={"status": new_status, "data_mode": locked.data_mode},
    )
    return locked
