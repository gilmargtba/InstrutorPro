from celery import shared_task

from .instructor_precheck import InstructorValidationService, due_precheck_ids
from .publication_notifications import deliver_publication_notice, due_publication_notice_ids
from .verification_notifications import (
    deliver_verification_approval_notice,
    due_verification_approval_notice_ids,
)


@shared_task(name="discovery.run_instructor_precheck")
def run_instructor_precheck_task(request_id):
    return InstructorValidationService.run(request_id)


@shared_task(name="discovery.retry_instructor_prechecks")
def retry_instructor_prechecks_task():
    request_ids = due_precheck_ids()
    for request_id in request_ids:
        run_instructor_precheck_task.delay(str(request_id))
    return len(request_ids)


@shared_task(name="discovery.deliver_publication_notice")
def deliver_publication_notice_task(decision_id):
    return deliver_publication_notice(decision_id)


@shared_task(name="discovery.retry_publication_notices")
def retry_publication_notices_task():
    decision_ids = due_publication_notice_ids()
    for decision_id in decision_ids:
        deliver_publication_notice_task.delay(str(decision_id))
    return len(decision_ids)


@shared_task(name="discovery.deliver_verification_approval_notice")
def deliver_verification_approval_notice_task(request_id):
    return deliver_verification_approval_notice(request_id)


@shared_task(name="discovery.retry_verification_approval_notices")
def retry_verification_approval_notices_task():
    request_ids = due_verification_approval_notice_ids()
    for request_id in request_ids:
        deliver_verification_approval_notice_task.delay(str(request_id))
    return len(request_ids)
