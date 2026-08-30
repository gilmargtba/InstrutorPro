from django.conf import settings
from django.contrib.auth import login, logout
from django.db import transaction
from django.db.models import Count
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.people.models import Person, RoleAssignment
from apps.territories.models import FederativeUnit

from .models import DataMode, LessonRequest, StudentDemand, StudentProfile
from .services import transition_lesson_request


def _synthetic_enabled():
    return settings.SYNTHETIC_MARKETPLACE_ENABLED


class StudentRegistrationSerializer(serializers.Serializer):
    username = serializers.RegexField(r"^[a-zA-Z0-9_.-]+$", max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    display_name = serializers.CharField(max_length=120)
    city = serializers.CharField(max_length=100)
    uf = serializers.CharField(min_length=2, max_length=2)
    intended_category = serializers.CharField(max_length=8, default="B")
    synthetic_data_confirmed = serializers.BooleanField()

    def validate(self, attrs):
        if not _synthetic_enabled():
            raise serializers.ValidationError("Synthetic marketplace is disabled")
        if not attrs["synthetic_data_confirmed"] or not attrs["email"].endswith("@example.invalid"):
            raise serializers.ValidationError(
                "Use only explicit synthetic identities ending in @example.invalid"
            )
        attrs["uf_object"] = FederativeUnit.objects.get(code=attrs["uf"].upper())
        return attrs

    @transaction.atomic
    def create(self, data):
        uf = data.pop("uf_object")
        data.pop("uf")
        data.pop("synthetic_data_confirmed")
        password = data.pop("password")
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

    def post(self, request):
        serializer = StudentRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        login(
            request,
            profile.person.account,
            backend="django.contrib.auth.backends.ModelBackend",
        )
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
