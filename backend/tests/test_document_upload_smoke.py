from unittest.mock import patch

import pytest
from django.conf import settings
from django.db import transaction
from django.test import override_settings

from apps.marketplace.management.commands.check_document_upload import EICAR, Command
from apps.marketplace.real_documents import DocumentUploadError
from tests.test_real_professional_documents import ENABLED


@pytest.mark.django_db
@override_settings(**ENABLED)
def test_live_smoke_pipeline_authorization_and_restore_logic(tmp_path):
    def scanner(file):
        if settings.CLAMD_HOST == "127.0.0.1":
            raise DocumentUploadError("Test-only scanner outage")
        content = file.read()
        file.seek(0)
        return "BLOCKED" if EICAR in content else "CLEAN"

    with override_settings(MEDIA_ROOT=tmp_path):
        with patch("apps.marketplace.real_documents.scan_with_clamd", side_effect=scanner):
            with transaction.atomic():
                Command().exercise_pipeline(str(tmp_path))
                transaction.set_rollback(True)
