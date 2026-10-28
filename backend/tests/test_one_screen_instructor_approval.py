from datetime import timedelta
from uuid import uuid4

import pytest
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Point
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import Account
from apps.audit.models import AuditEvent
from apps.discovery.admin_approval import approval_panel
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


def scenario(*, evidence=True, offer=True, start_review=True):
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
    if start_review:
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
def test_missing_documents_are_not_reported_as_ready():
    web, _, _, profile, _, _, document = scenario()
    document.delete()
    panel = approval_panel(profile, Account.objects.get(username="gilmar"))
    assert panel["documents_ok"] is False
    assert "Documentos sem scanner limpo ou revisão individual" in panel["blockers"]
    assert not panel["document_inventory"]


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_reviewer_finds_files_and_must_assume_request_before_private_download():
    web, change, action, _, _, item, document = scenario(start_review=False)
    download_url = reverse("instructor-document-download", args=[document.pk])
    page = web.get(change)
    content = page.content.decode()
    assert "credential.pdf" not in content
    assert "Arquivos enviados ao perfil: 1" in content
    assert "ASSUMIR ANÁLISE E LIBERAR VISUALIZAÇÃO PRIVADA" in content
    assert download_url not in content

    response = web.post(action, {"operation": "start_review"}, follow=True)
    assert response.status_code == 200
    item.refresh_from_db()
    assert item.status == item.Status.UNDER_REVIEW
    assert "credential.pdf" in response.content.decode()
    assert download_url in response.content.decode()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_verification_request_shows_private_files_and_decision_in_one_screen():
    web, _, _, _, _, item, document = scenario(start_review=False)
    reviewer = Account.objects.get(username="gilmar")
    reviewer.user_permissions.add(
        Permission.objects.get(codename="change_professionalverificationrequest")
    )
    change_url = reverse("admin:discovery_professionalverificationrequest_change", args=[item.pk])
    download_url = reverse("instructor-document-download", args=[document.pk])

    submitted = web.get(change_url)
    assert submitted.status_code == 200
    assert "ASSUMIR ANÁLISE" in submitted.content.decode()
    assert "credential.pdf" not in submitted.content.decode()
    assert download_url not in submitted.content.decode()

    start_url = reverse("admin:discovery_verification_request_transition", args=[item.pk, "start"])
    assert web.post(start_url).status_code == 302
    reviewing = web.get(change_url)
    content = reviewing.content.decode()
    assert reviewing.status_code == 200
    assert "credential.pdf" in content
    assert download_url in content
    assert "APROVAR DOCUMENTOS E VERIFICAÇÃO" in content


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_admin_finds_documents_by_instructor_and_request():
    web, _, _, _, _, item, document = scenario()
    reviewer = Account.objects.get(username="gilmar")
    reviewer.user_permissions.add(
        Permission.objects.get(codename="change_professionalverificationrequest"),
        Permission.objects.get(codename="view_instructordocument"),
    )
    request_url = reverse("admin:discovery_professionalverificationrequest_change", args=[item.pk])
    queue = web.get(reverse("admin:discovery_professionalverificationrequest_changelist"))
    assert queue.status_code == 200
    assert "Instrutor Real" in queue.content.decode()
    assert "1 arquivo(s)" in queue.content.decode()

    document_list = web.get(reverse("admin:marketplace_instructordocument_changelist"))
    content = document_list.content.decode()
    assert document_list.status_code == 200
    assert "Escolher instrutor e ver documentos" in content
    assert "Instrutor Real" in content
    assert "Credencial profissional" in content
    assert "credential.pdf" in content
    assert request_url in content
    assert "1 arquivo(s) vinculado(s)" in web.get(request_url).content.decode()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_document_list_does_not_expose_real_file_before_assignment():
    web, _, _, _, _, item, document = scenario(start_review=False)
    reviewer = Account.objects.get(username="gilmar")
    reviewer.user_permissions.add(
        Permission.objects.get(codename="view_instructordocument"),
        Permission.objects.get(codename="change_professionalverificationrequest"),
    )
    document_list = web.get(reverse("admin:marketplace_instructordocument_changelist"))
    assert document_list.status_code == 200
    assert "credential.pdf" not in document_list.content.decode()
    assert "Documentos vinculados ao instrutor" in document_list.content.decode()
    assert "Escolher instrutor e ver documentos" in document_list.content.decode()


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_authorized_reviewer_can_decide_documents_without_responsible_username():
    web, change, action, profile, readiness, item, document = scenario(start_review=False)
    reviewer = Account.objects.create_user(
        username="document-reviewer",
        email="document-reviewer@example.invalid",
        password="test-password-123",
        is_staff=True,
    )
    reviewer.user_permissions.add(
        Permission.objects.get(codename="change_instructorprofile"),
        Permission.objects.get(codename="review_professional_verification"),
        Permission.objects.get(codename="review_instructor_document"),
    )
    web.force_login(reviewer)
    assert web.post(action, {"operation": "start_review"}).status_code == 302
    page = web.get(change)
    content = page.content.decode()
    assert "credential.pdf" in content
    assert "VISUALIZAR ARQUIVO PRIVADO" in content
    assert "APROVAR DOCUMENTOS E VERIFICAÇÃO" in content
    assert "ANALISAR E PUBLICAR" not in content
    assert (
        web.post(
            action,
            {
                "operation": "approve_verification",
                "confirm_verification": "on",
                "reviewed_document_ids": [str(document.pk)],
                "verification_method": "Conferência documental humana",
                "verification_source": "Credencial e fonte conferidas",
            },
        ).status_code
        == 302
    )
    item.refresh_from_db()
    document.refresh_from_db()
    profile.refresh_from_db()
    readiness.refresh_from_db()
    assert item.status == item.Status.VERIFIED
    assert document.status == document.Status.APPROVED
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert readiness.status == readiness.Status.REVIEW_REQUIRED


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_older_document_is_locatable_but_not_downloadable_from_current_request():
    web, change, _, profile, _, _, _ = scenario()
    older_request = ProfessionalVerificationRequest.objects.create(
        profile=profile, status=ProfessionalVerificationRequest.Status.REJECTED
    )
    ProfessionalVerificationRequest.objects.filter(pk=older_request.pk).update(
        created_at=timezone.now() - timedelta(days=2)
    )
    older = InstructorDocument.objects.create(
        instructor=profile,
        verification_request=older_request,
        document_type=InstructorDocument.DocumentType.DRIVER_LICENSE,
        file=f"private-test/{uuid4()}.pdf",
        original_name="older-cnh.pdf",
        mime_type="application/pdf",
        size_bytes=8,
        sha256="1" * 64,
        scan_status=InstructorDocument.ScanStatus.CLEAN,
        data_mode=DataMode.REAL,
    )
    content = web.get(change).content.decode()
    assert "older-cnh.pdf" in content
    assert reverse("instructor-document-download", args=[older.pk]) not in content


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_document_inventory_is_hidden_without_document_review_permission():
    web, change, _, _, _, _, document = scenario()
    reviewer = Account.objects.get(username="gilmar")
    reviewer.user_permissions.remove(Permission.objects.get(codename="review_instructor_document"))
    content = web.get(change).content.decode()
    assert "credential.pdf" not in content
    assert reverse("instructor-document-download", args=[document.pk]) not in content
    assert "Somente um revisor com permissão" in content


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_submitted_request_can_be_reviewed_and_published_in_one_human_action():
    web, change, action, profile, readiness, item, document = scenario(start_review=False)
    page = web.get(change)
    assert page.status_code == 200
    assert "ASSUMIR ANÁLISE E LIBERAR VISUALIZAÇÃO PRIVADA" in page.content.decode()
    response = web.post(action, combined_data(document), follow=True)
    assert response.status_code == 200
    for obj in (profile, readiness, item, document):
        obj.refresh_from_db()
    assert item.status == item.Status.VERIFIED
    assert item.reviewer.username == "gilmar"
    assert readiness.status == readiness.Status.APPROVED
    assert document.status == document.Status.APPROVED
    assert profile.publication_status == profile.PublicationStatus.APPROVED


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_submitted_request_review_rolls_back_when_offer_is_missing():
    web, _, action, profile, readiness, item, document = scenario(start_review=False, offer=False)
    response = web.post(action, combined_data(document), follow=True)
    assert response.status_code == 200
    for obj in (profile, readiness, item, document):
        obj.refresh_from_db()
    assert item.status == item.Status.SUBMITTED
    assert item.reviewer_id is None
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert document.status == document.Status.PENDING
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED


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
    assert "Próximo passo: completar a revisão da UF GO" in content
    assert reverse("admin:territories_regulatoryreadiness_change", args=[readiness.pk]) in content
    assert "Salve a evidência na nova aba" in content
    assert "ANALISAR E PUBLICAR" in content
    readiness.refresh_from_db()
    profile.refresh_from_db()
    item.refresh_from_db()
    assert readiness.status == readiness.Status.REVIEW_REQUIRED
    assert profile.publication_status == profile.PublicationStatus.UNPUBLISHED
    assert item.status == item.Status.UNDER_REVIEW


@pytest.mark.django_db
@override_settings(**SETTINGS)
def test_regulatory_shortcut_is_hidden_without_regulatory_permission():
    web, change, _, _, readiness, _, _ = scenario(evidence=False)
    admin = Account.objects.get(username="gilmar")
    admin.user_permissions.remove(Permission.objects.get(codename="change_regulatoryreadiness"))
    content = web.get(change).content.decode()
    assert "Peça a um administrador com permissão regulatória" in content
    edit_url = reverse("admin:territories_regulatoryreadiness_change", args=[readiness.pk])
    assert edit_url not in content


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
    assert "B=NÃO" in web.get(change).content.decode()
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
def test_human_publication_accepts_a_and_b_with_only_a_offer_but_search_keeps_b_hidden():
    web, _, action, profile, readiness, item, document = scenario()
    profile.refresh_from_db()
    profile.categories = ["A", "B"]
    profile.save(update_fields=["categories"])
    approved = web.post(action, combined_data(document))
    assert approved.status_code == 302
    profile.refresh_from_db()
    assert profile.publication_status == profile.PublicationStatus.APPROVED
    assert set(profile.offers.filter(is_active=True).values_list("category", flat=True)) == {"A"}
    assert PublicationDecision.objects.filter(profile=profile, decision="APPROVE").count() == 1
    assert [
        row.pk
        for row in search_published_instructors(latitude=-18.02, longitude=-49.35, category="A")
    ] == [profile.pk]
    assert list(search_published_instructors(latitude=-18.02, longitude=-49.35, category="B")) == []


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
