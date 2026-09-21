import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderPayment:
    payment_id: str
    status: str


@dataclass(frozen=True)
class ProviderWebhook:
    event_id: str
    payment_id: str
    status: str
    amount_minor: int


class PaymentProvider(Protocol):
    code: str

    def create_customer(self, *, reference: str, email: str) -> str: ...
    def create_payment(
        self, *, reference: str, amount_minor: int, idempotency_key: str
    ) -> ProviderPayment: ...
    def get_payment(self, payment_id: str) -> ProviderPayment: ...
    def cancel_payment(self, payment_id: str) -> ProviderPayment: ...
    def refund_payment(self, payment_id: str) -> ProviderPayment: ...
    def verify_webhook(self, *, signature: str, raw_body: bytes) -> bool: ...
    def parse_webhook(self, raw_body: bytes) -> ProviderWebhook: ...


class FakePaymentProvider:
    """Deterministic test adapter. It never performs network or financial operations."""

    code = "fake"

    def __init__(self, webhook_secret="test-webhook-secret"):
        self.webhook_secret = webhook_secret.encode()

    def create_customer(self, *, reference, email):
        return f"cus_{reference}"

    def create_payment(self, *, reference, amount_minor, idempotency_key):
        digest = hashlib.sha256(idempotency_key.encode()).hexdigest()[:24]
        return ProviderPayment(f"pay_{digest}", "PENDING")

    def get_payment(self, payment_id):
        return ProviderPayment(payment_id, "PENDING")

    def cancel_payment(self, payment_id):
        return ProviderPayment(payment_id, "CANCELLED")

    def refund_payment(self, payment_id):
        return ProviderPayment(payment_id, "REFUNDED")

    def sign(self, raw_body):
        return hmac.new(self.webhook_secret, raw_body, hashlib.sha256).hexdigest()

    def verify_webhook(self, *, signature, raw_body):
        return hmac.compare_digest(signature, self.sign(raw_body))

    def parse_webhook(self, raw_body):
        data = json.loads(raw_body)
        return ProviderWebhook(
            event_id=data["event_id"],
            payment_id=data["payment_id"],
            status=data["status"],
            amount_minor=int(data["amount_minor"]),
        )
