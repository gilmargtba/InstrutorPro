from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PrivacyNotice, PrivacyRequest
from .services import create_privacy_request


class PrivacyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyRequest
        fields = ("id", "request_type", "status", "details", "requested_at", "completed_at")
        read_only_fields = ("id", "status", "requested_at", "completed_at")


class PrivacyRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = PrivacyRequest.objects.filter(requester=request.user)
        return Response(PrivacyRequestSerializer(rows, many=True).data)

    def post(self, request):
        serializer = PrivacyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        row = create_privacy_request(
            requester=request.user,
            request_type=serializer.validated_data["request_type"],
            details=serializer.validated_data.get("details", ""),
            request_id=getattr(request, "request_id", None),
        )
        return Response(PrivacyRequestSerializer(row).data, status=status.HTTP_201_CREATED)


class PrivacyNoticeView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        notice = PrivacyNotice.objects.filter(is_current=True).first()
        return Response(
            {
                "product": "InstrutorProCNH",
                "title": "Política de Privacidade e Proteção de Dados",
                "version": notice.version if notice else "2026-09-16",
                "last_updated": (
                    notice.published_at.date().isoformat()
                    if notice and notice.published_at
                    else "2026-09-16"
                ),
                "controller_cnpj": "10.280.826/0001-05",
                "privacy_contact": "focusgtba@gmail.com",
            }
        )
