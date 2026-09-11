from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.people.models import RoleAssignment

from .models import Entitlement, MarketplaceEvent, Plan, PlanEntitlement, Subscription

FREE_ENTITLEMENTS = {
    "PUBLIC_PROFILE": "Perfil público",
    "WHATSAPP_CONTACT": "Contato pelo WhatsApp",
    "BASIC_ANALYTICS": "Estatísticas básicas",
}
PRO_ENTITLEMENTS = {
    "ADVANCED_ANALYTICS": "Estatísticas avançadas",
    "CALENDAR": "Agenda profissional",
    "EXTRA_PHOTOS": "Fotos adicionais",
    "MULTIPLE_VEHICLES": "Múltiplos veículos",
    "FEATURED_PLACEMENT": "Posicionamento em destaque",
    "LEAD_MANAGEMENT": "Gestão de contatos",
    "DEMAND_INSIGHTS": "Inteligência de demanda",
}


@transaction.atomic
def ensure_saas_catalog():
    free, _ = Plan.objects.get_or_create(
        code="FREE",
        defaults={
            "name": "Free",
            "description": "Fundação gratuita do marketplace.",
            "status": Plan.Status.ACTIVE,
            "billing_interval": Plan.BillingInterval.NONE,
            "price_amount": 0,
            "display_order": 10,
            "is_public": True,
        },
    )
    pro, _ = Plan.objects.get_or_create(
        code="PRO",
        defaults={
            "name": "Pro",
            "description": "Estrutura preparada; oferta comercial ainda não aprovada.",
            "status": Plan.Status.DRAFT,
            "billing_interval": Plan.BillingInterval.MONTHLY,
            "price_amount": None,
            "display_order": 20,
            "is_public": False,
        },
    )
    for plan, entries in ((free, FREE_ENTITLEMENTS), (pro, PRO_ENTITLEMENTS)):
        for code, name in entries.items():
            entitlement, _ = Entitlement.objects.get_or_create(code=code, defaults={"name": name})
            PlanEntitlement.objects.get_or_create(plan=plan, entitlement=entitlement)
    return free, pro


@transaction.atomic
def assign_free_plan(account):
    has_role = RoleAssignment.objects.filter(
        person__account=account,
        role=RoleAssignment.Role.INSTRUCTOR,
        revoked_at__isnull=True,
    ).exists()
    if not account.can_operate or not has_role:
        raise PermissionError("Active instructor role is required")
    free, _ = ensure_saas_catalog()
    subscription, _ = Subscription.objects.get_or_create(
        account=account,
        status=Subscription.Status.ACTIVE,
        defaults={"plan": free, "started_at": timezone.now()},
    )
    return subscription


def current_subscription(account):
    return (
        Subscription.objects.filter(
            account=account,
            status__in=[
                Subscription.Status.TRIALING,
                Subscription.Status.ACTIVE,
                Subscription.Status.PAST_DUE,
            ],
        )
        .select_related("plan")
        .first()
    )


def has_entitlement(account, entitlement):
    subscription = current_subscription(account)
    if not subscription or subscription.status not in {
        Subscription.Status.TRIALING,
        Subscription.Status.ACTIVE,
    }:
        return False
    code = getattr(entitlement, "code", entitlement)
    return PlanEntitlement.objects.filter(plan=subscription.plan, entitlement__code=code).exists()


def instructor_analytics(instructor, days):
    days = days if days in {7, 30, 90} else 30
    start = timezone.now() - timedelta(days=days)
    rows = (
        MarketplaceEvent.objects.filter(instructor=instructor, created_at__gte=start)
        .values("event_type")
        .annotate(total=Count("id"))
    )
    totals = {row["event_type"]: row["total"] for row in rows}
    impressions = totals.get(MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION, 0)
    views = totals.get(MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED, 0)
    contacts = totals.get(MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED, 0)
    timeline_rows = (
        MarketplaceEvent.objects.filter(instructor=instructor, created_at__gte=start)
        .annotate(day=TruncDate("created_at"))
        .values("day", "event_type")
        .annotate(total=Count("id"))
        .order_by("day")
    )
    timeline = {}
    for row in timeline_rows:
        day = row["day"].isoformat()
        timeline.setdefault(day, {"date": day, "impressions": 0, "views": 0, "contacts": 0})
        key = {
            MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION: "impressions",
            MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED: "views",
            MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED: "contacts",
        }.get(row["event_type"])
        if key:
            timeline[day][key] = row["total"]
    return {
        "days": days,
        "search_impressions": impressions,
        "profile_views": views,
        "whatsapp_contacts": contacts,
        "conversion_percent": round(contacts * 100 / views, 1) if views else 0,
        "timeline": list(timeline.values()),
    }


@transaction.atomic
def change_subscription_plan(*, actor, subscription, plan, reason, request_id=None):
    if settings.APP_ENV == "PRODUCTION" or not actor.has_perm("marketplace.manage_saas"):
        raise PermissionError("SaaS administration is restricted to DEV/TEST")
    before = {"plan": subscription.plan.code, "status": subscription.status}
    subscription.plan = plan
    subscription.save(update_fields=["plan", "updated_at"])
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.subscription.plan_changed",
        target_type="marketplace.Subscription",
        target_id=subscription.id,
        request_id=request_id,
        reason_code=reason,
        metadata={"before": before, "after": {"plan": plan.code, "status": subscription.status}},
    )
    return subscription
