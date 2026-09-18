import hashlib

import pytest
from django.contrib import admin
from django.test import RequestFactory
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.privacy.admin import LegalAcceptanceRecordAdmin, LegalDocumentAdmin
from apps.privacy.models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice


def account(username):
    return Account.objects.create_user(
        username=username,
        email=f"{username}@example.invalid",
        password="safe-test-password",
    )


def authenticated(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize("audience", ["student", "instructor"])
def test_current_terms_are_public_versioned_and_hash_matches(audience):
    response = APIClient().get(f"/api/v1/legal/documents/{audience}/")

    assert response.status_code == 200
    assert response.data["version"] == "1.0"
    assert response.data["contact"] == "focusgtba@gmail.com"
    assert (
        response.data["content_sha256"]
        == hashlib.sha256(response.data["content"].encode("utf-8")).hexdigest()
    )
    assert "InstrutorProCNH" in response.data["title"]


@pytest.mark.django_db
def test_acceptance_requires_both_explicit_confirmations():
    user = account("legal-reject")

    response = authenticated(user).post(
        "/api/v1/legal/acceptances/",
        {"audience": "STUDENT", "accept_terms": True, "acknowledge_privacy": False},
        format="json",
    )

    assert response.status_code == 400
    assert not LegalAcceptanceRecord.objects.filter(account=user).exists()


@pytest.mark.django_db
def test_acceptance_records_exact_terms_and_privacy_versions_and_is_idempotent():
    user = account("legal-accept")
    client = authenticated(user)
    payload = {"audience": "STUDENT", "accept_terms": True, "acknowledge_privacy": True}

    first = client.post("/api/v1/legal/acceptances/", payload, format="json")
    second = client.post("/api/v1/legal/acceptances/", payload, format="json")

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.data["id"] == second.data["id"]
    row = LegalAcceptanceRecord.objects.get(account=user)
    assert row.terms_document.version == "1.0"
    assert row.privacy_notice.version == "2026-09-16"
    assert (
        AuditEvent.objects.filter(
            actor=user, action="privacy.legal_terms.accepted", target_id=row.id
        ).count()
        == 1
    )
    history = client.get("/api/v1/legal/acceptances/")
    assert history.status_code == 200
    assert history.data[0]["terms_sha256"] == row.terms_document.content_sha256


@pytest.mark.django_db
def test_acceptance_history_is_object_scoped():
    owner = account("legal-owner")
    other = account("legal-other")
    authenticated(owner).post(
        "/api/v1/legal/acceptances/",
        {"audience": "INSTRUCTOR", "accept_terms": True, "acknowledge_privacy": True},
        format="json",
    )

    assert authenticated(other).get("/api/v1/legal/acceptances/").data == []


@pytest.mark.django_db
def test_acceptance_record_cannot_be_changed_or_deleted():
    user = account("legal-immutable")
    terms = LegalDocument.objects.get(audience="STUDENT", is_active=True)
    privacy = PrivacyNotice.objects.get(is_current=True)
    row = LegalAcceptanceRecord.objects.create(
        account=user, terms_document=terms, privacy_notice=privacy
    )

    row.request_id = None
    with pytest.raises(ValueError, match="immutable"):
        row.save()
    with pytest.raises(ValueError, match="immutable"):
        row.delete()


@pytest.mark.django_db
def test_published_terms_content_cannot_be_rewritten():
    terms = LegalDocument.objects.get(audience="STUDENT", is_active=True)
    terms.content = "conteúdo substituído"

    with pytest.raises(ValueError, match="create a new version"):
        terms.save()


@pytest.mark.django_db
def test_missing_current_terms_fails_closed():
    LegalDocument.objects.filter(audience="STUDENT").update(is_active=False)
    user = account("legal-missing")

    response = authenticated(user).post(
        "/api/v1/legal/acceptances/",
        {"audience": "STUDENT", "accept_terms": True, "acknowledge_privacy": True},
        format="json",
    )

    assert response.status_code == 409
    assert not LegalAcceptanceRecord.objects.filter(account=user).exists()


@pytest.mark.django_db
def test_new_terms_version_requires_and_preserves_new_acceptance():
    user = account("legal-versioned")
    client = authenticated(user)
    payload = {"audience": "STUDENT", "accept_terms": True, "acknowledge_privacy": True}
    assert client.post("/api/v1/legal/acceptances/", payload, format="json").status_code == 201
    old = LegalDocument.objects.get(audience="STUDENT", version="1.0")
    old.is_active = False
    old.save(update_fields=["is_active", "content_sha256"])
    new = LegalDocument.objects.create(
        document_type="TERMS",
        audience="STUDENT",
        version="1.1",
        title="Termos de Uso — Aluno — InstrutorProCNH",
        content=old.content + "\n\nNova versão.",
        effective_at=timezone.now(),
        is_active=True,
    )

    assert client.post("/api/v1/legal/acceptances/", payload, format="json").status_code == 201
    versions = set(
        LegalAcceptanceRecord.objects.filter(account=user).values_list(
            "terms_document__version", flat=True
        )
    )
    assert versions == {"1.0", "1.1"}
    assert new.acceptances.filter(account=user).exists()


@pytest.mark.django_db
def test_admin_cannot_change_or_delete_acceptance_and_counts_documents():
    administrator = account("legal-admin")
    user = account("legal-admin-user")
    terms = LegalDocument.objects.get(audience="STUDENT", is_active=True)
    privacy = PrivacyNotice.objects.get(is_current=True)
    LegalAcceptanceRecord.objects.create(account=user, terms_document=terms, privacy_notice=privacy)
    request = RequestFactory().get("/admin/privacy/")
    request.user = administrator
    acceptance_admin = LegalAcceptanceRecordAdmin(LegalAcceptanceRecord, admin.site)
    document_admin = LegalDocumentAdmin(LegalDocument, admin.site)

    assert not acceptance_admin.has_change_permission(request)
    assert not acceptance_admin.has_delete_permission(request)
    document = document_admin.get_queryset(request).get(pk=terms.pk)
    assert document_admin.acceptance_count(document) == 1
