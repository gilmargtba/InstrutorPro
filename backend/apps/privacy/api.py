from django.db import transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent

from .models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice, PrivacyRequest
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


class LegalDocumentView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, audience):
        normalized = audience.upper()
        if normalized not in LegalDocument.Audience.values:
            return Response(
                {"code": "not_found", "detail": "Documento não encontrado."}, status=404
            )
        document = LegalDocument.objects.filter(
            document_type=LegalDocument.Type.TERMS,
            audience=normalized,
            is_active=True,
            effective_at__lte=timezone.now(),
        ).first()
        if not document:
            return Response(
                {"code": "not_found", "detail": "Documento não encontrado."}, status=404
            )
        return Response(
            {
                "title": document.title,
                "audience": document.audience,
                "version": document.version,
                "effective_at": document.effective_at,
                "content": document.content,
                "content_sha256": document.content_sha256,
                "contact": "focusgtba@gmail.com",
            }
        )


class LegalAcceptanceSerializer(serializers.Serializer):
    audience = serializers.ChoiceField(choices=LegalDocument.Audience.choices)
    accept_terms = serializers.BooleanField()
    acknowledge_privacy = serializers.BooleanField()

    def validate(self, attrs):
        if not attrs["accept_terms"] or not attrs["acknowledge_privacy"]:
            raise serializers.ValidationError(
                "É necessário aceitar os Termos e confirmar a ciência da Política de Privacidade."
            )
        return attrs


class LegalAcceptanceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = LegalAcceptanceRecord.objects.filter(account=request.user).select_related(
            "terms_document", "privacy_notice"
        )
        return Response(
            [
                {
                    "id": row.id,
                    "audience": row.terms_document.audience,
                    "terms_version": row.terms_document.version,
                    "terms_sha256": row.terms_document.content_sha256,
                    "privacy_version": row.privacy_notice.version,
                    "accepted_at": row.accepted_at,
                }
                for row in rows
            ]
        )

    @transaction.atomic
    def post(self, request):
        serializer = LegalAcceptanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        terms = LegalDocument.objects.filter(
            document_type=LegalDocument.Type.TERMS,
            audience=serializer.validated_data["audience"],
            is_active=True,
            effective_at__lte=timezone.now(),
        ).first()
        privacy = PrivacyNotice.objects.filter(
            is_current=True, published_at__lte=timezone.now()
        ).first()
        if not terms or not privacy:
            return Response(
                {
                    "code": "legal_documents_unavailable",
                    "detail": "Documentos vigentes indisponíveis.",
                },
                status=status.HTTP_409_CONFLICT,
            )
        row, created = LegalAcceptanceRecord.objects.get_or_create(
            account=request.user,
            terms_document=terms,
            privacy_notice=privacy,
            defaults={"request_id": getattr(request, "request_id", None)},
        )
        if created:
            AuditEvent.objects.create(
                actor=request.user,
                action="privacy.legal_terms.accepted",
                target_type="privacy.LegalAcceptanceRecord",
                target_id=row.id,
                request_id=getattr(request, "request_id", None),
                metadata={
                    "audience": terms.audience,
                    "terms_version": terms.version,
                    "terms_sha256": terms.content_sha256,
                    "privacy_version": privacy.version,
                },
            )
        return Response(
            {
                "id": row.id,
                "terms_version": terms.version,
                "privacy_version": privacy.version,
                "accepted_at": row.accepted_at,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
