"""Regression checks for private-document deployment configuration."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DocumentDeploymentTests(unittest.TestCase):
    def test_document_prefixes_return_404_before_spa_fallback(self):
        config = (ROOT / "frontend/nginx.demo.conf").read_text(encoding="utf-8")
        block = re.search(r"location ~ (\S+) \{\s*return 404;\s*\}", config)
        self.assertIsNotNone(block)
        for prefix in (
            "media",
            "documents",
            "uploads",
            "private",
            "private_documents",
            "quarantine",
            "professional-documents",
        ):
            for path in (f"/{prefix}", f"/{prefix}/technical.txt"):
                with self.subTest(path=path):
                    self.assertRegex(path, block.group(1))
        for path in ("/profissional/instrutor/verificacao", "/privacidade", "/api/v1/"):
            self.assertIsNone(re.search(block.group(1), path))
        self.assertLess(block.start(), config.index("location / {"))

    def test_scanner_has_egress_without_host_port_or_document_mount(self):
        compose = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
        scanner = compose.split("  clamav:\n", 1)[1].split("  backend:\n", 1)[0]
        self.assertIn("networks: [private, public]", scanner)
        self.assertNotIn("ports:", scanner)
        self.assertNotIn("demo_private_documents", scanner)

    def test_document_volume_is_not_mounted_into_public_services(self):
        compose = (ROOT / "compose.production.yaml").read_text(encoding="utf-8")
        public_services = compose.split("  frontend:\n", 1)[1].split("\nvolumes:\n", 1)[
            0
        ]
        self.assertNotIn("demo_private_documents", public_services)


if __name__ == "__main__":
    unittest.main()
