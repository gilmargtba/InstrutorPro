from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.accounts.models import Account


def _has_explicit_permission(*, actor: Account, codename: str) -> bool:
    direct = actor.user_permissions.filter(
        content_type__app_label="organizations", codename=codename
    ).exists()
    through_group = actor.groups.filter(
        permissions__content_type__app_label="organizations",
        permissions__codename=codename,
    ).exists()
    return direct or through_group


def can_manage_platform_organization(*, actor: Account | None) -> bool:
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and _has_explicit_permission(actor=actor, codename="manage_platform_organization")
    )


def can_validate_platform_organization(*, actor: Account | None) -> bool:
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and _has_explicit_permission(actor=actor, codename="validate_platform_organization")
    )
