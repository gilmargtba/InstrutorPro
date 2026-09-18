from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db.models import Count
from django.http import FileResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile, InstructorServiceArea
from apps.discovery.services import (
    grant_service_location_authorization,
    invalidate_after_owner_sensitive_edit,
)
from apps.people.models import Person, RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice
from apps.territories.models import FederativeUnit

from .capabilities import enabled
from .documents import can_review_document
from .models import (
    DataMode,
    InstructorContactChannel,
    InstructorDocument,
    InstructorOffer,
    InstructorVehicle,
    LessonRequest,
    MarketplaceEvent,
    ProfilePhoto,
    StudentDemand,
    StudentProfile,
)
from .saas import assign_free_plan, current_subscription, has_entitlement, instructor_analytics
from .services import transition_lesson_request


def _synthetic_enabled():
    return settings.SYNTHETIC_MARKETPLACE_ENABLED


class RealRegistrationSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["STUDENT", "INSTRUCTOR"])
    username = serializers.RegexField(r"^[a-zA-Z0-9_.-]+$", max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirmation = serializers.CharField(write_only=True, min_length=10)
    display_name = serializers.CharField(max_length=120)
    birth_date = serializers.DateField()
    city = serializers.CharField(max_length=100, required=False)
    uf = serializers.CharField(min_length=2, max_length=2, required=False)
    terms_version = serializers.CharField(max_length=40)
    privacy_version = serializers.CharField(max_length=40)
    terms_accepted = serializers.BooleanField()
    privacy_acknowledged = serializers.BooleanField()

    def validate(self, attrs):
        role = attrs["role"]
        required_capabilities = ["REAL_ACCOUNT_REGISTRATION", "REAL_PERSONAL_DATA"]
        required_capabilities.append(
            "REAL_STUDENT_USE" if role == "STUDENT" else "REAL_INSTRUCTOR_REGISTRATION"
        )
        if not all(enabled(name) for name in required_capabilities):
            raise PermissionDenied("Cadastro real não está autorizado para esta audiência.")
        if not attrs["terms_accepted"] or not attrs["privacy_acknowledged"]:
            raise serializers.ValidationError("Os aceites obrigatórios devem ser confirmados.")
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "As senhas não coincidem."})
        today = timezone.localdate()
        age = (
            today.year
            - attrs["birth_date"].year
            - ((today.month, today.day) < (attrs["birth_date"].month, attrs["birth_date"].day))
        )
        if age < 18:
            raise serializers.ValidationError(
                {"birth_date": "Cadastro restrito a maiores de 18 anos."}
            )
        if Account.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Já existe uma conta com este e-mail."})
        if Account.objects.filter(username__iexact=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Este usuário já está em uso."})
        if role == "STUDENT" and (not attrs.get("city") or not attrs.get("uf")):
            raise serializers.ValidationError("Cidade e UF são obrigatórias para aluno.")
        audience = (
            LegalDocument.Audience.STUDENT
            if role == "STUDENT"
            else LegalDocument.Audience.INSTRUCTOR
        )
        terms = LegalDocument.objects.filter(
            document_type=LegalDocument.Type.TERMS,
            audience=audience,
            version=attrs["terms_version"],
            is_active=True,
            effective_at__lte=timezone.now(),
        ).first()
        privacy = PrivacyNotice.objects.filter(
            version=attrs["privacy_version"],
            is_current=True,
            published_at__lte=timezone.now(),
        ).first()
        if not terms or not privacy:
            raise serializers.ValidationError("As versões jurídicas informadas não estão vigentes.")
        attrs["terms_document"] = terms
        attrs["privacy_notice"] = privacy
        if role == "STUDENT":
            try:
                attrs["uf_object"] = FederativeUnit.objects.get(code=attrs["uf"].upper())
            except FederativeUnit.DoesNotExist as exc:
                raise serializers.ValidationError({"uf": "UF inválida."}) from exc
        return attrs


class RealRegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @transaction.atomic
    def post(self, request):
        serializer = RealRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        account = Account.objects.create_user(
            username=data["username"], email=data["email"], password=data["password"]
        )
        person = Person.objects.create(account=account, birth_date=data["birth_date"])
        RoleAssignment.objects.create(
            person=person, role=data["role"], grant_reason="CONTROLLED_PILOT_REGISTRATION"
        )
        if data["role"] == "STUDENT":
            StudentProfile.objects.create(
                person=person,
                display_name=data["display_name"],
                city=data["city"],
                uf=data["uf_object"],
                data_mode=DataMode.REAL,
            )
        else:
            InstructorProfile.objects.create(
                person=person,
                display_name=data["display_name"],
                categories=["B"],
                transmission_options=[],
                is_demo=False,
            )
        acceptance = LegalAcceptanceRecord.objects.create(
            account=account,
            terms_document=data["terms_document"],
            privacy_notice=data["privacy_notice"],
            request_id=getattr(request, "request_id", None),
        )
        AuditEvent.objects.create(
            actor=account,
            action="marketplace.real_account.registered",
            target_type="accounts.Account",
            target_id=account.id,
            request_id=getattr(request, "request_id", None),
            metadata={
                "role": data["role"],
                "terms_version": data["terms_document"].version,
                "privacy_version": data["privacy_notice"].version,
                "acceptance_id": str(acceptance.id),
            },
        )
        login(request, account, backend="django.contrib.auth.backends.ModelBackend")
        get_token(request)
        return Response(
            {"id": account.id, "role": data["role"], "acceptance_id": acceptance.id},
            status=status.HTTP_201_CREATED,
        )


class InstructorDocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        document = get_object_or_404(
            InstructorDocument.objects.select_related("instructor__person__account"), pk=pk
        )
        if request.user != document.instructor.person.account and not can_review_document(
            request.user
        ):
            return Response(
                {"code": "forbidden", "detail": "Acesso ao documento negado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        AuditEvent.objects.create(
            actor=request.user,
            action="marketplace.instructor_document.downloaded",
            target_type="InstructorDocument",
            target_id=document.id,
            metadata={"data_mode": document.data_mode, "version": document.version},
        )
        response = FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.original_name,
            content_type=document.mime_type,
        )
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class ProfilePhotoPrivateDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        photo = get_object_or_404(
            ProfilePhoto.objects.select_related("instructor__person__account"), pk=pk
        )
        owner = photo.instructor.person.account
        can_review = request.user.has_perm("marketplace.review_profile_photo")
        if request.user != owner and not can_review:
            return Response(
                {"code": "forbidden", "detail": "Acesso à foto negado."},
                status=status.HTTP_403_FORBIDDEN,
            )
        AuditEvent.objects.create(
            actor=request.user,
            action="marketplace.profile_photo.downloaded",
            target_type="ProfilePhoto",
            target_id=photo.id,
            metadata={"data_mode": photo.data_mode, "status": photo.status},
        )
        response = FileResponse(photo.file.open("rb"), content_type=photo.mime_type)
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response


class StudentRegistrationSerializer(serializers.Serializer):
    username = serializers.RegexField(r"^[a-zA-Z0-9_.-]+$", max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirmation = serializers.CharField(write_only=True, min_length=10)
    display_name = serializers.CharField(max_length=120)
    city = serializers.CharField(max_length=100)
    uf = serializers.CharField(min_length=2, max_length=2)
    intended_category = serializers.CharField(max_length=8, default="B")
    preferred_transmission = serializers.ChoiceField(
        choices=["MANUAL", "AUTOMATIC", "INDIFFERENT"], default="INDIFFERENT"
    )
    synthetic_data_confirmed = serializers.BooleanField()

    def validate(self, attrs):
        if not _synthetic_enabled():
            raise serializers.ValidationError("Synthetic marketplace is disabled")
        if not attrs["synthetic_data_confirmed"] or not attrs["email"].endswith("@example.invalid"):
            raise serializers.ValidationError(
                "Use only explicit synthetic identities ending in @example.invalid"
            )
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "As senhas não coincidem."})
        if Account.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Já existe uma conta com este e-mail."})
        if Account.objects.filter(username__iexact=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Este usuário já está em uso."})
        attrs["uf_object"] = FederativeUnit.objects.get(code=attrs["uf"].upper())
        return attrs

    @transaction.atomic
    def create(self, data):
        uf = data.pop("uf_object")
        data.pop("uf")
        data.pop("synthetic_data_confirmed")
        password = data.pop("password")
        data.pop("password_confirmation")
        username, email = data.pop("username"), data.pop("email")
        account = Account.objects.create_user(username=username, email=email, password=password)
        person = Person.objects.create(account=account)
        RoleAssignment.objects.create(
            person=person,
            role=RoleAssignment.Role.STUDENT,
            grant_reason="M1_SYNTHETIC_REGISTRATION",
        )
        profile = StudentProfile.objects.create(
            person=person, uf=uf, data_mode=DataMode.SYNTHETIC, **data
        )
        AuditEvent.objects.create(
            actor=account,
            action="marketplace.synthetic_student.registered",
            target_type="StudentProfile",
            target_id=profile.id,
            metadata={"data_mode": DataMode.SYNTHETIC},
        )
        return profile


class StudentRegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        login(
            request,
            profile.person.account,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        get_token(request)
        return Response(
            {
                "id": profile.id,
                "display_name": profile.display_name,
                "data_mode": profile.data_mode,
            },
            status=status.HTTP_201_CREATED,
        )


class SessionLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SessionLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SessionLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = SessionLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            account = Account.objects.get(email__iexact=serializer.validated_data["email"])
        except Account.DoesNotExist:
            return Response({"detail": "Credenciais inválidas"}, status=400)
        user = authenticate(
            request,
            username=account.username,
            password=serializer.validated_data["password"],
        )
        if user is None or not user.can_operate:
            return Response({"detail": "Credenciais inválidas"}, status=400)
        login(request, user)
        get_token(request)
        roles = list(
            RoleAssignment.objects.filter(
                person__account=user, revoked_at__isnull=True
            ).values_list("role", flat=True)
        )
        return Response({"account_id": user.id, "roles": roles, "is_staff": user.is_staff})


class SessionMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = list(
            RoleAssignment.objects.filter(
                person__account=request.user, revoked_at__isnull=True
            ).values_list("role", flat=True)
        )
        payload = {"email": request.user.email, "roles": roles, "is_staff": request.user.is_staff}
        person = getattr(request.user, "person", None)
        instructor = getattr(person, "instructor_profile", None) if person else None
        student = getattr(person, "student_profile", None) if person else None
        if instructor:
            vehicle = getattr(instructor, "vehicle", None)
            area = getattr(instructor, "service_area", None)
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            metrics = (
                instructor.marketplace_events.filter(created_at__gte=month_start)
                .values("event_type")
                .annotate(total=Count("id"))
            )
            metrics_by_type = {row["event_type"]: row["total"] for row in metrics}
            offer = instructor.offers.filter(is_active=True).order_by("price_amount").first()
            payload["instructor"] = {
                "display_name": instructor.display_name,
                "profile_status": instructor.profile_status,
                "publication_status": instructor.publication_status,
                "verification_status": instructor.verification_status,
                "document_count": instructor.documents.count(),
                "photo_count": instructor.profile_photos.count(),
                "vehicle": (
                    {
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "status": vehicle.verification_status,
                    }
                    if vehicle
                    else None
                ),
                "service_area": (
                    {"city": area.city, "uf": area.uf, "radius_km": instructor.service_radius_km}
                    if area
                    else None
                ),
                "pending_requests": instructor.lesson_requests.filter(status="PENDING").count(),
                "offer": (
                    {
                        "price_amount": str(offer.price_amount),
                        "duration_minutes": offer.duration_minutes,
                    }
                    if offer
                    else None
                ),
                "metrics": {
                    "search_impressions": metrics_by_type.get(
                        MarketplaceEvent.Type.SEARCH_RESULT_IMPRESSION, 0
                    ),
                    "profile_views": metrics_by_type.get(
                        MarketplaceEvent.Type.INSTRUCTOR_PROFILE_VIEWED, 0
                    ),
                    "whatsapp_clicks": metrics_by_type.get(
                        MarketplaceEvent.Type.WHATSAPP_CONTACT_CLICKED, 0
                    ),
                },
            }
        if student:
            payload["student"] = {
                "display_name": student.display_name,
                "city": student.city,
                "uf": student.uf.code,
                "intended_category": student.intended_category,
                "preferred_transmission": student.preferred_transmission,
                "request_count": student.lesson_requests.count(),
                "upcoming_lesson_count": student.platform_lessons.filter(
                    status="SCHEDULED"
                ).count(),
            }
        return Response(payload)


class OwnAccountInput(serializers.Serializer):
    student_display_name = serializers.CharField(max_length=120, required=False)
    instructor_display_name = serializers.CharField(max_length=120, required=False)
    phone = serializers.RegexField(r"^\+?[0-9]{10,14}$", required=False, allow_blank=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    student_city = serializers.CharField(max_length=100, required=False)
    student_uf = serializers.CharField(min_length=2, max_length=2, required=False)
    intended_category = serializers.CharField(max_length=8, required=False)
    preferred_transmission = serializers.ChoiceField(
        choices=["MANUAL", "AUTOMATIC", "INDIFFERENT"], required=False
    )
    bio = serializers.CharField(max_length=2000, required=False, allow_blank=True)
    categories = serializers.ListField(
        child=serializers.CharField(max_length=8), required=False, allow_empty=False
    )
    transmission_options = serializers.ListField(
        child=serializers.ChoiceField(choices=["MANUAL", "AUTOMATIC"]),
        required=False,
        allow_empty=False,
    )
    whatsapp = serializers.RegexField(r"^\+55[1-9][0-9]{9,10}$", required=False)
    price_amount = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=1, required=False
    )
    duration_minutes = serializers.IntegerField(min_value=30, max_value=240, required=False)
    instructor_city = serializers.CharField(max_length=100, required=False)
    instructor_uf = serializers.CharField(min_length=2, max_length=2, required=False)
    service_latitude = serializers.FloatField(min_value=-90, max_value=90, required=False)
    service_longitude = serializers.FloatField(min_value=-180, max_value=180, required=False)
    service_radius_km = serializers.ChoiceField(choices=[5, 10, 20, 50], required=False)
    service_location_authorized = serializers.BooleanField(required=False)
    vehicle = serializers.DictField(required=False)

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {name: "Este campo não pode ser alterado." for name in sorted(unknown)}
            )
        return attrs

    def validate_vehicle(self, value):
        allowed = {"category", "make", "model", "year", "transmission", "ownership_type"}
        unknown = set(value) - allowed
        if unknown:
            raise serializers.ValidationError(
                f"Campos não permitidos: {', '.join(sorted(unknown))}"
            )
        return value


def _own_account_payload(user):
    person = user.person
    student = getattr(person, "student_profile", None)
    instructor = getattr(person, "instructor_profile", None)
    payload = {
        "email": user.email,
        "email_editable": False,
        "phone": person.phone,
        "birth_date": person.birth_date,
        "roles": list(
            person.role_assignments.filter(revoked_at__isnull=True).values_list("role", flat=True)
        ),
    }
    if student:
        payload["student"] = {
            "display_name": student.display_name,
            "city": student.city,
            "uf": student.uf.code,
            "intended_category": student.intended_category,
            "preferred_transmission": student.preferred_transmission,
        }
    if instructor:
        area = getattr(instructor, "service_area", None)
        contact = getattr(instructor, "contact_channel", None)
        vehicle = getattr(instructor, "vehicle", None)
        offer = instructor.offers.filter(is_active=True).order_by("created_at").first()
        payload["instructor"] = {
            "display_name": instructor.display_name,
            "bio": instructor.bio,
            "categories": instructor.categories,
            "transmission_options": instructor.transmission_options,
            "profile_status": instructor.profile_status,
            "verification_status": instructor.verification_status,
            "publication_status": instructor.publication_status,
            "whatsapp": contact.whatsapp_e164 if contact else "",
            "price_amount": str(offer.price_amount) if offer else "",
            "duration_minutes": offer.duration_minutes if offer else None,
            "city": area.city if area else "",
            "uf": area.uf if area else "",
            "vehicle": (
                {
                    "category": vehicle.category,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "transmission": vehicle.transmission,
                    "ownership_type": vehicle.ownership_type,
                    "verification_status": vehicle.verification_status,
                }
                if vehicle
                else None
            ),
        }
    return payload


class OwnAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_own_account_payload(request.user))

    @transaction.atomic
    def patch(self, request):
        serializer = OwnAccountInput(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        person = Person.objects.select_for_update().get(account=request.user)
        before = _own_account_payload(request.user)
        person_fields = []
        for field in ("phone", "birth_date"):
            if field in data:
                setattr(person, field, data[field])
                person_fields.append(field)
        if person_fields:
            person.save(update_fields=person_fields)

        student = getattr(person, "student_profile", None)
        if (
            student
            and student.data_mode == DataMode.REAL
            and not settings.SYNTHETIC_MARKETPLACE_ENABLED
            and not all(enabled(name) for name in ("REAL_PERSONAL_DATA", "REAL_STUDENT_USE"))
        ):
            raise PermissionDenied("Edição de dados reais do aluno não está autorizada.")
        if student:
            student_fields = []
            student_mapping = {
                "student_display_name": "display_name",
                "student_city": "city",
                "intended_category": "intended_category",
                "preferred_transmission": "preferred_transmission",
            }
            for input_field, model_field in student_mapping.items():
                if input_field in data:
                    setattr(student, model_field, data[input_field])
                    student_fields.append(model_field)
            if "student_uf" in data:
                student.uf = FederativeUnit.objects.get(code=data["student_uf"].upper())
                student_fields.append("uf")
            if student_fields:
                student.save(update_fields=student_fields)

        instructor = getattr(person, "instructor_profile", None)
        if (
            instructor
            and not instructor.is_demo
            and not settings.SYNTHETIC_MARKETPLACE_ENABLED
            and not all(
                enabled(name) for name in ("REAL_PERSONAL_DATA", "REAL_INSTRUCTOR_REGISTRATION")
            )
        ):
            raise PermissionDenied("Edição de dados reais do instrutor não está autorizada.")
        sensitive = set()
        if instructor:
            profile_fields = []
            instructor_mapping = {
                "instructor_display_name": "display_name",
                "bio": "bio",
                "categories": "categories",
                "transmission_options": "transmission_options",
            }
            for input_field, model_field in instructor_mapping.items():
                if input_field in data:
                    if getattr(instructor, model_field) != data[input_field] and model_field in {
                        "categories",
                        "transmission_options",
                    }:
                        sensitive.add(model_field)
                    setattr(instructor, model_field, data[input_field])
                    profile_fields.append(model_field)
            if profile_fields:
                instructor.save(update_fields=profile_fields)
            if "whatsapp" in data:
                InstructorContactChannel.objects.update_or_create(
                    instructor=instructor,
                    defaults={
                        "whatsapp_e164": data["whatsapp"],
                        "data_mode": DataMode.SYNTHETIC if instructor.is_demo else DataMode.REAL,
                    },
                )
            service_fields = {
                "instructor_city",
                "instructor_uf",
                "service_latitude",
                "service_longitude",
                "service_radius_km",
                "service_location_authorized",
            }
            if service_fields.intersection(data):
                area = (
                    InstructorServiceArea.objects.select_for_update()
                    .filter(profile=instructor)
                    .first()
                )
                required = {
                    "instructor_city",
                    "instructor_uf",
                    "service_latitude",
                    "service_longitude",
                }
                if not area and (missing := required - set(data)):
                    raise serializers.ValidationError(
                        {"service_area": f"Campos obrigatórios: {', '.join(sorted(missing))}"}
                    )
                point = None
                if "service_latitude" in data or "service_longitude" in data:
                    if "service_latitude" not in data or "service_longitude" not in data:
                        raise serializers.ValidationError(
                            "Latitude e longitude públicas devem ser informadas juntas."
                        )
                    point = Point(data["service_longitude"], data["service_latitude"], srid=4326)
                if area:
                    area.city = data.get("instructor_city", area.city)
                    area.uf = data.get("instructor_uf", area.uf).upper()
                    area.radius_km = data.get("service_radius_km", area.radius_km)
                    if point:
                        area.public_service_location = point
                    area.save(update_fields=["city", "uf", "radius_km", "public_service_location"])
                else:
                    area = InstructorServiceArea.objects.create(
                        profile=instructor,
                        city=data["instructor_city"],
                        uf=data["instructor_uf"].upper(),
                        public_service_location=point,
                        private_location=None,
                        radius_km=data.get("service_radius_km", 10),
                        location_authorized=False,
                    )
                if data.get("service_location_authorized") and not area.location_authorized:
                    grant_service_location_authorization(
                        actor=request.user,
                        service_area=area,
                        purpose="CONTROLLED_PILOT_MARKETPLACE_DISCOVERY",
                        policy_version="PILOT-1",
                        reason="OWNER_EXPLICIT_AUTHORIZATION",
                        request_id=getattr(request, "request_id", None),
                    )
            if "price_amount" in data or "duration_minutes" in data:
                offer = instructor.offers.filter(is_active=True).order_by("created_at").first()
                if offer:
                    if "price_amount" in data:
                        offer.price_amount = data["price_amount"]
                    if "duration_minutes" in data:
                        offer.duration_minutes = data["duration_minutes"]
                    offer.save(update_fields=["price_amount", "duration_minutes", "updated_at"])
                elif "price_amount" in data and "duration_minutes" in data:
                    InstructorOffer.objects.create(
                        instructor=instructor,
                        category=instructor.categories[0],
                        price_amount=data["price_amount"],
                        duration_minutes=data["duration_minutes"],
                        data_mode=DataMode.SYNTHETIC if instructor.is_demo else DataMode.REAL,
                    )
                else:
                    raise serializers.ValidationError(
                        "Preço e duração são obrigatórios para criar a primeira oferta."
                    )
            if "vehicle" in data:
                vehicle = (
                    InstructorVehicle.objects.select_for_update()
                    .filter(instructor=instructor)
                    .first()
                )
                if vehicle:
                    for field, value in data["vehicle"].items():
                        if getattr(vehicle, field) != value:
                            setattr(vehicle, field, value)
                            sensitive.add(f"vehicle.{field}")
                    vehicle.verification_status = InstructorVehicle.VerificationStatus.PENDING
                    vehicle.save()
                else:
                    required = {"category", "make", "model", "year", "transmission"}
                    missing = required - set(data["vehicle"])
                    if missing:
                        raise serializers.ValidationError(
                            {"vehicle": f"Campos obrigatórios: {', '.join(sorted(missing))}"}
                        )
                    InstructorVehicle.objects.create(
                        instructor=instructor,
                        data_mode=DataMode.SYNTHETIC if instructor.is_demo else DataMode.REAL,
                        **data["vehicle"],
                    )
                    sensitive.add("vehicle")
            if sensitive and (
                instructor.profile_status != InstructorProfile.Status.DRAFT
                or instructor.verification_status
                != InstructorProfile.VerificationStatus.NOT_STARTED
                or instructor.publication_status != InstructorProfile.PublicationStatus.UNPUBLISHED
            ):
                instructor = invalidate_after_owner_sensitive_edit(
                    actor=request.user,
                    profile=instructor,
                    changed_fields=sensitive,
                    request_id=getattr(request, "request_id", None),
                )

        after = _own_account_payload(request.user)
        AuditEvent.objects.create(
            actor=request.user,
            action="account.own_data.updated",
            target_type="accounts.Account",
            target_id=request.user.id,
            request_id=getattr(request, "request_id", None),
            metadata={
                "changed_fields": sorted(data),
                "before": {
                    "phone": before.get("phone"),
                    "birth_date": before["birth_date"].isoformat()
                    if before.get("birth_date")
                    else None,
                },
                "after": {
                    "phone": after.get("phone"),
                    "birth_date": after["birth_date"].isoformat()
                    if after.get("birth_date")
                    else None,
                },
            },
        )
        return Response(after)


def _request_instructor(request):
    return get_object_or_404(
        InstructorProfile.objects.select_related("person__account"),
        person__account=request.user,
    )


class InstructorSaaSSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        instructor = _request_instructor(request)
        subscription = current_subscription(request.user) or assign_free_plan(request.user)
        metrics = instructor_analytics(instructor, int(request.query_params.get("days", 30)))
        return Response(
            {
                "display_name": instructor.display_name,
                "profile_status": instructor.profile_status,
                "publication_status": instructor.publication_status,
                "plan": {
                    "code": subscription.plan.code,
                    "name": subscription.plan.name,
                    "entitlements": list(
                        subscription.plan.plan_entitlements.order_by(
                            "entitlement__code"
                        ).values_list("entitlement__code", flat=True)
                    ),
                },
                "metrics": metrics,
            }
        )


class InstructorAdvancedAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        _request_instructor(request)
        if not has_entitlement(request.user, "ADVANCED_ANALYTICS"):
            return Response(
                {"code": "entitlement_required", "detail": "Recurso não incluído no plano."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response({"status": "prepared"})


class DemandSerializer(serializers.ModelSerializer):
    uf = serializers.CharField(write_only=True, min_length=2, max_length=2)

    class Meta:
        model = StudentDemand
        fields = [
            "id",
            "category",
            "city",
            "uf",
            "region",
            "radius_km",
            "transmission",
            "availability",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, data):
        data["uf"] = FederativeUnit.objects.get(code=data["uf"].upper())
        return StudentDemand.objects.create(
            student=self.context["student"], data_mode=DataMode.SYNTHETIC, **data
        )


class DemandListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_student(self, request):
        return StudentProfile.objects.get(
            person__account=request.user, data_mode=DataMode.SYNTHETIC
        )

    def get(self, request):
        demands = StudentDemand.objects.filter(student=self.get_student(request)).order_by(
            "-created_at"
        )
        return Response(DemandSerializer(demands, many=True).data)

    def post(self, request):
        if not _synthetic_enabled():
            return Response({"detail": "Synthetic marketplace is disabled"}, status=403)
        student = self.get_student(request)
        serializer = DemandSerializer(data=request.data, context={"student": student})
        serializer.is_valid(raise_exception=True)
        demand = serializer.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="marketplace.synthetic_demand.created",
            target_type="StudentDemand",
            target_id=demand.id,
            metadata={"data_mode": DataMode.SYNTHETIC},
        )
        return Response(DemandSerializer(demand).data, status=201)


class DemandAggregateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        threshold = settings.DEMAND_MAP_MIN_AGGREGATION_COUNT
        if not _synthetic_enabled() or threshold < 1:
            return Response({"detail": "Aggregate demand map is disabled"}, status=404)
        rows = (
            StudentDemand.objects.filter(
                data_mode=DataMode.SYNTHETIC, status=StudentDemand.Status.ACTIVE
            )
            .values("uf__code", "city")
            .annotate(count=Count("id"))
            .filter(count__gte=threshold)
            .order_by("uf__code", "city")
        )
        # Nenhum ponto individual ou identificador de aluno sai deste endpoint.
        return Response(
            {
                "minimum_count": threshold,
                "regions": [
                    {"uf": r["uf__code"], "city": r["city"], "count": r["count"]} for r in rows
                ],
            }
        )


class LessonRequestSerializer(serializers.ModelSerializer):
    instructor_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = LessonRequest
        fields = [
            "id",
            "instructor_id",
            "category",
            "preferred_period",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def create(self, data):
        instructor = InstructorProfile.objects.get(
            pk=data.pop("instructor_id"),
            is_demo=True,
            publication_status=InstructorProfile.PublicationStatus.APPROVED,
        )
        return LessonRequest.objects.create(
            student=self.context["student"],
            instructor=instructor,
            data_mode=DataMode.SYNTHETIC,
            **data,
        )


class LessonRequestListCreateView(DemandListCreateView):
    def get(self, request):
        rows = LessonRequest.objects.filter(student=self.get_student(request)).order_by(
            "-created_at"
        )
        return Response(LessonRequestSerializer(rows, many=True).data)

    def post(self, request):
        if not _synthetic_enabled():
            return Response({"detail": "Synthetic marketplace is disabled"}, status=403)
        serializer = LessonRequestSerializer(
            data=request.data, context={"student": self.get_student(request)}
        )
        serializer.is_valid(raise_exception=True)
        row = serializer.save()
        AuditEvent.objects.create(
            actor=request.user,
            action="marketplace.synthetic_lesson_request.created",
            target_type="LessonRequest",
            target_id=row.id,
            metadata={"data_mode": DataMode.SYNTHETIC},
        )
        return Response(LessonRequestSerializer(row).data, status=201)


class LessonRequestTransitionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        row = LessonRequest.objects.get(
            pk=pk, instructor__person__account=request.user, data_mode=DataMode.SYNTHETIC
        )
        try:
            row = transition_lesson_request(
                lesson_request=row, new_status=request.data.get("status"), actor=request.user
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=409)
        return Response({"id": row.id, "status": row.status})
