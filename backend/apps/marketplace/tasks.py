from celery import shared_task

from .models import DocumentRetentionPolicy
from .professional_retention import enforce_professional_document_retention
from .retention import enforce_marketplace_analytics_retention
from .availability_interest import purge_expired_availability_interests


@shared_task(name="marketplace.purge_expired_availability_interests")
def purge_expired_availability_interests_task():
    return {"deleted": purge_expired_availability_interests()}


@shared_task(name="marketplace.enforce_analytics_retention")
def enforce_analytics_retention_task():
    result = enforce_marketplace_analytics_retention()
    return {
        "eligible": result.eligible,
        "processed": result.processed,
        "batches": result.batches,
        "strategy": "DELETE",
    }


@shared_task(name="marketplace.enforce_professional_document_retention")
def enforce_professional_document_retention_task():
    result = enforce_professional_document_retention(
        scope=DocumentRetentionPolicy.Scope.PRODUCTION,
        dry_run=False,
    )
    return {
        "policy_available": result.policy_available,
        "eligible": result.eligible,
        "processed": result.processed,
    }
