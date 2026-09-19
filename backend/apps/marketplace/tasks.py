from celery import shared_task

from .retention import enforce_marketplace_analytics_retention


@shared_task(name="marketplace.enforce_analytics_retention")
def enforce_analytics_retention_task():
    result = enforce_marketplace_analytics_retention()
    return {
        "eligible": result.eligible,
        "processed": result.processed,
        "batches": result.batches,
        "strategy": "DELETE",
    }
