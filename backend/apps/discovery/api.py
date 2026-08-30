from uuid import uuid4

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.people.models import Person, RoleAssignment

from .geocoding import DemoGeocodingProvider, LocationNotFound
from .models import InstructorProfile, InstructorServiceArea
from .selectors import published_instructor_counts_by_uf, search_demo_instructors
from .services import grant_service_location_authorization, submit_profile


class SearchParameters(serializers.Serializer):
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)
    radius_km = serializers.ChoiceField(choices=[5, 10, 20, 50])
    category = serializers.ChoiceField(choices=["B"])
    transmission = serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"], required=False)
    vehicle_available = serializers.BooleanField(required=False)


class InstructorResult(serializers.Serializer):
    id = serializers.UUIDField()
    display_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    distance_km = serializers.FloatField()
    categories = serializers.ListField(child=serializers.CharField())
    transmission = serializers.CharField()
    vehicle_available = serializers.BooleanField()
    demo_rating = serializers.FloatField()
    demo_price = serializers.FloatField()
    availability_summary = serializers.CharField()
    demo = serializers.BooleanField()


class InstructorSearchResponse(serializers.Serializer):
    count = serializers.IntegerField()
    results = InstructorResult(many=True)


class InstructorStateSummary(serializers.Serializer):
    uf = serializers.CharField()
    count = serializers.IntegerField()
    search_location = serializers.CharField()


class GeocodingResponse(serializers.Serializer):
    results = serializers.ListField(child=serializers.DictField())
    provider = serializers.CharField()


class InstructorSearchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name, str, required=name in {"latitude", "longitude", "radius_km", "category"}
            )
            for name in [
                "latitude",
                "longitude",
                "radius_km",
                "category",
                "transmission",
                "vehicle_available",
            ]
        ],
        responses=InstructorSearchResponse,
    )
    def get(self, request):
        params = SearchParameters(data=request.query_params.dict())
        params.is_valid(raise_exception=True)
        rows = search_demo_instructors(**params.validated_data)
        results = [
            {
                "id": str(row.id),
                "display_name": row.display_name,
                "latitude": round(row.service_area.public_service_location.y, 5),
                "longitude": round(row.service_area.public_service_location.x, 5),
                "distance_km": round(row.distance.km, 1),
                "categories": row.categories,
                "transmission": row.transmission_options[0],
                "vehicle_available": row.vehicle_available,
                "demo_rating": float(row.demo_rating),
                "demo_price": float(row.demo_price),
                "availability_summary": row.availability_summary,
                "demo": True,
            }
            for row in rows
        ]
        return Response({"count": len(results), "results": results})


class InstructorStateSummaryView(APIView):
    permission_classes = [AllowAny]
    search_locations = {
        "RS": "Porto Alegre",
        "SC": "Florianópolis",
        "SP": "São Paulo",
        "RJ": "Rio de Janeiro",
        "ES": "Vitória",
    }

    @extend_schema(responses=InstructorStateSummary(many=True))
    def get(self, request):
        results = [
            {
                "uf": row["service_area__uf"],
                "count": row["total"],
                "search_location": self.search_locations[row["service_area__uf"]],
            }
            for row in published_instructor_counts_by_uf()
            if row["service_area__uf"] in self.search_locations
        ]
        return Response({"states": results})


class GeocodingView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter("q", str, required=True)], responses=GeocodingResponse
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"code": "invalid_query", "detail": "Informe cidade, bairro ou CEP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            results = DemoGeocodingProvider().geocode(query)
        except LocationNotFound:
            return Response(
                {
                    "code": "location_not_found",
                    "detail": "Local não encontrado no catálogo demonstrativo.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"results": [result.__dict__ for result in results], "provider": "DEMO_LOCAL"}
        )


class DemoOnboardingInput(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    prerequisite_accepted = serializers.BooleanField()
    display_name = serializers.CharField(max_length=80)
    city = serializers.CharField(max_length=100)
    uf = serializers.ChoiceField(choices=["RS", "SC", "SP", "RJ", "ES"])
    category = serializers.ChoiceField(choices=["B"])
    vehicle_available = serializers.BooleanField()
    vehicle_make = serializers.CharField(max_length=60, required=False, allow_blank=True)
    vehicle_model = serializers.CharField(max_length=60, required=False, allow_blank=True)
    vehicle_year = serializers.IntegerField(min_value=1990, max_value=2030, required=False)
    vehicle_transmission = serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"], required=False)
    transmissions = serializers.ListField(
        child=serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"]), min_length=1
    )
    radius_km = serializers.ChoiceField(choices=[5, 10, 20, 50])
    latitude = serializers.FloatField(min_value=-34, max_value=-19)
    longitude = serializers.FloatField(min_value=-52, max_value=-39)
    location_authorized = serializers.BooleanField()
    credential_type = serializers.ChoiceField(choices=["CREDENCIAL_DEMO"])
    credential_uf = serializers.ChoiceField(choices=["RS", "SC", "SP", "RJ", "ES"])
    credential_validity = serializers.CharField(max_length=30)
    synthetic_data_confirmed = serializers.BooleanField()

    def validate(self, attrs):
        if not settings.SYNTHETIC_MARKETPLACE_ENABLED:
            raise serializers.ValidationError("Synthetic marketplace is disabled")
        if not attrs["email"].endswith("@example.invalid"):
            raise serializers.ValidationError(
                {"email": "Use uma identidade sintética terminada em @example.invalid."}
            )
        if not attrs["prerequisite_accepted"]:
            raise serializers.ValidationError(
                {"prerequisite_accepted": "O aceite do pré-requisito é obrigatório."}
            )
        if attrs["vehicle_available"] and not all(
            attrs.get(field)
            for field in ("vehicle_make", "vehicle_model", "vehicle_year", "vehicle_transmission")
        ):
            raise serializers.ValidationError(
                {"vehicle_available": "Preencha os dados sintéticos do veículo."}
            )
        if not attrs["location_authorized"]:
            raise serializers.ValidationError(
                {
                    "location_authorized": (
                        "A autorização explícita é obrigatória para esta demonstração."
                    )
                }
            )
        if not attrs["synthetic_data_confirmed"]:
            raise serializers.ValidationError(
                {"synthetic_data_confirmed": "Confirme que todos os dados são sintéticos."}
            )
        if attrs["credential_uf"] != attrs["uf"]:
            raise serializers.ValidationError(
                {"credential_uf": "Na DEMO, a UF da credencial deve coincidir com a área."}
            )
        return attrs


class DemoInstructorOnboardingView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        serializer = DemoOnboardingInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        token = uuid4().hex
        account = Account.objects.create_user(
            username=f"instructor_{token}",
            email=data["email"].lower(),
            password=data["password"],
        )
        person = Person.objects.create(account=account)
        RoleAssignment.objects.create(
            person=person,
            role="INSTRUCTOR",
            granted_by=account,
            grant_reason="SYNTHETIC_DEMO_ONBOARDING",
        )
        clean_name = data["display_name"].strip()
        if not clean_name.lower().endswith(" demo"):
            clean_name += " Demo"
        profile = InstructorProfile.objects.create(
            person=person,
            display_name=clean_name,
            bio="Perfil criado exclusivamente no onboarding sintético CODEX 02E.",
            categories=[data["category"]],
            transmission_options=list(dict.fromkeys(data["transmissions"])),
            vehicle_available=data["vehicle_available"],
            service_radius_km=data["radius_km"],
            is_demo=True,
        )
        from apps.marketplace.models import (
            DataMode,
            InstructorPrerequisiteAcceptance,
            InstructorVehicle,
        )

        InstructorPrerequisiteAcceptance.objects.create(
            instructor=profile,
            policy_version="M1-SYNTHETIC-PREREQUISITE-1",
            data_mode=DataMode.SYNTHETIC,
        )
        if data["vehicle_available"]:
            InstructorVehicle.objects.create(
                instructor=profile,
                category=data["category"],
                make=data["vehicle_make"],
                model=data["vehicle_model"],
                year=data["vehicle_year"],
                transmission=data["vehicle_transmission"],
                data_mode=DataMode.SYNTHETIC,
            )
        area = InstructorServiceArea.objects.create(
            profile=profile,
            city=data["city"],
            uf=data["uf"],
            public_service_location=Point(data["longitude"], data["latitude"], srid=4326),
            private_location=None,
            radius_km=data["radius_km"],
            location_authorized=False,
        )
        grant_service_location_authorization(
            actor=account,
            service_area=area,
            purpose="SYNTHETIC_MARKETPLACE_DISCOVERY",
            policy_version="DEMO-ONBOARDING-1",
            reason="DEMO_EXPLICIT_LOCATION_CONSENT",
            request_id=request.headers.get("X-Request-ID"),
        )
        submit_profile(
            actor=account, profile=profile, request_id=request.headers.get("X-Request-ID")
        )
        AuditEvent.objects.create(
            actor=account,
            action="discovery.demo_onboarding_completed",
            target_type="discovery.InstructorProfile",
            target_id=profile.id,
            reason_code="SYNTHETIC_DEMO_ONBOARDING",
            metadata={"credential": "visual_only", "synthetic": True},
        )
        return Response(
            {
                "id": str(profile.id),
                "display_name": profile.display_name,
                "profile_status": "SUBMITTED",
                "email": account.email,
                "message": "Perfil enviado para análise",
                "timeline": [
                    "Cadastro preenchido",
                    "Enviado para análise",
                    "Verificação",
                    "Aprovação",
                    "Publicação",
                ],
            },
            status=status.HTTP_201_CREATED,
        )
