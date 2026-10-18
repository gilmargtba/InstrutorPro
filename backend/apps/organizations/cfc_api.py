"""Private CFC pre-registration. Instructor eligibility remains in discovery."""

import uuid

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import InstructorProfile
from apps.marketplace.capabilities import enabled
from apps.people.models import Person, RoleAssignment
from apps.privacy.models import LegalAcceptanceRecord, LegalDocument, PrivacyNotice

from .models import CFC, CFCInstructorLink, CFCMembership


class EmailUnavailable(APIException):
    status_code = 503
    default_detail = "O pré-cadastro está indisponível até o e-mail transacional funcionar."


def _email_ready():
    backend = settings.EMAIL_BACKEND
    if backend in {
        "django.core.mail.backends.console.EmailBackend",
        "django.core.mail.backends.dummy.EmailBackend",
    }:
        return False
    if backend == "django.core.mail.backends.smtp.EmailBackend" and not settings.EMAIL_HOST:
        return False
    return bool(settings.DEFAULT_FROM_EMAIL)


def _send_activation_email(link):
    account = link.account
    uid = urlsafe_base64_encode(force_bytes(account.pk))
    token = default_token_generator.make_token(account)
    url = f"{settings.FRONTEND_PUBLIC_URL}/cfc/ativar-instrutor?uid={uid}&token={token}"
    try:
        sent = send_mail(
            "Ative seu pré-cadastro de instrutor — InstrutorProCNH",
            f"{link.cfc.display_name} iniciou um pré-cadastro em seu nome. "
            "Se você reconhece o CFC, crie sua própria senha e aceite o vínculo aqui: "
            f"{url}\n\n"
            "O pré-cadastro não verifica nem publica seu perfil. "
            "Se você não reconhece o convite, ignore esta mensagem.",
            settings.DEFAULT_FROM_EMAIL,
            [account.email],
            fail_silently=False,
        )
        if sent != 1:
            raise RuntimeError("Entrega não confirmada")
    except Exception as exc:
        raise EmailUnavailable() from exc


def _membership(actor, cfc_id):
    if not actor.is_authenticated or not actor.can_operate:
        raise PermissionDenied("Acesso ao CFC negado.")
    membership = (
        CFCMembership.objects.select_related("cfc")
        .filter(
            cfc_id=cfc_id,
            person__account=actor,
            is_active=True,
            cfc__is_active=True,
        )
        .first()
    )
    if not membership:
        raise PermissionDenied("Acesso ao CFC negado.")
    return membership


class CFCCountSerializer(serializers.Serializer):
    declared_instructor_count = serializers.IntegerField(min_value=0, max_value=100000)


class CFCInstructorSerializer(serializers.Serializer):
    display_name = serializers.CharField(max_length=120, trim_whitespace=True)
    email = serializers.EmailField()


class CFCActivationSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    birth_date = serializers.DateField()
    password = serializers.CharField(write_only=True, min_length=10)
    password_confirmation = serializers.CharField(write_only=True, min_length=10)
    terms_version = serializers.CharField(max_length=40)
    privacy_version = serializers.CharField(max_length=40)
    terms_accepted = serializers.BooleanField()
    privacy_acknowledged = serializers.BooleanField()
    cfc_link_accepted = serializers.BooleanField()

    def validate(self, attrs):
        if not all(
            enabled(name)
            for name in (
                "REAL_ACCOUNT_REGISTRATION",
                "REAL_PERSONAL_DATA",
                "REAL_INSTRUCTOR_REGISTRATION",
            )
        ):
            raise PermissionDenied("Cadastro real de instrutor não está autorizado.")
        if not all(
            attrs[key] for key in ("terms_accepted", "privacy_acknowledged", "cfc_link_accepted")
        ):
            raise serializers.ValidationError(
                "Confirme os aceites obrigatórios e o vínculo com o CFC."
            )
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({"password_confirmation": "As senhas não coincidem."})
        today = timezone.localdate()
        birth = attrs["birth_date"]
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        if age < 18:
            raise serializers.ValidationError(
                {"birth_date": "Cadastro restrito a maiores de 18 anos."}
            )
        try:
            account_id = force_str(urlsafe_base64_decode(attrs["uid"]))
            attrs["account_id"] = uuid.UUID(account_id)
        except (ValueError, TypeError, OverflowError, UnicodeDecodeError) as exc:
            raise serializers.ValidationError("Convite inválido ou expirado.") from exc
        attrs["terms_document"] = LegalDocument.objects.filter(
            document_type=LegalDocument.Type.TERMS,
            audience=LegalDocument.Audience.INSTRUCTOR,
            version=attrs["terms_version"],
            is_active=True,
            effective_at__lte=timezone.now(),
        ).first()
        attrs["privacy_notice"] = PrivacyNotice.objects.filter(
            version=attrs["privacy_version"],
            is_current=True,
            published_at__lte=timezone.now(),
        ).first()
        if not attrs["terms_document"] or not attrs["privacy_notice"]:
            raise serializers.ValidationError("As versões jurídicas informadas não estão vigentes.")
        return attrs


class CFCMembershipListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.can_operate:
            raise PermissionDenied("Acesso ao CFC negado.")
        rows = (
            CFCMembership.objects.select_related("cfc")
            .filter(person__account=request.user, is_active=True, cfc__is_active=True)
            .order_by("cfc__display_name")
        )
        return Response([{"id": row.cfc_id, "display_name": row.cfc.display_name} for row in rows])


class CFCDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cfc_id):
        cfc = _membership(request.user, cfc_id).cfc
        return Response(
            {
                "id": cfc.id,
                "display_name": cfc.display_name,
                "declared_instructor_count": cfc.declared_instructor_count,
                "pre_registered_count": cfc.instructor_links.count(),
                "accepted_count": cfc.instructor_links.filter(
                    status=CFCInstructorLink.Status.ACCEPTED
                ).count(),
            }
        )

    @extend_schema(
        request=CFCCountSerializer,
        responses={200: OpenApiResponse(description="Contagem informada atualizada.")},
    )
    @transaction.atomic
    def patch(self, request, cfc_id):
        _membership(request.user, cfc_id)
        serializer = CFCCountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cfc = CFC.objects.select_for_update().get(pk=cfc_id)
        old_count = cfc.declared_instructor_count
        cfc.declared_instructor_count = serializer.validated_data["declared_instructor_count"]
        cfc.save(update_fields=["declared_instructor_count"])
        AuditEvent.objects.create(
            actor=request.user,
            action="cfc.instructor_count.updated",
            target_type="organizations.CFC",
            target_id=cfc.id,
            request_id=getattr(request, "request_id", None),
            metadata={"previous": old_count, "new": cfc.declared_instructor_count},
        )
        return Response({"declared_instructor_count": cfc.declared_instructor_count})


class CFCInstructorListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "cfc_pre_registration"

    def get_throttles(self):
        return [ScopedRateThrottle()] if self.request.method == "POST" else []

    def get(self, request, cfc_id):
        cfc = _membership(request.user, cfc_id).cfc
        rows = cfc.instructor_links.select_related("account").order_by("-invited_at")
        return Response(
            [
                {
                    "id": row.id,
                    "display_name": row.display_name,
                    "email": row.account.email,
                    "status": row.status,
                    "invited_at": row.invited_at,
                }
                for row in rows
            ]
        )

    @extend_schema(
        request=CFCInstructorSerializer,
        responses={201: OpenApiResponse(description="Convite de ativação enviado.")},
    )
    @transaction.atomic
    def post(self, request, cfc_id):
        cfc = _membership(request.user, cfc_id).cfc
        if not all(
            enabled(name)
            for name in (
                "REAL_ACCOUNT_REGISTRATION",
                "REAL_PERSONAL_DATA",
                "REAL_INSTRUCTOR_REGISTRATION",
            )
        ):
            raise PermissionDenied("Cadastro real de instrutor não está autorizado.")
        if not _email_ready():
            raise EmailUnavailable()
        serializer = CFCInstructorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if Account.objects.filter(email__iexact=data["email"]).exists():
            return Response(
                {"detail": "Este e-mail já possui conta. O vínculo exige análise separada."},
                status=409,
            )
        try:
            account = Account.objects.create_user(
                username=f"cfc-{uuid.uuid4().hex}",
                email=data["email"].lower(),
                password=None,
                is_active=False,
                lifecycle_status=Account.LifecycleStatus.BLOCKED,
                lifecycle_reason="CFC_INVITATION_PENDING",
            )
        except IntegrityError:
            return Response({"detail": "Este e-mail já possui conta."}, status=409)
        link = CFCInstructorLink.objects.create(
            cfc=cfc, account=account, display_name=data["display_name"]
        )
        _send_activation_email(link)
        AuditEvent.objects.create(
            actor=request.user,
            action="cfc.instructor.pre_registered",
            target_type="organizations.CFCInstructorLink",
            target_id=link.id,
            request_id=getattr(request, "request_id", None),
            metadata={"cfc_id": str(cfc.id)},
        )
        return Response({"id": link.id, "status": link.status}, status=status.HTTP_201_CREATED)


class CFCInstructorResendView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    @transaction.atomic
    def post(self, request, cfc_id, link_id):
        _membership(request.user, cfc_id)
        if not all(
            enabled(name)
            for name in (
                "REAL_ACCOUNT_REGISTRATION",
                "REAL_PERSONAL_DATA",
                "REAL_INSTRUCTOR_REGISTRATION",
            )
        ):
            raise PermissionDenied("Cadastro real de instrutor não está autorizado.")
        if not _email_ready():
            raise EmailUnavailable()
        link = (
            CFCInstructorLink.objects.select_related("cfc", "account")
            .select_for_update()
            .filter(pk=link_id, cfc_id=cfc_id, status=CFCInstructorLink.Status.PENDING)
            .first()
        )
        if not link or link.account.is_active:
            return Response({"detail": "Pré-cadastro pendente não encontrado."}, status=404)
        _send_activation_email(link)
        AuditEvent.objects.create(
            actor=request.user,
            action="cfc.instructor.invitation_resent",
            target_type="organizations.CFCInstructorLink",
            target_id=link.id,
            request_id=getattr(request, "request_id", None),
        )
        return Response({"detail": "Convite reenviado."})


class CFCInstructorActivationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "registration"

    @extend_schema(
        request=CFCActivationSerializer,
        responses={200: OpenApiResponse(description="Conta ativada; perfil ainda não publicado.")},
    )
    @transaction.atomic
    def post(self, request):
        serializer = CFCActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        account = Account.objects.select_for_update().filter(pk=data["account_id"]).first()
        if (
            not account
            or account.is_active
            or not default_token_generator.check_token(account, data["token"])
        ):
            raise serializers.ValidationError("Convite inválido ou expirado.")
        link = (
            CFCInstructorLink.objects.select_related("cfc")
            .select_for_update()
            .filter(account=account, status=CFCInstructorLink.Status.PENDING, cfc__is_active=True)
            .first()
        )
        if not link:
            raise serializers.ValidationError("Convite inválido ou expirado.")
        try:
            validate_password(data["password"], user=account)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from exc
        account.set_password(data["password"])
        account.is_active = True
        account.lifecycle_status = Account.LifecycleStatus.ACTIVE
        account.lifecycle_reason = "CFC_INVITATION_ACCEPTED"
        account.lifecycle_changed_at = timezone.now()
        account.lifecycle_version += 1
        account.save(
            update_fields=[
                "password",
                "is_active",
                "lifecycle_status",
                "lifecycle_reason",
                "lifecycle_changed_at",
                "lifecycle_version",
            ]
        )
        person = Person.objects.create(account=account, birth_date=data["birth_date"])
        RoleAssignment.objects.create(
            person=person,
            role=RoleAssignment.Role.INSTRUCTOR,
            grant_reason="CFC_PRE_REGISTRATION_SELF_ACTIVATION",
        )
        InstructorProfile.objects.create(
            person=person,
            display_name=link.display_name,
            categories=[],
            transmission_options=[],
            is_demo=False,
        )
        acceptance = LegalAcceptanceRecord.objects.create(
            account=account,
            terms_document=data["terms_document"],
            privacy_notice=data["privacy_notice"],
            request_id=getattr(request, "request_id", None),
        )
        link.status = CFCInstructorLink.Status.ACCEPTED
        link.accepted_at = timezone.now()
        link.save(update_fields=["status", "accepted_at"])
        AuditEvent.objects.create(
            actor=account,
            action="cfc.instructor.activated",
            target_type="organizations.CFCInstructorLink",
            target_id=link.id,
            request_id=getattr(request, "request_id", None),
            metadata={"cfc_id": str(link.cfc_id), "acceptance_id": str(acceptance.id)},
        )
        login(request, account, backend="django.contrib.auth.backends.ModelBackend")
        get_token(request)
        return Response({"status": link.status, "instructor_profile_status": "DRAFT"})
