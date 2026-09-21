from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import configured_provider, process_webhook


class PaymentWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, provider):
        try:
            adapter = configured_provider()
            if provider != adapter.code:
                raise LookupError
            receipt, processed = process_webhook(
                provider=adapter,
                signature=request.headers.get("X-Payment-Signature", ""),
                raw_body=request.body,
            )
        except (LookupError, PermissionError):
            return Response({"code": "WEBHOOK_REJECTED"}, status=status.HTTP_401_UNAUTHORIZED)
        except (KeyError, TypeError, ValueError):
            return Response({"code": "INVALID_WEBHOOK"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"event_id": receipt.provider_event_id, "processed": processed},
            status=status.HTTP_200_OK,
        )
