from celery import shared_task

from .publication_notifications import deliver_publication_notice, due_publication_notice_ids


@shared_task(name="discovery.deliver_publication_notice")
def deliver_publication_notice_task(decision_id):
    return deliver_publication_notice(decision_id)


@shared_task(name="discovery.retry_publication_notices")
def retry_publication_notices_task():
    decision_ids = due_publication_notice_ids()
    for decision_id in decision_ids:
        deliver_publication_notice_task.delay(str(decision_id))
    return len(decision_ids)
