from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.accounts.models import Account


ROLE_ASSIGNMENT_PERMISSION = "people.manage_role_assignments"


def can_manage_role_assignments(*, actor: Account | None) -> bool:
    if not actor or not actor.can_operate or not actor.is_authenticated:
        return False
    permission_filter = {
        "content_type__app_label": "people",
        "codename": "manage_role_assignments",
    }
    return bool(
        actor.user_permissions.filter(**permission_filter).exists()
        or actor.groups.filter(permissions__codename="manage_role_assignments")
        .filter(permissions__content_type__app_label="people")
        .exists()
    )
