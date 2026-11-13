import hashlib
import re
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.people.identifiers import _fernet, fingerprint_identifier
from apps.territories.models import FederativeUnit

from .models import AvailabilityInterest, AvailabilityInterestPolicy


def active_interest_policy():
    policy = (
        AvailabilityInterestPolicy.objects.select_related("privacy_notice")
        .filter(pk=1, enabled=True)
        .first()
    )
    if not policy:
        return None
    try:
        policy.full_clean()
    except Exception:
        return None
    return policy


class InterestValidationError(ValueError):
    pass


def validate_interest_data(data):
    data["uf"] = data["uf"].upper()
    data["city"] = data.get("city", "").strip()
    data["region"] = data.get("region", "").strip()
    if len(data["name"].strip().split()) < 2:
        raise InterestValidationError("Informe seu nome completo.")
    if (
        data["scope"] in (AvailabilityInterest.Scope.CITY, AvailabilityInterest.Scope.REGION)
        and not data["city"]
    ):
        raise InterestValidationError("Informe a cidade da busca.")
    if data["scope"] == AvailabilityInterest.Scope.REGION and not data["region"]:
        raise InterestValidationError("Informe a região da cidade.")
    if data["scope"] == AvailabilityInterest.Scope.UF:
        data["city"] = data["region"] = ""
    elif data["scope"] == AvailabilityInterest.Scope.CITY:
        data["region"] = ""
    if not FederativeUnit.objects.filter(code=data["uf"]).exists():
        raise InterestValidationError("UF inválida.")
    if len(re.sub(r"\D", "", data["phone"])) not in (10, 11):
        raise InterestValidationError("Informe telefone brasileiro com DDD.")
    today = date.today()
    birth_date = data["birth_date"]
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
    if age < 18:
        raise InterestValidationError("Cadastro restrito a maiores de 18 anos.")
    if not data["consent_granted"]:
        raise InterestValidationError("Consentimento necessário para este aviso.")


def create_availability_interest(*, data, request_id=None):
    """All personal data stays private; a retry key cannot create a second lead."""
    with transaction.atomic():
        validate_interest_data(data)
        policy = (
            AvailabilityInterestPolicy.objects.select_for_update(of=("self",))
            .select_related("privacy_notice")
            .filter(pk=1)
            .first()
        )
        if not policy or not policy.enabled:
            raise ValueError("O aviso de disponibilidade não está ativo.")
        policy.full_clean()
        if (
            data["privacy_notice_version"] != policy.privacy_notice.version
            or data["consent_version"] != policy.consent_version
        ):
            raise ValueError("O aviso de privacidade mudou. Leia e aceite a versão atual.")
        existing = AvailabilityInterest.objects.filter(
            idempotency_key=data["idempotency_key"]
        ).first()
        if existing:
            return existing, False
        phone = re.sub(r"\D", "", data["phone"])
        now = timezone.now()
        item = AvailabilityInterest.objects.create(
            scope=data["scope"],
            city=data["city"],
            region=data["region"],
            uf=data["uf"],
            name_encrypted=_fernet().encrypt(data["name"].strip().encode("utf-8")).decode("ascii"),
            phone_encrypted=_fernet().encrypt(phone.encode("ascii")).decode("ascii"),
            phone_fingerprint=fingerprint_identifier(phone),
            idempotency_key=data["idempotency_key"],
            privacy_notice=policy.privacy_notice,
            consent_version=policy.consent_version,
            consent_text_sha256=hashlib.sha256(policy.consent_text.encode("utf-8")).hexdigest(),
            consented_at=now,
            expires_at=now + timedelta(days=policy.retention_days),
        )
        AuditEvent.objects.create(
            action="marketplace.availability_interest.created",
            target_type="marketplace.AvailabilityInterest",
            target_id=item.pk,
            request_id=request_id,
            metadata={
                "uf": item.uf,
                "scope": item.scope,
                "privacy_notice_version": policy.privacy_notice.version,
            },
        )
        return item, True


def purge_expired_availability_interests():
    """Remove expired contact data in bounded batches; no personal data in logs."""
    total = 0
    while True:
        ids = list(
            AvailabilityInterest.objects.filter(expires_at__lte=timezone.now()).values_list(
                "pk", flat=True
            )[:500]
        )
        if not ids:
            return total
        deleted, _ = AvailabilityInterest.objects.filter(pk__in=ids).delete()
        total += deleted


def withdraw_availability_interest(*, reference, phone, request_id=None):
    digits = re.sub(r"\D", "", phone)
    with transaction.atomic():
        item = AvailabilityInterest.objects.select_for_update().filter(pk=reference).first()
        if not item or item.phone_fingerprint != fingerprint_identifier(digits):
            return False
        AuditEvent.objects.create(
            action="marketplace.availability_interest.withdrawn",
            target_type="marketplace.AvailabilityInterest",
            target_id=item.pk,
            request_id=request_id,
        )
        item.delete()
        return True
