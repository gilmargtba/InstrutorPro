from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses={200: OpenApiResponse(description="Processo disponível")})
    def get(self, request):
        return Response({"status": "ok"})


class ReadinessView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Dependências essenciais disponíveis"),
            503: OpenApiResponse(description="Banco indisponível"),
        }
    )
    def get(self, request):
        try:
            connections["default"].cursor().execute("SELECT 1")
        except OperationalError:
            return Response({"status": "unavailable", "checks": {"database": "down"}}, status=503)
        return Response({"status": "ok", "checks": {"database": "up"}})
