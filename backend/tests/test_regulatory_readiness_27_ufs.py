from datetime import date

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.test import Client
from django.urls import reverse

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.territories.management.commands.seed_regulatory_research import EVIDENCE
from apps.territories.models import RegulatoryReadiness, RegulatoryReadinessHistory
from apps.territories.policies import approved_instructor_publication_ufs
from apps.territories.services import (
    approve_instructor_publication_uf,
    set_instructor_publication_uf_review_state,
)


def complete_human_evidence(item):
    item.source_authority = "DETRAN-PR"
    item.source_consulted_at = date(2026, 9, 28)
    item.evidence = "Texto oficial e alterações conferidos; consulta individual confirmada."
    item.save()


@pytest.mark.django_db
def test_initial_inventory_is_idempotent_and_does_not_approve_any_uf():
    call_command("seed_territories", verbosity=0)
    assert len(EVIDENCE) == 27
    call_command("seed_regulatory_research", "--apply", verbosity=0)
    call_command("seed_regulatory_research", "--apply", verbosity=0)
    assert RegulatoryReadiness.objects.count() == 27
    assert RegulatoryReadinessHistory.objects.count() == 27
    assert not RegulatoryReadiness.objects.exclude(status="REVIEW_REQUIRED").exists()
    assert not approved_instructor_publication_ufs().exists()
    assert (
        AuditEvent.objects.filter(action="territories.regulatory_readiness_research_seed").count()
        == 27
    )


@pytest.mark.django_db
def test_only_identified_admin_can_approve_one_uf_with_audit_and_history():
    call_command("seed_territories", verbosity=0)
    call_command("seed_regulatory_research", "--apply", verbosity=0)
    item = RegulatoryReadiness.objects.get(federative_unit__code="PR")
    account = Account.objects.create_user(
        username="gilmar",
        email="gilmar-test@example.com",
        password="test-password",
        is_staff=True,
    )
    with pytest.raises(PermissionDenied):
        approve_instructor_publication_uf(
            actor=account, readiness_id=item.pk, valid_from=date(2026, 9, 28), reason="Revisado"
        )
    call_command("grant_regulatory_reviewer", "gilmar", "--apply", verbosity=0)
    account = Account.objects.get(pk=account.pk)
    with pytest.raises(ValidationError):
        approve_instructor_publication_uf(
            actor=account, readiness_id=item.pk, valid_from=date(2026, 9, 28), reason="Revisado"
        )
    complete_human_evidence(item)
    other_admin = Account.objects.create_user(
        username="other-admin",
        email="other-admin@example.com",
        password="test-password",
        is_staff=True,
        is_superuser=True,
    )
    with pytest.raises(PermissionDenied):
        approve_instructor_publication_uf(
            actor=other_admin,
            readiness_id=item.pk,
            valid_from=date(2026, 9, 28),
            reason="Não é o responsável designado",
        )
    item = approve_instructor_publication_uf(
        actor=account,
        readiness_id=item.pk,
        valid_from=date(2026, 9, 28),
        reason="Norma, alterações e consulta oficial confirmadas manualmente",
    )
    assert item.status == "APPROVED"
    assert item.reviewed_by == account
    assert item.approved_by == account
    assert item.reviewed_at and item.approved_at
    assert item.history.count() == 3
    assert AuditEvent.objects.filter(
        action="territories.regulatory_readiness_approve", target_id=item.pk
    ).exists()
    assert list(approved_instructor_publication_ufs().values_list("code", flat=True)) == ["PR"]

    blocked = set_instructor_publication_uf_review_state(
        actor=account, readiness_id=item.pk, status="SUSPENDED", reason="Nova norma sob análise"
    )
    assert blocked.status == "SUSPENDED"
    assert blocked.approved_by is None and blocked.approved_at is None
    assert blocked.history.count() == 4
    assert not approved_instructor_publication_ufs().exists()
    assert AuditEvent.objects.filter(
        action="territories.regulatory_readiness_review_state", target_id=item.pk
    ).exists()
    with pytest.raises(ValidationError):
        set_instructor_publication_uf_review_state(
            actor=account, readiness_id=item.pk, status="APPROVED", reason="Inválido"
        )
    pending = set_instructor_publication_uf_review_state(
        actor=account, readiness_id=item.pk, status="REVIEW_REQUIRED", reason="Nova consulta"
    )
    assert pending.status == "REVIEW_REQUIRED"
    assert pending.history.count() == 5


@pytest.mark.django_db
def test_admin_lists_27_pending_and_requires_explicit_confirmation():
    call_command("seed_territories", verbosity=0)
    call_command("seed_regulatory_research", "--apply", verbosity=0)
    account = Account.objects.create_user(
        username="gilmar",
        email="gilmar-admin@example.com",
        password="test-password",
        is_staff=True,
    )
    call_command("grant_regulatory_reviewer", "gilmar", "--apply", verbosity=0)
    web = Client()
    web.force_login(account)
    index = web.get(reverse("admin:territories_federativeunit_changelist"))
    assert index.status_code == 200
    assert "EM REVISÃO" in index.content.decode()
    item = RegulatoryReadiness.objects.get(federative_unit__code="RS")
    url = reverse("admin:territories_readiness_approve", args=[item.pk])
    assert web.get(url).status_code == 200
    assert web.post(url, {"valid_from": "2026-09-28", "reason": "teste"}).status_code == 302
    item.refresh_from_db()
    assert item.status == "REVIEW_REQUIRED"
    assert not approved_instructor_publication_ufs().exists()
    review_url = reverse("admin:territories_readiness_review_state", args=[item.pk])
    assert web.get(review_url).status_code == 200
    assert (
        web.post(review_url, {"status": "APPROVED", "reason": "não permitido"}).status_code == 302
    )
    item.refresh_from_db()
    assert item.status == "REVIEW_REQUIRED"
    assert (
        web.post(review_url, {"status": "SUSPENDED", "reason": "Revisão normativa"}).status_code
        == 302
    )
    item.refresh_from_db()
    assert item.status == "SUSPENDED"
    assert not approved_instructor_publication_ufs().exists()


@pytest.mark.django_db
def test_admin_can_approve_one_uf_and_revoke_it_without_terminal():
    call_command("seed_territories", verbosity=0)
    call_command("seed_regulatory_research", "--apply", verbosity=0)
    account = Account.objects.create_user(
        username="gilmar",
        email="gilmar-ui@example.com",
        password="test-password",
        is_staff=True,
    )
    call_command("grant_regulatory_reviewer", "gilmar", "--apply", verbosity=0)
    item = RegulatoryReadiness.objects.get(federative_unit__code="PR")
    complete_human_evidence(item)
    web = Client()
    web.force_login(account)
    approval_url = reverse("admin:territories_readiness_approve", args=[item.pk])
    assert web.get(approval_url).status_code == 200
    response = web.post(
        approval_url,
        {"valid_from": "2026-09-28", "reason": "Revisado", "confirm_current_source": "on"},
    )
    assert response.status_code == 302
    item.refresh_from_db()
    assert item.status == "APPROVED"
    assert item.approved_by == account
    assert list(approved_instructor_publication_ufs().values_list("code", flat=True)) == ["PR"]
    review_url = reverse("admin:territories_readiness_review_state", args=[item.pk])
    response = web.post(review_url, {"status": "SUSPENDED", "reason": "Ato superveniente"})
    assert response.status_code == 302
    item.refresh_from_db()
    assert item.status == "SUSPENDED"
    assert not approved_instructor_publication_ufs().exists()
