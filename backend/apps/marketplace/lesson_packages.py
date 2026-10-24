"""Commercial lesson bundles, isolated from official lesson and payment state."""

from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile

from .models import DataMode, InstructorLessonPackage, Plan, Subscription
from .saas import current_subscription

PACKAGE_LIMITS = {"FREE": 1, "PRO": 6, "PREMIUM": None}


class PackageLimitReached(ValidationError):
    def __init__(self, plan_code, limit):
        super().__init__(
            f"O plano {plan_code} permite até {limit} pacote(s) ativo(s). "
            "Desative um pacote ou conheça os planos superiores.",
            code="package_limit_reached",
        )


def effective_package_plan(account):
    """Paid tiers count only while their existing subscription is valid and active."""
    subscription = current_subscription(account)
    if not subscription:
        return "FREE"
    plan = subscription.plan
    if plan.status != Plan.Status.ACTIVE or plan.code not in PACKAGE_LIMITS:
        return "FREE"
    if plan.code == "FREE":
        return "FREE"
    now = timezone.now()
    if subscription.status == Subscription.Status.TRIALING:
        return (
            plan.code if subscription.trial_ends_at and subscription.trial_ends_at > now else "FREE"
        )
    if subscription.status == Subscription.Status.ACTIVE:
        return (
            plan.code
            if subscription.current_period_end and subscription.current_period_end > now
            else "FREE"
        )
    return "FREE"


def package_visibility(instructor):
    """Oldest active packages retain visibility after downgrade; records stay untouched."""
    account = instructor.person.account
    plan_code = effective_package_plan(account)
    limit = PACKAGE_LIMITS[plan_code]
    mode = DataMode.SYNTHETIC if instructor.is_demo else DataMode.REAL
    active = list(
        InstructorLessonPackage.objects.filter(
            instructor=instructor, is_active=True, data_mode=mode
        ).order_by("created_at", "id")
    )
    within_plan_limit = active if limit is None else active[:limit]
    visible = [
        package for package in within_plan_limit if package.category in instructor.categories
    ]
    return plan_code, limit, active, visible


def package_data(package):
    return {
        "id": str(package.id),
        "name": package.name,
        "category": package.category,
        "lesson_count": package.lesson_count,
        "price_amount": package.price_amount,
        "price_per_lesson": (package.price_amount / Decimal(package.lesson_count)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ),
        "vehicle_included": package.vehicle_included,
        "description": package.description,
        "is_active": package.is_active,
    }


@transaction.atomic
def save_lesson_package(*, actor, profile, data, package_id=None, request_id=None):
    locked = (
        InstructorProfile.objects.select_for_update()
        .select_related("person__account")
        .get(pk=profile.pk)
    )
    if not actor.can_operate or locked.person.account_id != actor.pk:
        raise PermissionDenied("Somente o instrutor titular pode editar seus pacotes.")
    mode = DataMode.SYNTHETIC if locked.is_demo else DataMode.REAL
    if package_id:
        package = InstructorLessonPackage.objects.select_for_update().get(
            pk=package_id, instructor=locked, data_mode=mode
        )
        created = False
        was_active = package.is_active
    else:
        package = InstructorLessonPackage(instructor=locked, data_mode=mode)
        created = True
        was_active = False
    for field, value in data.items():
        setattr(package, field, value)
    if package.category not in locked.categories:
        raise ValidationError("Selecione uma categoria cadastrada no seu perfil.")
    if package.vehicle_included and not locked.vehicle_available:
        raise ValidationError("O perfil não informa veículo disponível para este pacote.")
    if package.is_active and not was_active:
        plan_code = effective_package_plan(actor)
        limit = PACKAGE_LIMITS[plan_code]
        count = (
            InstructorLessonPackage.objects.filter(
                instructor=locked, data_mode=mode, is_active=True
            )
            .exclude(pk=package.pk)
            .count()
        )
        if limit is not None and count >= limit:
            raise PackageLimitReached(plan_code, limit)
    package.full_clean()
    package.save()
    AuditEvent.objects.create(
        actor=actor,
        action="marketplace.lesson_package.created"
        if created
        else "marketplace.lesson_package.updated",
        target_type="marketplace.InstructorLessonPackage",
        target_id=package.pk,
        request_id=request_id,
        metadata={"active": package.is_active, "category": package.category, "created": created},
    )
    return package
