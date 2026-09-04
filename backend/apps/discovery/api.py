from uuid import uuid4

from django.conf import settings
from django.contrib.auth import login
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.people.models import Person, RoleAssignment

from .geocoding import LocationNotFound, ProviderUnavailable, get_geocoding_provider
from .models import InstructorProfile, InstructorServiceArea
from .selectors import (
    published_instructor_counts_by_uf,
    published_instructor_profiles,
    search_published_instructors,
)
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
    profile_photo_url = serializers.CharField(allow_null=True)
    verified_claims = serializers.ListField(child=serializers.CharField())
    city = serializers.CharField()
    uf = serializers.CharField()


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
        rows = search_published_instructors(**params.validated_data)
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
                "demo": row.is_demo,
                "city": row.service_area.city,
                "uf": row.service_area.uf,
                "profile_photo_url": self._photo_url(row),
                "verified_claims": self._verified_claims(row),
            }
            for row in rows
        ]
        return Response({"count": len(results), "results": results})

    @staticmethod
    def _photo_url(row):
        photo = (
            row.profile_photos.filter(status="APPROVED", publication_authorized_at__isnull=False)
            .order_by("-uploaded_at")
            .first()
        )
        return f"/api/v1/instructors/profile-photos/{photo.id}/" if photo else None

    @staticmethod
    def _verified_claims(row):
        from apps.marketplace.models import DocumentRequirement, InstructorDocument

        claims = []
        approved = row.documents.filter(
            status=InstructorDocument.Status.APPROVED,
            scan_status=InstructorDocument.ScanStatus.CLEAN,
        ).filter(Q(valid_until__isnull=True) | Q(valid_until__gte=timezone.localdate()))
        approved = approved.select_related("requirement")
        types = {document.requirement.document_type for document in approved}
        if DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION in types:
            claims.append("CREDENTIAL_VERIFIED")
        if DocumentRequirement.DocumentType.INSTRUCTOR_COURSE in types:
            claims.append("COURSE_VERIFIED")
        if DocumentRequirement.DocumentType.VEHICLE_EVIDENCE in types:
            claims.append("VEHICLE_VERIFIED")
        return claims


class PublicProfilePhotoView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, pk):
        from apps.marketplace.models import ProfilePhoto

        photo = get_object_or_404(
            ProfilePhoto,
            pk=pk,
            status=ProfilePhoto.Status.APPROVED,
            publication_authorized_at__isnull=False,
            instructor__publication_status="APPROVED",
            data_mode="SYNTHETIC",
        )
        response = FileResponse(photo.file.open("rb"), content_type=photo.mime_type)
        response["Cache-Control"] = "public, max-age=300"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class PublicInstructorProfileView(InstructorSearchView):
    authentication_classes = []

    def get(self, request, pk):
        row = get_object_or_404(
            published_instructor_profiles().select_related("service_area"), pk=pk
        )
        return Response(
            {
                "id": row.id,
                "display_name": row.display_name,
                "bio": row.bio,
                "categories": row.categories,
                "transmission_options": row.transmission_options,
                "vehicle_available": row.vehicle_available,
                "service_area": {
                    "city": row.service_area.city,
                    "uf": row.service_area.uf,
                    "radius_km": row.service_area.radius_km,
                },
                "availability_summary": row.availability_summary,
                "profile_photo_url": self._photo_url(row),
                "verified_claims": self._verified_claims(row),
                "synthetic": row.is_demo,
            }
        )


class InstructorStateSummaryView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=InstructorStateSummary(many=True))
    def get(self, request):
        results = [
            {
                "uf": row["service_area__uf"],
                "count": row["total"],
                "search_location": row["search_location"],
            }
            for row in published_instructor_counts_by_uf()
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
            provider = get_geocoding_provider()
            results = provider.geocode(
                query, limit=min(int(request.query_params.get("limit", 5)), 10)
            )
        except LocationNotFound:
            return Response(
                {
                    "code": "location_not_found",
                    "detail": "Localidade brasileira não encontrada.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except (ProviderUnavailable, ValueError):
            return Response(
                {
                    "code": "provider_unavailable",
                    "detail": "A busca de localidades está temporariamente indisponível.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response(
            {"results": [result.public_dict() for result in results], "provider": provider.code}
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
    credential_identifier = serializers.CharField(max_length=80, required=False, allow_blank=True)
    credential_issued_at = serializers.DateField(required=False, allow_null=True)
    credential_valid_until = serializers.DateField(required=False, allow_null=True)
    synthetic_data_confirmed = serializers.BooleanField()
    photo_publication_authorized = serializers.BooleanField(default=False)
    photo_notice_version = serializers.CharField(max_length=80, required=False, allow_blank=True)
    profile_photo = serializers.FileField(required=False, write_only=True)
    credential_file = serializers.FileField(required=False, write_only=True)
    course_file = serializers.FileField(required=False, write_only=True)
    vehicle_file = serializers.FileField(required=False, write_only=True)

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
        if attrs.get("profile_photo") and not attrs["photo_publication_authorized"]:
            raise serializers.ValidationError(
                {"photo_publication_authorized": "A autorização separada da foto é obrigatória."}
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
        from apps.marketplace.documents import (
            upload_synthetic_document,
            upload_synthetic_profile_photo,
        )
        from apps.marketplace.models import (
            DataMode,
            DocumentRequirement,
            InstructorPrerequisiteAcceptance,
            InstructorVehicle,
        )

        InstructorPrerequisiteAcceptance.objects.create(
            instructor=profile,
            policy_version="M1-SYNTHETIC-PREREQUISITE-1",
            data_mode=DataMode.SYNTHETIC,
        )
        vehicle = None
        if data["vehicle_available"]:
            vehicle = InstructorVehicle.objects.create(
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
        uploads = (
            ("credential_file", DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION, None),
            ("course_file", DocumentRequirement.DocumentType.INSTRUCTOR_COURSE, None),
            ("vehicle_file", DocumentRequirement.DocumentType.VEHICLE_EVIDENCE, vehicle),
        )
        document_ids = []
        for field, document_type, related_vehicle in uploads:
            upload = data.get(field)
            if not upload:
                continue
            requirement, _ = DocumentRequirement.objects.get_or_create(
                uf=data["uf"],
                category=data["category"],
                provider_type="INSTRUCTOR",
                rule_version="M1-SYNTHETIC-DOSSIER-1",
                document_type=document_type,
                defaults={
                    "label": DocumentRequirement.DocumentType(document_type).label,
                    "required": False,
                    "requires_validity": False,
                    "active_from": timezone.localdate(),
                },
            )
            document = upload_synthetic_document(
                actor=account,
                instructor=profile,
                requirement=requirement,
                upload=upload,
                vehicle=related_vehicle,
                credential_uf=data["credential_uf"] if field == "credential_file" else data["uf"],
                private_identifier=(
                    data.get("credential_identifier", "") if field == "credential_file" else ""
                ),
                issued_at=data.get("credential_issued_at") if field == "credential_file" else None,
                valid_until=(
                    data.get("credential_valid_until") if field == "credential_file" else None
                ),
            )
            document_ids.append(str(document.id))
        photo_id = None
        if data.get("profile_photo"):
            photo = upload_synthetic_profile_photo(
                actor=account,
                instructor=profile,
                upload=data["profile_photo"],
                publication_authorized=data["photo_publication_authorized"],
                notice_version=data.get("photo_notice_version", ""),
            )
            photo_id = str(photo.id)
        submit_profile(
            actor=account, profile=profile, request_id=request.headers.get("X-Request-ID")
        )
        AuditEvent.objects.create(
            actor=account,
            action="discovery.demo_onboarding_completed",
            target_type="discovery.InstructorProfile",
            target_id=profile.id,
            reason_code="SYNTHETIC_DEMO_ONBOARDING",
            metadata={
                "credential": "synthetic_fixture",
                "synthetic": True,
                "document_ids": document_ids,
                "profile_photo_id": photo_id,
            },
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


class OnboardingDraftInput(serializers.Serializer):
    step = serializers.IntegerField(min_value=1, max_value=7)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, min_length=10, required=False)
    prerequisite_accepted = serializers.BooleanField(required=False)
    display_name = serializers.CharField(max_length=80, required=False)
    category = serializers.ChoiceField(choices=["B"], required=False)
    transmissions = serializers.ListField(
        child=serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"]), required=False
    )
    vehicle_available = serializers.BooleanField(required=False)
    vehicle_make = serializers.CharField(max_length=60, required=False, allow_blank=True)
    vehicle_model = serializers.CharField(max_length=60, required=False, allow_blank=True)
    vehicle_year = serializers.IntegerField(min_value=1990, max_value=2030, required=False)
    vehicle_transmission = serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"], required=False)
    city = serializers.CharField(max_length=100, required=False)
    uf = serializers.ChoiceField(choices=["RS", "SC", "SP", "RJ", "ES"], required=False)
    region = serializers.CharField(max_length=100, required=False, allow_blank=True)
    radius_km = serializers.ChoiceField(choices=[5, 10, 20, 50], required=False)
    latitude = serializers.FloatField(min_value=-34, max_value=-19, required=False)
    longitude = serializers.FloatField(min_value=-52, max_value=-39, required=False)
    location_authorized = serializers.BooleanField(required=False)
    credential_identifier = serializers.CharField(max_length=80, required=False, allow_blank=True)
    credential_issued_at = serializers.DateField(required=False, allow_null=True)
    credential_valid_until = serializers.DateField(required=False, allow_null=True)
    photo_publication_authorized = serializers.BooleanField(required=False)
    photo_notice_version = serializers.CharField(max_length=80, required=False, allow_blank=True)
    profile_photo = serializers.FileField(required=False, write_only=True)
    credential_file = serializers.FileField(required=False, write_only=True)
    course_file = serializers.FileField(required=False, write_only=True)
    vehicle_file = serializers.FileField(required=False, write_only=True)


class DemoInstructorOnboardingDraftView(APIView):
    """Persist each onboarding step into existing domain entities in DEV/TEST only."""

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "GET" else [AllowAny()]

    def _profile(self, request):
        person = getattr(request.user, "person", None)
        return getattr(person, "instructor_profile", None) if person else None

    def get(self, request):
        profile = self._profile(request)
        if not profile or not profile.is_demo:
            return Response({"detail": "Cadastro não encontrado."}, status=404)
        return Response(self._payload(profile))

    @transaction.atomic
    def post(self, request):
        if not settings.SYNTHETIC_MARKETPLACE_ENABLED:
            return Response({"detail": "Synthetic marketplace is disabled"}, status=403)
        serializer = OnboardingDraftInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        profile = self._profile(request) if request.user.is_authenticated else None
        if profile is None:
            profile = self._create_identity(request, data)
        self._save_step(request, profile, data)
        return Response(self._payload(profile))

    def _create_identity(self, request, data):
        required = ["email", "password", "display_name", "prerequisite_accepted"]
        if any(not data.get(field) for field in required):
            raise serializers.ValidationError({"detail": "Complete os dados da primeira etapa."})
        email = data["email"].lower()
        if not email.endswith("@example.invalid"):
            raise serializers.ValidationError(
                {"email": "Use identidade DEV/TEST @example.invalid."}
            )
        if Account.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({"email": "Já existe uma conta com este e-mail."})
        account = Account.objects.create_user(
            username=f"instructor_{uuid4().hex}", email=email, password=data["password"]
        )
        person = Person.objects.create(account=account)
        RoleAssignment.objects.create(
            person=person,
            role=RoleAssignment.Role.INSTRUCTOR,
            granted_by=account,
            grant_reason="SYNTHETIC_ONBOARDING_DRAFT",
        )
        profile = InstructorProfile.objects.create(
            person=person,
            display_name=data["display_name"].strip(),
            categories=["B"],
            transmission_options=["MANUAL"],
            vehicle_available=False,
            is_demo=True,
        )
        from apps.marketplace.models import (
            DataMode,
            InstructorOnboardingDraft,
            InstructorPrerequisiteAcceptance,
        )

        InstructorPrerequisiteAcceptance.objects.create(
            instructor=profile,
            policy_version="M1-SYNTHETIC-PREREQUISITE-1",
            data_mode=DataMode.SYNTHETIC,
        )
        InstructorOnboardingDraft.objects.create(instructor=profile, data_mode=DataMode.SYNTHETIC)
        login(request, account, backend="django.contrib.auth.backends.ModelBackend")
        AuditEvent.objects.create(
            actor=account,
            action="discovery.synthetic_onboarding.started",
            target_type="discovery.InstructorProfile",
            target_id=profile.id,
        )
        return profile

    def _save_step(self, request, profile, data):
        from apps.marketplace.documents import (
            upload_synthetic_document,
            upload_synthetic_profile_photo,
        )
        from apps.marketplace.models import DataMode, DocumentRequirement, InstructorVehicle

        draft = profile.onboarding_draft
        step = data["step"]
        if data.get("display_name"):
            profile.display_name = data["display_name"].strip()
        if data.get("category"):
            profile.categories = [data["category"]]
        if data.get("transmissions"):
            profile.transmission_options = list(dict.fromkeys(data["transmissions"]))
        if "vehicle_available" in data:
            profile.vehicle_available = data["vehicle_available"]
        if data.get("radius_km"):
            profile.service_radius_km = data["radius_km"]
        profile.save()
        vehicle = getattr(profile, "vehicle", None)
        if step >= 4 and data.get("vehicle_available"):
            vehicle, _ = InstructorVehicle.objects.update_or_create(
                instructor=profile,
                defaults={
                    "category": data.get("category", "B"),
                    "make": data.get("vehicle_make", ""),
                    "model": data.get("vehicle_model", ""),
                    "year": data.get("vehicle_year", 2000),
                    "transmission": data.get("vehicle_transmission", "MANUAL"),
                    "data_mode": DataMode.SYNTHETIC,
                },
            )
        if step >= 5 and all(
            data.get(field) is not None for field in ("city", "uf", "latitude", "longitude")
        ):
            area, created = InstructorServiceArea.objects.update_or_create(
                profile=profile,
                defaults={
                    "city": data["city"],
                    "uf": data["uf"],
                    "public_service_location": Point(
                        data["longitude"], data["latitude"], srid=4326
                    ),
                    "private_location": None,
                    "radius_km": data.get("radius_km", 10),
                },
            )
            if created and data.get("location_authorized"):
                grant_service_location_authorization(
                    actor=profile.person.account,
                    service_area=area,
                    purpose="SYNTHETIC_MARKETPLACE_DISCOVERY",
                    policy_version="DEMO-ONBOARDING-1",
                    reason="DEMO_EXPLICIT_LOCATION_CONSENT",
                    request_id=request.headers.get("X-Request-ID"),
                )
        if data.get("profile_photo") and not profile.profile_photos.exists():
            upload_synthetic_profile_photo(
                actor=profile.person.account,
                instructor=profile,
                upload=data["profile_photo"],
                publication_authorized=data.get("photo_publication_authorized", False),
                notice_version=data.get("photo_notice_version", ""),
            )
        file_types = {
            "credential_file": DocumentRequirement.DocumentType.INSTRUCTOR_AUTHORIZATION,
            "course_file": DocumentRequirement.DocumentType.INSTRUCTOR_COURSE,
            "vehicle_file": DocumentRequirement.DocumentType.VEHICLE_EVIDENCE,
        }
        for field, document_type in file_types.items():
            upload = data.get(field)
            if not upload:
                continue
            requirement, _ = DocumentRequirement.objects.get_or_create(
                uf=data.get("uf", "RS"),
                category=data.get("category", "B"),
                provider_type="INSTRUCTOR",
                rule_version="M1-SYNTHETIC-DOSSIER-1",
                document_type=document_type,
                defaults={
                    "label": DocumentRequirement.DocumentType(document_type).label,
                    "required": False,
                    "requires_validity": False,
                    "active_from": timezone.localdate(),
                },
            )
            upload_synthetic_document(
                actor=profile.person.account,
                instructor=profile,
                requirement=requirement,
                upload=upload,
                vehicle=vehicle if field == "vehicle_file" else None,
                credential_uf=data.get("uf", "RS"),
                private_identifier=data.get("credential_identifier", "")
                if field == "credential_file"
                else "",
                issued_at=data.get("credential_issued_at") if field == "credential_file" else None,
                valid_until=data.get("credential_valid_until")
                if field == "credential_file"
                else None,
            )
        draft.current_step = min(step + 1, 7)
        draft.completed_steps = sorted(set(draft.completed_steps + [step]))
        draft.region = data.get("region", draft.region)
        draft.credential_identifier = data.get("credential_identifier", draft.credential_identifier)
        draft.credential_issued_at = data.get("credential_issued_at", draft.credential_issued_at)
        draft.credential_valid_until = data.get(
            "credential_valid_until", draft.credential_valid_until
        )
        draft.save()
        AuditEvent.objects.create(
            actor=profile.person.account,
            action="discovery.synthetic_onboarding.step_saved",
            target_type="discovery.InstructorProfile",
            target_id=profile.id,
            metadata={"step": step},
        )

    @staticmethod
    def _payload(profile):
        draft = profile.onboarding_draft
        area = getattr(profile, "service_area", None)
        vehicle = getattr(profile, "vehicle", None)
        return {
            "id": str(profile.id),
            "current_step": draft.current_step,
            "completed_steps": draft.completed_steps,
            "display_name": profile.display_name,
            "email": profile.person.account.email,
            "categories": profile.categories,
            "transmissions": profile.transmission_options,
            "vehicle_available": profile.vehicle_available,
            "vehicle": (
                {
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "transmission": vehicle.transmission,
                }
                if vehicle
                else None
            ),
            "service_area": (
                {
                    "city": area.city,
                    "uf": area.uf,
                    "radius_km": area.radius_km,
                    "region": draft.region,
                }
                if area
                else None
            ),
            "location_authorized": bool(
                area and area.authorization_history.filter(revoked_at__isnull=True).exists()
            ),
            "photo_present": profile.profile_photos.exists(),
            "document_types": list(
                profile.documents.values_list("requirement__document_type", flat=True)
            ),
            "profile_status": profile.profile_status,
        }


class DemoInstructorOnboardingSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        profile = getattr(getattr(request.user, "person", None), "instructor_profile", None)
        if not profile or not profile.is_demo:
            return Response({"detail": "Cadastro não encontrado."}, status=404)
        if profile.profile_status != InstructorProfile.Status.DRAFT:
            return Response({"detail": "Cadastro já enviado."}, status=409)
        submit_profile(
            actor=request.user, profile=profile, request_id=request.headers.get("X-Request-ID")
        )
        AuditEvent.objects.create(
            actor=request.user,
            action="discovery.synthetic_onboarding.completed",
            target_type="discovery.InstructorProfile",
            target_id=profile.id,
            metadata={"completed_steps": profile.onboarding_draft.completed_steps},
        )
        return Response({"id": str(profile.id), "profile_status": profile.profile_status})
