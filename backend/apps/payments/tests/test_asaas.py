import io
import json
from urllib.error import HTTPError

import pytest

from apps.payments.asaas import AsaasSandboxError, AsaasSandboxProvider

SANDBOX_KEY = "$aact_hmlg_test-only-not-a-real-key"
WEBHOOK_TOKEN = "test-only-webhook-token-with-32-chars"


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


def provider_with_response(data, calls):
    def transport(req, timeout):
        calls.append((req, timeout))
        return Response(json.dumps(data).encode())

    return AsaasSandboxProvider(
        api_key=SANDBOX_KEY, webhook_token=WEBHOOK_TOKEN, transport=transport
    )


def test_provider_rejects_production_key_and_short_webhook_token():
    with pytest.raises(ValueError, match="ASAAS_SANDBOX_KEY_REQUIRED"):
        AsaasSandboxProvider(api_key="$aact_prod_secret", webhook_token=WEBHOOK_TOKEN)
    with pytest.raises(ValueError, match="ASAAS_WEBHOOK_TOKEN_REQUIRED"):
        AsaasSandboxProvider(api_key=SANDBOX_KEY, webhook_token="short")


def test_customer_creation_uses_sandbox_and_external_reference():
    calls = []
    provider = provider_with_response({"id": "cus_test"}, calls)
    assert provider.create_customer(
        reference="local-1", name="Teste", email="test@example.com"
    ) == ("cus_test")
    req, timeout = calls[0]
    assert req.full_url == "https://api-sandbox.asaas.com/v3/customers"
    assert req.get_method() == "POST" and timeout == 15
    assert req.get_header("Access_token") == SANDBOX_KEY
    assert json.loads(req.data) == {
        "externalReference": "local-1",
        "name": "Teste",
        "email": "test@example.com",
    }


def test_customer_lookup_avoids_duplicates_and_fails_on_ambiguity():
    calls = []
    provider = provider_with_response({"data": [{"id": "cus_existing"}]}, calls)
    assert provider.find_customer_by_reference("local 1") == "cus_existing"
    assert calls[0][0].full_url.endswith("/customers?externalReference=local+1&limit=2")
    missing = provider_with_response({"data": []}, [])
    assert missing.find_customer_by_reference("local-1") is None
    duplicate = provider_with_response({"data": [{"id": "cus_a"}, {"id": "cus_b"}]}, [])
    with pytest.raises(AsaasSandboxError, match="ASAAS_CUSTOMER_LOOKUP_AMBIGUOUS"):
        duplicate.find_customer_by_reference("local-1")


def test_pro_checkout_is_hosted_card_recurring_and_does_not_claim_payment():
    calls = []
    provider = provider_with_response(
        {"link": "https://sandbox.asaas.com/checkoutSession/show/test-id"}, calls
    )
    link = provider.create_pro_checkout(
        reference="local-subscription-1",
        customer_id="cus_test",
        amount_minor=1290,
        callback_url="https://example.com/instrutor/plano",
        next_due_date="2026-09-30",
    )
    assert link.startswith("https://sandbox.asaas.com/")
    req, _ = calls[0]
    assert req.full_url == "https://api-sandbox.asaas.com/v3/checkouts"
    payload = json.loads(req.data)
    assert payload["billingTypes"] == ["CREDIT_CARD"]
    assert payload["chargeTypes"] == ["RECURRENT"]
    assert payload["items"][0]["value"] == 12.9
    assert payload["customer"] == "cus_test"
    assert "creditCard" not in payload and "creditCardHolderInfo" not in payload


def test_checkout_rejects_non_sandbox_link_and_insecure_callback():
    provider = provider_with_response({"link": "https://asaas.com/checkoutSession/show/id"}, [])
    with pytest.raises(AsaasSandboxError, match="ASAAS_SANDBOX_CHECKOUT_LINK_MISSING"):
        provider.create_pro_checkout(
            reference="sub-1",
            customer_id="cus_test",
            amount_minor=1000,
            callback_url="https://example.com/instrutor/plano",
            next_due_date="2026-09-30",
        )
    with pytest.raises(ValueError, match="ASAAS_CALLBACK_HTTPS_REQUIRED"):
        provider.create_pro_checkout(
            reference="sub-1",
            customer_id="cus_test",
            amount_minor=1000,
            callback_url="http://example.com/instrutor/plano",
            next_due_date="2026-09-30",
        )


def test_subscription_operations_encode_identifier_and_use_sandbox():
    calls = []
    provider = provider_with_response({"id": "sub_test"}, calls)
    assert provider.get_subscription("sub_1?x=y")["id"] == "sub_test"
    provider.list_subscription_payments("sub_1")
    provider.cancel_subscription("sub_1")
    assert calls[0][0].full_url.endswith("/subscriptions/sub_1%3Fx%3Dy")
    assert calls[1][0].full_url.endswith("/subscriptions/sub_1/payments")
    assert calls[2][0].get_method() == "DELETE"


def test_webhook_token_is_required_and_provider_errors_are_sanitized():
    def transport(req, timeout):
        raise HTTPError(req.full_url, 401, "sensitive gateway response", {}, None)

    provider = AsaasSandboxProvider(
        api_key=SANDBOX_KEY, webhook_token=WEBHOOK_TOKEN, transport=transport
    )
    assert provider.verify_webhook(WEBHOOK_TOKEN)
    assert not provider.verify_webhook("wrong")
    assert not provider.verify_webhook("")
    with pytest.raises(AsaasSandboxError) as exc:
        provider.get_subscription("sub_test")
    assert "sensitive" not in str(exc.value)
