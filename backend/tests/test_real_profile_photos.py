from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.marketplace.documents import review_profile_photo
from apps.marketplace.models import ProfilePhoto
from apps.people.models import Person

ENABLED = {
    "REAL_PRODUCTION_AUTHORIZATION": "FULL_PRODUCTION",
    "REAL_DOCUMENT_UPLOADS": True,
    "PROFESSIONAL_DOCUMENT_UPLOAD_MODE": "PRODUCTION",
    "REAL_DOCUMENT_UPLOAD_ENABLED": True,
    "CLAMD_HOST": "clamav",
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
}


def owner_and_profile():
    owner = Account.objects.create_user(username="photo-owner", password="test-password-123")
    profile = InstructorProfile.objects.create(
        person=Person.objects.create(account=owner),
        display_name="Instrutor Real",
        categories=["A"],
        is_demo=False,
    )
    return owner, profile


def photo(name="perfil.png", content=b"\x89PNG\r\n\x1a\nprivate-test-data", mime="image/png"):
    return SimpleUploadedFile(name, content, content_type=mime)


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_real_photo_requires_consent_and_clean_scan_before_private_review(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, profile = owner_and_profile()
        client = APIClient()
        client.force_authenticate(owner)
        url = "/api/v1/instructor/profile-photo/"
        assert client.get(url).json()["upload_available"] is True
        assert (
            client.post(
                url, {"file": photo(), "publication_authorized": False}, format="multipart"
            ).status_code
            == 400
        )
        oversized = photo(content=b"\x89PNG\r\n\x1a\n" + b"x" * (5 * 1024 * 1024))
        assert (
            client.post(
                url, {"file": oversized, "publication_authorized": True}, format="multipart"
            ).status_code
            == 400
        )
        assert (
            client.post(
                url,
                {
                    "file": photo("perfil.pdf", b"%PDF-1.4", "application/pdf"),
                    "publication_authorized": True,
                },
                format="multipart",
            ).status_code
            == 400
        )
        with patch("apps.marketplace.profile_photos.scan_with_clamd", return_value="BLOCKED"):
            assert (
                client.post(
                    url, {"file": photo(), "publication_authorized": True}, format="multipart"
                ).status_code
                == 400
            )
        with patch(
            "apps.marketplace.profile_photos.scan_with_clamd", side_effect=OSError("scanner down")
        ):
            assert (
                client.post(
                    url, {"file": photo(), "publication_authorized": True}, format="multipart"
                ).status_code
                == 400
            )
        assert not ProfilePhoto.objects.exists()
        with patch("apps.marketplace.profile_photos.scan_with_clamd", return_value="CLEAN"):
            response = client.post(
                url, {"file": photo(), "publication_authorized": True}, format="multipart"
            )
        assert response.status_code == 201
        record = ProfilePhoto.objects.get()
        assert record.instructor == profile and record.status == ProfilePhoto.Status.PENDING
        assert record.data_mode == "REAL" and record.publication_authorized_at
        assert response.json()["private_preview_url"].endswith(f"/{record.id}/download/")
        assert AuditEvent.objects.filter(
            action="marketplace.profile_photo.uploaded", target_id=record.id
        ).exists()
        with patch("apps.marketplace.profile_photos.scan_with_clamd", return_value="CLEAN"):
            assert (
                client.post(
                    url, {"file": photo(), "publication_authorized": True}, format="multipart"
                ).status_code
                == 400
            )
        assert ProfilePhoto.objects.count() == 1


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_real_photo_is_private_until_review_and_profile_eligibility(tmp_path):
    with override_settings(MEDIA_ROOT=tmp_path):
        owner, profile = owner_and_profile()
        client = APIClient()
        client.force_authenticate(owner)
        with patch("apps.marketplace.profile_photos.scan_with_clamd", return_value="CLEAN"):
            client.post(
                "/api/v1/instructor/profile-photo/",
                {"file": photo(), "publication_authorized": True},
                format="multipart",
            )
        record = ProfilePhoto.objects.get()
        public_url = f"/api/v1/instructors/profile-photos/{record.id}/"
        private_url = f"/api/v1/marketplace/profile-photos/{record.id}/download/"
        assert APIClient().get(public_url).status_code == 404
        outsider = Account.objects.create_user(
            username="photo-outsider",
            email="photo-outsider@example.invalid",
            password="test-password-123",
        )
        client.force_authenticate(outsider)
        assert client.get(private_url).status_code == 403
        assert client.get("/api/v1/instructor/profile-photo/").status_code == 404
        client.force_authenticate(owner)
        private = client.get(private_url)
        assert private.status_code == 200 and private["Cache-Control"] == "private, no-store"
        reviewer = Account.objects.create_user(
            username="photo-reviewer",
            email="photo-reviewer@example.invalid",
            password="test-password-123",
        )
        reviewer.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="marketplace", codename="review_profile_photo"
            )
        )
        review_profile_photo(
            actor=reviewer,
            photo=record,
            decision=ProfilePhoto.Status.APPROVED,
            reason="PHOTO_CHECKED",
        )
        assert APIClient().get(public_url).status_code == 404
        with patch(
            "apps.discovery.api.published_instructor_profiles",
            return_value=InstructorProfile.objects.filter(pk=profile.pk),
        ):
            public = APIClient().get(public_url)
        assert public.status_code == 200 and public["Content-Type"] == "image/png"
        public.close()
        private.close()
