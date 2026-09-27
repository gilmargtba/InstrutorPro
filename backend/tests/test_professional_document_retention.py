from datetime import timedelta

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.marketplace.models import (
    DataMode,
    DocumentRequirement,
    DocumentRetentionPolicy,
    InstructorDocument,
)
from apps.marketplace.professional_retention import (
    enforce_professional_document_retention,
    schedule_document_retention,
)
from apps.people.models import Person


def _document(scope):
    owner = Account.objects.create_user(
        username=f"owner-{scope.lower()}",
        email=f"owner-{scope.lower()}@example.invalid",
        password="test-password-123",
    )
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner),
        display_name="Instrutor teste",
        categories=["B"],
        is_demo=scope == DocumentRetentionPolicy.Scope.TEST,
    )
    requirement = DocumentRequirement.objects.create(
        uf="GO",
        category="B",
        document_type=DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION,
        rule_version="retention-test-v1",
        label="Documento técnico de teste",
        active_from=timezone.localdate(),
    )
    document = InstructorDocument.objects.create(
        instructor=profile,
        requirement=requirement,
        file=SimpleUploadedFile("test.pdf", b"%PDF-1.4\ntechnical-only"),
        original_name="test.pdf",
        mime_type="application/pdf",
        size_bytes=23,
        sha256="0" * 64,
        data_mode=(
            DataMode.SYNTHETIC if scope == DocumentRetentionPolicy.Scope.TEST else DataMode.REAL
        ),
    )
    return owner, document


def _policy(scope, approver):
    return DocumentRetentionPolicy.objects.create(
        scope=scope,
        rule_version="TEST_ONLY_v1" if scope == DocumentRetentionPolicy.Scope.TEST else "v1",
        retention_days=1,
        source_reference=(
            "TEST_ONLY" if scope == DocumentRetentionPolicy.Scope.TEST else "UNAPPROVED"
        ),
        approved_at=timezone.now() if scope == DocumentRetentionPolicy.Scope.TEST else None,
        approved_by=approver if scope == DocumentRetentionPolicy.Scope.TEST else None,
        active=True,
    )


@pytest.mark.django_db(transaction=True)
def test_test_policy_deletes_only_expired_technical_file_and_keeps_audit(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, document = _document(DocumentRetentionPolicy.Scope.TEST)
        policy = _policy(DocumentRetentionPolicy.Scope.TEST, owner)
        past = timezone.now() - timedelta(days=3)
        assert schedule_document_retention(document, now=past)
        assert document.retention_policy_id == policy.pk
        storage_key = document.file.name
        assert document.file.storage.exists(storage_key)

        dry_run = enforce_professional_document_retention(
            scope=DocumentRetentionPolicy.Scope.TEST, dry_run=True
        )
        assert dry_run.eligible == 1 and dry_run.processed == 0
        assert document.file.storage.exists(storage_key)

        result = enforce_professional_document_retention(
            scope=DocumentRetentionPolicy.Scope.TEST, dry_run=False
        )
        assert result.processed == 1
        assert not InstructorDocument.objects.filter(pk=document.pk).exists()
        assert not document.file.storage.exists(storage_key)
        assert AuditEvent.objects.filter(
            action="marketplace.professional_document.retention_deleted", target_id=document.pk
        ).exists()


@pytest.mark.django_db
def test_legal_hold_and_unapproved_production_policy_block_deletion(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, document = _document(DocumentRetentionPolicy.Scope.TEST)
        _policy(DocumentRetentionPolicy.Scope.TEST, owner)
        assert schedule_document_retention(document, now=timezone.now() - timedelta(days=3))
        document.legal_hold = True
        document.save(update_fields=["legal_hold"])
        held = enforce_professional_document_retention(
            scope=DocumentRetentionPolicy.Scope.TEST, dry_run=False
        )
        assert held.eligible == 0 and InstructorDocument.objects.filter(pk=document.pk).exists()

        _policy(DocumentRetentionPolicy.Scope.PRODUCTION, owner)
        production = enforce_professional_document_retention(
            scope=DocumentRetentionPolicy.Scope.PRODUCTION, dry_run=False
        )
        assert not production.policy_available and production.processed == 0


@pytest.mark.django_db(transaction=True)
def test_storage_failure_preserves_record_and_audit_for_retry(tmp_path, monkeypatch):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, document = _document(DocumentRetentionPolicy.Scope.TEST)
        _policy(DocumentRetentionPolicy.Scope.TEST, owner)
        assert schedule_document_retention(document, now=timezone.now() - timedelta(days=3))
        storage_key = document.file.name
        storage = document.file.storage
        original_delete = storage.delete

        def unavailable(name):
            raise OSError("Technical storage failure")

        monkeypatch.setattr(storage, "delete", unavailable)
        with pytest.raises(OSError):
            enforce_professional_document_retention(
                scope=DocumentRetentionPolicy.Scope.TEST, dry_run=False
            )
        assert InstructorDocument.objects.filter(pk=document.pk).exists()
        assert storage.exists(storage_key)
        assert not AuditEvent.objects.filter(
            action="marketplace.professional_document.retention_deleted", target_id=document.pk
        ).exists()
        monkeypatch.setattr(storage, "delete", original_delete)
        result = enforce_professional_document_retention(
            scope=DocumentRetentionPolicy.Scope.TEST, dry_run=False
        )
        assert result.processed == 1
