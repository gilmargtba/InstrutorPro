from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Account


def _has_explicit_permission(*, actor: Account, codename: str) -> bool:
    direct = actor.user_permissions.filter(
        content_type__app_label="accounts", codename=codename
    ).exists()
    through_group = actor.groups.filter(
        permissions__content_type__app_label="accounts",
        permissions__codename=codename,
    ).exists()
    return direct or through_group


def can_manage_account_lifecycle(*, actor: Account | None) -> bool:
    return bool(
        actor
        and actor.is_authenticated
        and actor.can_operate
        and _has_explicit_permission(actor=actor, codename="manage_account_lifecycle")
    )


def can_account_operate(*, account: Account | None) -> bool:
    return bool(account and account.is_authenticated and account.can_operate)
