"""Owner-managed category offers; publication remains a separate human decision."""

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from apps.audit.models import AuditEvent

from .models import DataMode, InstructorOffer


@transaction.atomic
def save_owner_category_offers(*, actor, profile, offers, request_id=None):
    locked = (
        type(profile)
        .objects.select_for_update()
        .select_related("person__account")
        .get(pk=profile.pk)
    )
    if actor != locked.person.account:
        raise PermissionDenied("Somente o titular pode editar suas ofertas.")
    selected = set(locked.categories)
    categories = [item["category"] for item in offers]
    if len(categories) != len(set(categories)) or not set(categories).issubset(selected):
        raise ValidationError("Cada oferta deve ter uma categoria distinta cadastrada no perfil.")
    mode = DataMode.SYNTHETIC if locked.is_demo else DataMode.REAL
    for item in offers:
        offer = (
            InstructorOffer.objects.select_for_update()
            .filter(instructor=locked, category=item["category"], data_mode=mode)
            .order_by("-is_active", "-created_at")
            .first()
        )
        created = offer is None
        if created:
            offer = InstructorOffer(instructor=locked, category=item["category"], data_mode=mode)
        changed = (
            created
            or offer.price_amount != item["price_amount"]
            or offer.duration_minutes != item["duration_minutes"]
        )
        if not changed:
            continue
        offer.price_amount = item["price_amount"]
        offer.duration_minutes = item["duration_minutes"]
        offer.full_clean()
        offer.save()
        AuditEvent.objects.create(
            actor=actor,
            action="marketplace.instructor_offer.owner_saved",
            target_type="marketplace.InstructorOffer",
            target_id=offer.pk,
            request_id=request_id,
            metadata={"category": offer.category, "created": created, "data_mode": mode},
        )
