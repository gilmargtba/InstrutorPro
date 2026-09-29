"""Asaas sandbox transport for the future PRO subscription flow.

This module is intentionally not wired to public checkout or production billing.
"""

import hmac
import json
from decimal import Decimal
from urllib import error, parse, request


class AsaasSandboxError(Exception):
    """A sanitized integration error; provider responses may contain personal data."""


class AsaasSandboxProvider:
    code = "ASAAS"
    base_url = "https://api-sandbox.asaas.com/v3"

    def __init__(self, *, api_key, webhook_token, transport=None):
        if not api_key.startswith("$aact_hmlg_"):
            raise ValueError("ASAAS_SANDBOX_KEY_REQUIRED")
        if len(webhook_token) < 32:
            raise ValueError("ASAAS_WEBHOOK_TOKEN_REQUIRED")
        self._api_key = api_key
        self._webhook_token = webhook_token
        self._transport = transport or request.urlopen

    def _request(self, method, path, payload=None):
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            method=method,
            headers={
                "access_token": self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "InstrutorProCNH/1.0 (sandbox)",
            },
        )
        try:
            with self._transport(req, timeout=15) as response:
                result = json.load(response)
        except (error.HTTPError, error.URLError, TimeoutError, ValueError):
            raise AsaasSandboxError("ASAAS_SANDBOX_REQUEST_FAILED") from None
        if not isinstance(result, dict):
            raise AsaasSandboxError("ASAAS_SANDBOX_INVALID_RESPONSE")
        return result

    def create_customer(self, *, reference, name, email):
        if not reference or not name or not email:
            raise ValueError("ASAAS_CUSTOMER_FIELDS_REQUIRED")
        data = self._request(
            "POST",
            "/customers",
            {"externalReference": reference, "name": name, "email": email},
        )
        customer_id = data.get("id")
        if not isinstance(customer_id, str) or not customer_id.startswith("cus_"):
            raise AsaasSandboxError("ASAAS_CUSTOMER_ID_MISSING")
        return customer_id

    def find_customer_by_reference(self, reference):
        if not reference:
            raise ValueError("ASAAS_CUSTOMER_REFERENCE_REQUIRED")
        query = parse.urlencode({"externalReference": reference, "limit": 2})
        data = self._request("GET", f"/customers?{query}")
        matches = data.get("data")
        if not isinstance(matches, list) or len(matches) > 1:
            raise AsaasSandboxError("ASAAS_CUSTOMER_LOOKUP_AMBIGUOUS")
        if not matches:
            return None
        customer_id = matches[0].get("id")
        if not isinstance(customer_id, str) or not customer_id.startswith("cus_"):
            raise AsaasSandboxError("ASAAS_CUSTOMER_ID_MISSING")
        return customer_id

    def create_pro_checkout(
        self, *, reference, customer_id, amount_minor, callback_url, next_due_date
    ):
        """Create a hosted monthly credit-card checkout, not a paid entitlement."""
        if not customer_id.startswith("cus_") or amount_minor <= 0:
            raise ValueError("ASAAS_CHECKOUT_ARGUMENT_INVALID")
        if not callback_url.startswith("https://"):
            raise ValueError("ASAAS_CALLBACK_HTTPS_REQUIRED")
        if not reference or not next_due_date:
            raise ValueError("ASAAS_CHECKOUT_ARGUMENT_INVALID")
        amount = Decimal(amount_minor) / Decimal(100)
        data = self._request(
            "POST",
            "/checkouts",
            {
                "billingTypes": ["CREDIT_CARD"],
                "chargeTypes": ["RECURRENT"],
                "externalReference": reference,
                "customer": customer_id,
                "minutesToExpire": 60,
                "items": [{"name": "InstrutorProCNH PRO", "quantity": 1, "value": float(amount)}],
                "subscription": {"cycle": "MONTHLY", "nextDueDate": next_due_date},
                "callback": {
                    "successUrl": callback_url,
                    "cancelUrl": callback_url,
                    "expiredUrl": callback_url,
                },
            },
        )
        link = data.get("link")
        if not isinstance(link, str) or not link.startswith(
            "https://sandbox.asaas.com/checkoutSession/"
        ):
            raise AsaasSandboxError("ASAAS_SANDBOX_CHECKOUT_LINK_MISSING")
        return link

    def get_subscription(self, subscription_id):
        return self._request("GET", f"/subscriptions/{parse.quote(subscription_id, safe='')}")

    def list_subscription_payments(self, subscription_id):
        return self._request(
            "GET", f"/subscriptions/{parse.quote(subscription_id, safe='')}/payments"
        )

    def cancel_subscription(self, subscription_id):
        return self._request("DELETE", f"/subscriptions/{parse.quote(subscription_id, safe='')}")

    def verify_webhook(self, token):
        return bool(token) and hmac.compare_digest(token, self._webhook_token)
