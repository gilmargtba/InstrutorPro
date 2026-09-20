from django.db.models import Q
from django.utils import timezone

from .models import FederativeUnit, RegulatoryReadiness

INSTRUCTOR_PUBLICATION_CAPABILITY = "INSTRUCTOR_PUBLICATION"
INSTRUCTOR_PROVIDER_TYPE = "INSTRUCTOR"


def approved_instructor_publication_ufs(*, on_date=None):
    """Return UFs with an explicit, currently valid publication approval."""
    day = on_date or timezone.localdate()
    return FederativeUnit.objects.filter(
        regulatory_readiness__provider_type=INSTRUCTOR_PROVIDER_TYPE,
        regulatory_readiness__capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        regulatory_readiness__status=RegulatoryReadiness.Status.APPROVED,
    ).filter(
        Q(regulatory_readiness__valid_from__isnull=True)
        | Q(regulatory_readiness__valid_from__lte=day),
        Q(regulatory_readiness__valid_until__isnull=True)
        | Q(regulatory_readiness__valid_until__gte=day),
    )


def instructor_publication_is_allowed(uf, *, on_date=None):
    return approved_instructor_publication_ufs(on_date=on_date).filter(code=uf.upper()).exists()
