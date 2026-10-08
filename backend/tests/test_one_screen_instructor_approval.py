from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.models import (
    InstructorProfile,
    InstructorServiceArea,
    ProfessionalVerificationRequest,
    PublicationDecision,
)
from apps.discovery.selectors import search_published_instructors
from apps.discovery.verification_services import start_verification_review
from apps.marketplace.models import (
    DataMode,
    InstructorContactChannel,
    InstructorDocument,
    InstructorOffer,
)
from apps.people.models import Person, RoleAssignment
from apps.territories.models import Country, FederativeUnit, RegulatoryReadiness

SETTINGS = {
    "SYNTHETIC_MARKETPLACE_ENABLED": False,
    "REAL_MARKETPLACE_SEARCH": True,
    "REAL_WHATSAPP_CONTACT": True,
    "REAL_PRODUCTION_AUTHORIZATION": "NOT_GRANTED",
    "PROFESSIONAL_VERIFICATION_MODE": "PRODUCTION",
    "REAL_PROFESSIONAL_VERIFICATION": True,
}


def scenario(*, evidence=True, offer=True):
    owner = Account.objects.create_user(
        username="owner-one-screen", email="owner@example.invalid", password="test-password-123"
    )
    person = Person.objects.create(account=owner)
    RoleAssignment.objects.create(
        person=person,
        role=RoleAssignment.Role.INSTRUCTOR,
        granted_by=owner,
        grant_reason="TEST",
    )
    profile = InstructorProfile.objects.create(
        person=person, display_name="Instrutor Real", is_demo=False, categories=["A"]
    )
    InstructorServiceArea.objects.create(
        profile=profile,
        city="Goiatuba",
        uf="GO",
        public_service_location=Point(-49.35, -18.02, srid=4326),
        location_authorized=True,
        radius_km=10,
    )
    InstructorContactChannel.objects.create(
        instructor=profile, whatsapp_e164="+5564999999999", is_active=True, data_mode=DataMode.REAL
    )
    if offer:
        InstructorOffer.objects.create(
            instructor=profile,
            category="A",
            price_amount="120.00",
            duration_minutes=60,
            data_mode=DataMode.REAL,
        )
    country, _ = Country.objects.get_or_create(code="BR", defaults={"name": "Brasil"})
    uf, _ = FederativeUnit.objects.get_or_create(
        code="GO", defaults={"country": country, "name": "Goiás", "ibge_code": "52"}
    )
    readiness = RegulatoryReadiness.objects.create(
        federative_unit=uf,
        provider_type="INSTRUCTOR",
        capability="INSTRUCTOR_PUBLICATION",
        status=RegulatoryReadiness.Status.REVIEW_REQUIRED,
        source_url="https://www.go.gov.br/fonte-oficial" if evidence else "",
        source_reference="Norma de teste GO" if evidence else "",
        source_authority="Órgão de teste" if evidence else "",
        source_consulted_at=timezone.localdate() if evidence else None,
        evidence="Evidência de teste revista pelo humano" if evidence else "",
        notes="Escopo de teste" if evidence else "",
    )
    admin = Account.objects.create_user(
        username="gilmar",
        email="admin@example.invalid",
        password="test-password-123",
        is_staff=True,
    )
    admin.user_permissions.add(
        *Permission.objects.filter(
            codename__in=[
                "change_instructorprofile",
                "review_professional_verification",
                "review_instructor_document",
                "manage_instructor_publication",
                "change_regulatoryreadiness",
                "change_instructoroffer",
            ]
        )
    )
    item = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.SUBMITTED
    )
    start_verification_review(actor=admin, verification_request=item)
    document = InstructorDocument.objects.create(
        instructor=profile,
        verification_request=item,
        document_type=InstructorDocument.DocumentType.PROFESSIONAL_CREDENTIAL,
        file=f"private-test/{uuid4()}.pdf",
        original_name="credential.pdf",
        mime_type="application/pdf",
        size_bytes=8,
        sha256="0" * 64,
        scan_status=InstructorDocument.ScanStatus.CLEAN,
        data_mode=DataMode.REAL,
    )
    web = Client()
    web.force_login(admin)
    change = reverse("admin:discovery_instructorprofile_change", args=[profile.pk])
    action = reverse("admin:discovery_instructor_approval_action", args=[profile.pk])
    return web, change, action, profile, readiness, item, document


def combined_data(document):
    return {
        "operation": "approve_publish",
        "confirm_uf": "on",
        "valid_from": timezone.localdate().isoformat(),
        "uf_reason": "Fonte e vigência conferidas",
        "confirm_verification": "on",
        "reviewed_document_ids": [str(document.pk)],
        "verification_method": "Conferência documental humana",
        "verification_source": "Fonte de teste consultada",
        "confirm_publish": "on",
        "publication_reason": "Publicação humana após elegibilidade",
    }


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_panel_shows_all_blockers_and_never_approves_on_get():
    web, change, _, profile, readiness, item, _ = scenario(evidence=False, offer=False)
    response = web.get(change)
    assert response.status_code == 200
    content = response.content.decode()
    assert "APROVAÇÃO E PUBLICAÇÃO" in content
    assert "UF GO sem aprovação regulatória vigente" in content
    assert "Nenhuma oferta real ativa" in content
    assert "link da fonte oficial" in content
    assert "APROVAR E PUBLICAR INSTRUTOR" in content
    readiness.refresh_from_db()
    profile.refresh_from_db()
    item.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert item.status == item.Status.UNDER_REVIEW


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_combined_action_rolls_back_every_decision_when_offer_is_missing():
    web, _, action, profile, readiness, item, document = scenario(offer=False)
    response = web.post(action, combined_data(document), follow=True)
    assert response.status_code == 200
    assert "Nenhuma oferta real ativa" in response.content.decode()
    for obj in (profile, readiness, item, document):
        obj.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert item.status == item.Status.UNDER_REVIEW
    assert document.status == document.Status.PENDING
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert not PublicationDecision.objects.filter(profile=profile).exists()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_combined_action_requires_explicit_human_uf_confirmation():
    web, _, action, profile, readiness, item, document = scenario()
    data = combined_data(document)
    del data["confirm_uf"]
    response = web.post(action, data, follow=True)
    assert response.status_code == 200
    readiness.refresh_from_db()
    item.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert item.status == item.Status.UNDER_REVIEW
    assert not PublicationDecision.objects.filter(profile=profile).exists()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_combined_action_approves_uf_documents_verification_and_publication_once():
    web, change, action, profile, readiness, item, document = scenario()
    response = web.post(action, combined_data(document), follow=True)
    assert response.status_code == 200
    for obj in (profile, readiness, item, document):
        obj.refresh_from_db()
    assert readiness.status == readiness.Status.APPROVED
    assert readiness.reviewed_by.username == "gilmar"
    assert readiness.approved_by.username == "gilmar"
    assert item.status == item.Status.VERIFIED
    assert document.status == document.Status.APPROVED
    assert profile.publication_status == profile.PublicationStatus.APPROVED
    assert PublicationDecision.objects.filter(profile=profile, decision="APPROVE").count() == 1
    assert AuditEvent.objects.filter(action="territories.regulatory_readiness_approve").count() == 1
    page = web.get(change).content.decode()
    assert "VER PERFIL PÚBLICO" in page
    assert "TESTAR NA BUSCA" in page


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_offer_b_is_not_copied_from_a_without_explicit_profile_category():
    web, _, action, profile, _, _, _ = scenario()
    response = web.post(
        action,
        {
            "operation": "save_offer",
            "offer_category": "B",
            "offer_price": "120.00",
            "offer_duration": "60",
            "offer_active": "on",
            "offer_reason": "Oferta B conferida",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert not InstructorOffer.objects.filter(instructor=profile, category="B").exists()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_offer_b_requires_explicit_category_price_duration_and_audit():
    web, change, action, profile, _, _, _ = scenario()
    profile.refresh_from_db()
    profile.categories = ["A", "B"]
    profile.save(update_fields=["categories"])
    assert "Oferta B inexistente ou inativa" in web.get(change).content.decode()
    response = web.post(
        action,
        {
            "operation": "save_offer",
            "offer_category": "B",
            "offer_price": "150.00",
            "offer_duration": "75",
            "offer_active": "on",
            "offer_reason": "Instrutor confirmou categoria B",
        },
    )
    assert response.status_code == 302
    offer = InstructorOffer.objects.get(instructor=profile, category="B")
    assert offer.is_active and offer.price_amount == 150 and offer.duration_minutes == 75
    assert AuditEvent.objects.filter(
        action="discovery.instructor_offer.admin_saved", target_id=offer.pk
    ).exists()
    assert profile.offers.get(category="A").price_amount == 120


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_human_publication_accepts_a_and_b_only_after_b_has_its_own_offer():
    web, _, action, profile, readiness, item, document = scenario()
    profile.refresh_from_db()
    profile.categories = ["A", "B"]
    profile.save(update_fields=["categories"])
    blocked = web.post(action, combined_data(document), follow=True)
    assert "Oferta B inexistente ou inativa" in blocked.content.decode()
    assert not PublicationDecision.objects.filter(profile=profile).exists()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    saved = web.post(
        action,
        {
            "operation": "save_offer",
            "offer_category": "B",
            "offer_price": "150.00",
            "offer_duration": "90",
            "offer_active": "on",
            "offer_reason": "Categoria B conferida separadamente",
        },
    )
    assert saved.status_code == 302
    approved = web.post(action, combined_data(document))
    assert approved.status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == profile.PublicationStatus.APPROVED
    assert set(profile.offers.filter(is_active=True).values_list("category", flat=True)) == {
        "A",
        "B",
    }
    assert PublicationDecision.objects.filter(profile=profile, decision="APPROVE").count() == 1
    for category in ("A", "B"):
        results = list(
            search_published_instructors(latitude=-18.02, longitude=-49.35, category=category)
        )
        assert [row.pk for row in results] == [profile.pk]


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_incomplete_uf_evidence_never_changes_readiness_or_verification():
    web, _, action, profile, readiness, item, document = scenario(evidence=False)
    response = web.post(action, combined_data(document), follow=True)
    assert response.status_code == 200
    assert "Faltam evidências da UF" in response.content.decode()
    readiness.refresh_from_db()
    item.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert item.status == item.Status.UNDER_REVIEW
    assert not PublicationDecision.objects.filter(profile=profile).exists()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_non_responsible_admin_cannot_use_combined_action():
    web, _, action, profile, readiness, item, document = scenario()
    other = Account.objects.create_user(
        username="another-admin",
        email="other@example.invalid",
        password="test-password-123",
        is_staff=True,
        is_superuser=True,
    )
    web.force_login(other)
    response = web.post(action, combined_data(document))
    assert response.status_code == 403
    readiness.refresh_from_db()
    item.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert item.status == item.Status.UNDER_REVIEW
    assert not PublicationDecision.objects.filter(profile=profile).exists()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_combined_action_replay_cannot_publish_twice():
    web, _, action, profile, _, _, document = scenario()
    data = combined_data(document)
    assert web.post(action, data).status_code == 302
    assert web.post(action, data).status_code == 302
    assert PublicationDecision.objects.filter(profile=profile, decision="APPROVE").count() == 1


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_invalid_offer_price_is_rejected_without_server_error():
    web, _, action, profile, _, _, _ = scenario()
    response = web.post(
        action,
        {
            "operation": "save_offer",
            "offer_category": "A",
            "offer_price": "NaN",
            "offer_duration": "60",
            "offer_active": "on",
            "offer_reason": "Teste de entrada inválida",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert profile.offers.get(category="A").price_amount == 120
