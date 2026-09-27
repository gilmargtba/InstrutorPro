"""Opt-in live technical smoke; database changes roll back and only its temp files are removed."""

import hashlib
import socket
import tarfile
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.core.signals import request_finished
from django.db import close_old_connections, transaction
from django.test import override_settings
from rest_framework.test import APIClient

from apps.accounts.models import Account
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.discovery.verification_services import save_verification_draft, start_verification_review
from apps.marketplace.real_documents import (
    DocumentUploadError,
    inspect_real_upload,
    scan_with_clamd,
)
from apps.people.models import Person, RoleAssignment

EICAR = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
PDF = b"%PDF-1.4\nTechnical upload smoke only\n%%EOF"
UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()


def sample(content=PDF, name="technical.pdf", mime="application/pdf"):
    return SimpleUploadedFile(name, content, content_type=mime)


def expect(condition, message):
    if not condition:
        raise CommandError(message)


def synthetic_cpf():
    digits = f"{uuid4().int % 1_000_000_000:09d}"
    for size in (9, 10):
        check = sum(int(digit) * (size + 1 - index) for index, digit in enumerate(digits)) * 10 % 11
        digits += str(0 if check == 10 else check)
    return digits


class Command(BaseCommand):
    help = "Technical upload smoke with real ClamAV, rollback and private-volume temp files."

    def add_arguments(self, parser):
        parser.add_argument("--confirm-technical-test", action="store_true")
        parser.add_argument("--public-origin", default="https://instrutorprocnh.com.br")

    def handle(self, *args, **options):
        if not options["confirm_technical_test"]:
            raise CommandError("Use --confirm-technical-test; synthetic accounts and files only.")
        root = Path(settings.MEDIA_ROOT).resolve()
        expect(
            root.is_dir() and root != Path(settings.BASE_DIR).resolve(),
            "Private storage unavailable",
        )
        expect(bool(settings.CLAMD_HOST), "CLAMD_HOST not configured")
        with socket.create_connection(
            (settings.CLAMD_HOST, settings.CLAMD_PORT), timeout=5
        ) as conn:
            conn.sendall(b"zVERSION\0")
            version = conn.recv(1024).decode().strip("\0\n")
        self.stdout.write(f"CLAMD_VERSION={version}")
        try:
            signature_date = datetime.strptime(
                version.split("/", 2)[2], "%a %b %d %H:%M:%S %Y"
            ).replace(tzinfo=UTC)
        except (ValueError, IndexError) as exc:
            raise CommandError("Cannot confirm signature date") from exc
        expect(
            timedelta(0) <= datetime.now(UTC) - signature_date < timedelta(hours=48),
            "Loaded signatures are not recent (48h technical gate)",
        )
        self.stdout.write("CLAMAV_SIGNATURE_STATUS=RECENT")
        expect(scan_with_clamd(sample()) == "CLEAN", "Clean scan failed")
        expect(
            scan_with_clamd(sample(EICAR, "technical.txt", "text/plain")) == "BLOCKED",
            "EICAR failed",
        )
        with override_settings(CLAMD_HOST="127.0.0.1", CLAMD_PORT=1):
            try:
                scan_with_clamd(sample())
            except DocumentUploadError:
                pass
            else:
                raise CommandError("Scanner outage did not fail closed")
        for file in (
            sample(name="bad.pdf.exe"),
            sample(mime="text/plain"),
            sample(b"MZ executable"),
        ):
            try:
                inspect_real_upload(file)
            except DocumentUploadError:
                pass
            else:
                raise CommandError("Invalid file accepted")
        with override_settings(INSTRUCTOR_DOCUMENT_MAX_BYTES=1):
            try:
                inspect_real_upload(sample())
            except DocumentUploadError:
                pass
            else:
                raise CommandError("Oversized file accepted")

        # This directory is inside the real mounted private volume, never /tmp storage.
        with tempfile.TemporaryDirectory(prefix="technical-upload-", dir=root) as directory:
            probe = Path(directory) / "technical-public-probe.pdf"
            probe.write_bytes(PDF)
            origin = options["public_origin"].rstrip("/")
            expect(origin.startswith("https://"), "HTTPS public origin required")
            for prefix in (
                "media",
                "documents",
                "uploads",
                "private",
                "private_documents",
                "quarantine",
                "professional-documents",
            ):
                try:
                    with urlopen(
                        f"{origin}/{prefix}/{Path(directory).name}/{probe.name}", timeout=20
                    ) as response:
                        code = response.status
                except HTTPError as exc:
                    code = exc.code
                expect(code in (403, 404), f"Public direct access not denied: {prefix} HTTP {code}")
            self.stdout.write("PUBLIC_DIRECT_ACCESS=BLOCKED")
            with override_settings(
                MEDIA_ROOT=directory,
                ALLOWED_HOSTS=[*settings.ALLOWED_HOSTS, "testserver"],
                SECURE_SSL_REDIRECT=False,
                REAL_DOCUMENT_UPLOADS=True,
                REAL_DOCUMENT_UPLOAD_ENABLED=True,
                PROFESSIONAL_DOCUMENT_UPLOAD_MODE="PRODUCTION",
            ):
                with transaction.atomic():
                    self.exercise_pipeline(directory)
                    transaction.set_rollback(True)
        self.stdout.write("TECHNICAL_TEST_DATA_REMOVED=YES")
        self.stdout.write("PRODUCTION_FLAGS_ACTIVATED=NO")
        self.stdout.write("DOCUMENT_TECHNICAL_SMOKE=PASS")

    def exercise_pipeline(self, directory):
        tag = uuid4().hex

        def account(role):
            user = Account.objects.create_user(
                username=f"smoke-{role}-{tag}", email=f"{role}-{tag}@example.invalid"
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])
            return user

        owner, other, student, reviewer, unauthorized, unassigned = [
            account(role)
            for role in ("owner", "other", "student", "reviewer", "unauthorized", "unassigned")
        ]
        unauthorized.is_staff = True
        unauthorized.save(update_fields=["is_staff"])
        RoleAssignment.objects.create(
            person=Person.objects.create(account=student),
            role="STUDENT",
            grant_reason="TECHNICAL_SMOKE_ROLLBACK_ONLY",
        )
        person = Person.objects.create(account=owner)
        instructor = InstructorProfile.objects.create(
            person=person, display_name="Technical smoke", categories=["B"], is_demo=False
        )
        area = InstructorServiceArea.objects.create(
            profile=instructor, city="Teste técnico", uf="GO"
        )
        item = save_verification_draft(actor=owner, profile=instructor, cpf=synthetic_cpf())
        client = APIClient()
        client.force_authenticate(owner)
        for uf in UFS:
            area.uf = uf
            area.save(update_fields=["uf"])
            expect(
                client.get("/api/v1/instructor/verification/").json()["document_upload_available"],
                f"Upload unavailable in {uf}",
            )
        area.uf = "GO"
        area.save(update_fields=["uf"])
        # Actual approved requirements are deliberately not fabricated or changed.
        url = "/api/v1/instructor/verification/documents/"

        def upload(content=PDF):
            return client.post(
                url,
                {"document_type": "OTHER_PROFESSIONAL", "file": sample(content)},
                format="multipart",
            )

        expect(upload().status_code == 201, "Generic pipeline failed")
        clean = item.documents.get()
        expect(
            clean.scan_status == "CLEAN" and clean.file.name.startswith("professional-documents/"),
            "Promotion failed",
        )
        with clean.file.open("rb") as handle:
            expect(
                hashlib.sha256(handle.read()).hexdigest() == clean.sha256, "Stored content differs"
            )
        # Archive and restore only this known synthetic file into a separate directory.
        archive = Path(directory) / "technical.tar"
        with tarfile.open(archive, "w") as tar:
            tar.add(clean.file.path, arcname="technical.pdf")
        with tarfile.open(archive) as tar:
            with tar.extractfile("technical.pdf") as source:
                restored = Path(directory) / "restored-technical.pdf"
                restored.write_bytes(source.read())
        expect(
            hashlib.sha256(restored.read_bytes()).hexdigest() == clean.sha256,
            "Restore hash differs",
        )
        expect(
            upload(b"%PDF-1.4\n" + EICAR).status_code == 201,
            "EICAR pipeline rejected before scanner",
        )
        blocked = item.documents.get(scan_status="BLOCKED")
        # on_commit deletion is intentionally deferred by this rollback-only smoke.
        expect(blocked.file.name.startswith("quarantine/"), "Blocked evidence was promoted")
        expect(
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 400,
            "Blocked evidence submitted",
        )
        blocked.delete()
        with override_settings(CLAMD_HOST="127.0.0.1", CLAMD_PORT=1):
            expect(upload().status_code == 201, "Outage ingestion failed")
        pending = item.documents.get(scan_status="PENDING")
        expect(pending.file.name.startswith("quarantine/"), "Outage escaped quarantine")
        expect(
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 400,
            "Pending evidence submitted",
        )
        pending.delete()
        # An approved mandatory territorial rule may require further documents in real production.
        # The technical request uses a transaction-local empty category list, not a fabricated rule.
        instructor.categories = []
        instructor.save(update_fields=["categories"])
        expect(
            client.post("/api/v1/instructor/verification/submit/", {}, format="json").status_code
            == 201,
            "Generic clean submission failed",
        )
        for user in (reviewer, unassigned):
            user.is_staff = True
            user.save(update_fields=["is_staff"])
            user.user_permissions.add(
                *Permission.objects.filter(
                    codename__in=["review_professional_verification", "review_instructor_document"]
                )
            )
        start_verification_review(actor=reviewer, verification_request=item)
        download_url = f"/api/v1/marketplace/instructor-documents/{clean.pk}/download/"
        client.force_authenticate(owner)
        expect(client.get(download_url).status_code == 403, "Owner accessed reviewer-only download")
        expect(
            client.delete(f"{url}{clean.pk}/").status_code == 400,
            "Owner removed submitted evidence",
        )
        for user in (None, other, student, unauthorized, unassigned):
            client.force_authenticate(user)
            expect(client.get(download_url).status_code in (401, 403), "Unauthorized download")
            expect(
                client.delete(f"{url}{clean.pk}/").status_code in (401, 403, 404),
                "Unauthorized deletion",
            )
        client.force_authenticate(reviewer)
        other_profile = InstructorProfile.objects.create(
            person=Person.objects.create(account=other),
            display_name="Other technical instructor",
            categories=[],
            is_demo=False,
        )
        other_request = save_verification_draft(
            actor=other, profile=other_profile, cpf=synthetic_cpf()
        )
        client.force_authenticate(other)
        expect(upload().status_code == 201, "Other instructor technical upload failed")
        other_document = other_request.documents.get()
        client.force_authenticate(reviewer)
        expect(
            client.get(
                f"/api/v1/marketplace/instructor-documents/{other_document.pk}/download/"
            ).status_code
            == 403,
            "Swapped document ID was exposed",
        )
        response = client.get(download_url)
        expect(response.status_code == 200, "Assigned reviewer cannot download")
        try:
            expect(
                hashlib.sha256(b"".join(response.streaming_content)).hexdigest() == clean.sha256,
                "Reviewer received wrong file",
            )
        finally:
            # FileResponse.close emits request_finished; this CLI deliberately holds
            # a rollback-only transaction across requests. Do not close its connection.
            disconnected = request_finished.disconnect(close_old_connections)
            try:
                response.close()
            finally:
                if disconnected:
                    request_finished.connect(close_old_connections)
        expect(
            client.get(f"/api/v1/marketplace/instructor-documents/{uuid4()}/download/").status_code
            == 404,
            "IDOR lookup failed",
        )
        instructor.refresh_from_db()
        expect(
            instructor.verification_status != "VERIFIED"
            and instructor.publication_status == "UNPUBLISHED",
            "Automatic verification/publication occurred",
        )
        for name in (
            "PRIVATE_STORAGE",
            "CLEAN_PIPELINE",
            "EICAR_DETECTION",
            "ANTIMALWARE_FAIL_CLOSED",
            "FILE_VALIDATION",
            "AUTHORIZATION",
            "IDOR_PROTECTION",
            "TECHNICAL_DOCUMENT_BACKUP",
            "TECHNICAL_DOCUMENT_RESTORE",
        ):
            self.stdout.write(f"{name}=PASS")
