from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .availability_interest import (
    InterestValidationError,
    active_interest_policy,
    create_availability_interest,
    withdraw_availability_interest,
)


class InterestSerializer(serializers.Serializer):
    city = serializers.CharField(max_length=120, trim_whitespace=True)
    uf = serializers.CharField(max_length=2)
    name = serializers.CharField(max_length=120, trim_whitespace=True)
    phone = serializers.CharField(max_length=24)
    birth_date = serializers.DateField(write_only=True)
    privacy_notice_version = serializers.CharField(max_length=40)
    consent_version = serializers.CharField(max_length=40)
    consent_granted = serializers.BooleanField()
    idempotency_key = serializers.UUIDField()


class WithdrawalSerializer(serializers.Serializer):
    reference = serializers.UUIDField()
    phone = serializers.CharField(max_length=24)


class AvailabilityInterestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "availability_interest"

    def get(self, request):
        policy = active_interest_policy()
        if not policy:
            return Response({"enabled": False})
        return Response(
            {
                "enabled": True,
                "retention_days": policy.retention_days,
                "privacy_notice_version": policy.privacy_notice.version,
                "consent_version": policy.consent_version,
                "consent_text": policy.consent_text,
            }
        )

    def post(self, request):
        if not active_interest_policy():
            return Response(
                {"detail": "Cadastro de interesse indisponível."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        serializer = InterestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item, created = create_availability_interest(
                data=serializer.validated_data,
                request_id=getattr(request, "request_id", None),
            )
        except InterestValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, DjangoValidationError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(
            {"id": str(item.pk), "expires_at": item.expires_at},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class AvailabilityInterestWithdrawalView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "availability_interest"

    def post(self, request):
        serializer = WithdrawalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        withdraw_availability_interest(
            reference=serializer.validated_data["reference"],
            phone=serializer.validated_data["phone"],
            request_id=getattr(request, "request_id", None),
        )
        return Response(
            {"detail": "Se o protocolo e telefone corresponderem, o pedido foi excluído."}
        )
