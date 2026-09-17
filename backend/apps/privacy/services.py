from uuid import UUID

from django.db import transaction

from apps.audit.models import AuditEvent

from .models import PrivacyRequest


def _request_id(value):
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


@transaction.atomic
def create_privacy_request(*, requester, request_type, details="", request_id=None):
    row = PrivacyRequest.objects.create(
        requester=requester,
        request_type=request_type,
        details=details,
    )
    AuditEvent.objects.create(
        actor=requester,
        action="privacy.request.created",
        target_type="privacy.PrivacyRequest",
        target_id=row.id,
        request_id=_request_id(request_id),
        metadata={"request_type": request_type, "status": row.status},
    )
    return row
