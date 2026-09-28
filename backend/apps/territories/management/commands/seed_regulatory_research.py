from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.audit.models import AuditEvent
from apps.territories.models import FederativeUnit, RegulatoryReadiness
from apps.territories.policies import INSTRUCTOR_PROVIDER_TYPE, INSTRUCTOR_PUBLICATION_CAPABILITY

# This is an evidence inventory, never an approval. Details and caveats are in the national report.
EVIDENCE = {
    "AC": (
        "Portarias 308/309/2026 (alterações a conferir)",
        "https://agencia.ac.gov.br/wp-content/uploads/2025/12/DO17658890660004-PORTARIA-DETRAN.pdf",
    ),
    "AL": (
        "Portaria DETRAN 81/2026",
        "https://diario.imprensaoficial.al.gov.br/apinova/api/editions/viewPdf/51308",
    ),
    "AP": (
        "DOE/AP 28/01/2026 (ato a identificar)",
        "https://diofe.portal.ap.gov.br/portal/edicoes/visualizar_pdf/9818/",
    ),
    "AM": (
        "Portaria normativa 007/2026 (exame, não autorização)",
        "https://www.detran.am.gov.br/wp-content/uploads/2026/04/01.03.011210.015588_2026_18_Portaria.pdf",
    ),
    "BA": (
        "Portaria 599/2025; alteração 108/2026 pendente",
        "https://www.ba.gov.br/detran/sites/site-detran/files/2025-12/Di%C3%A1rio%20Oficial%20do%20Estado%20da%20Bahia%20do%20dia%2030122025%20%20Edi%C3%A7%C3%A3o%2024307%20Edi%C3%A7%C3%A3o%20Principal.pdf",
    ),
    "CE": (
        "Portaria 189/2026; norma-base 156/2026 pendente",
        "https://imagens.seplag.ce.gov.br/PDF/20260212/do20260212p03.pdf",
    ),
    "DF": (
        "Instruções 38 e 161/2026",
        "https://www.sinj.df.gov.br/sinj/Norma/a7131d78dee44cf88e088ac476884a90/detran_ins_38_2026.html",
    ),
    "ES": (
        "Instrução de Serviço 016/2026",
        "https://detran.es.gov.br/Media/detran/Legislacao/Instrucoes-de-servico-2026/IS%20N%20016.pdf",
    ),
    "GO": (
        "Portarias 170, 55 e 209/2026 (interação pendente)",
        "https://legisla.casacivil.go.gov.br/pesquisa_ato_infralegal/detran/20407",
    ),
    "MA": (
        "Portarias 1139/2025 e 141/2026",
        "https://www.detran.ma.gov.br/inicio/paginas/Portarias.xhtml",
    ),
    "MT": (
        "Portaria 042/2026",
        "https://www.detran.mt.gov.br/documents/d/detran/portaria-n-042-2026-gp-detran-mt-pdf",
    ),
    "MS": (
        "Norma estadual ainda não localizada",
        "https://www.detran.ms.gov.br/detran-ms-orienta-instrutores-de-transito-sobre-credenciamento-e-renovacao-anual/",
    ),
    "MG": (
        "Portaria 0129/2026 citada em serviço oficial",
        "https://www.mg.gov.br/servico/autorizar-instrutores-de-transito-autonomos",
    ),
    "PA": (
        "Norma de instrutor ainda não localizada",
        "https://www.detran.pa.gov.br/habilitacao/autorizacao-exame-pratico-veicular",
    ),
    "PB": (
        "Boletim Detran-PB 12/02/2026 (comissão)",
        "https://detran.pb.gov.br/BOLETINS-DE-SERVICO/bis-001-detran-12-02-2026.pdf",
    ),
    "PR": (
        "Portaria 351/2026 citada pelo Detran-PR",
        "https://www.detran.pr.gov.br/Pagina/Instrutor-de-Transito-Autonomo",
    ),
    "PE": (
        "Portaria DETRAN/PE 1.408/2026",
        "https://www.detran.pe.gov.br/images/2026/PORTARIA_1408_2026___11_02_26___INSTRUTORES_AUTONOMOS.pdf",
    ),
    "PI": (
        "Edital de credenciamento 01/2026",
        "https://portal.pi.gov.br/detran/wp-content/uploads/sites/62/2026/02/EDITAL-Credenciamento-DETRANPI-01-2026-inst.-autonomos_com-data-para-documentaca.pdf",
    ),
    "RJ": (
        "Portaria 7.082/2026 citada pelo Detran-RJ",
        "https://detran.rj.gov.br/noticias/detran-rj-orienta-instrutores-autonomos-a-acompanharem-processos-de-credenciamento-pelo-sei-rj.html",
    ),
    "RN": (
        "Portal Detran-RN cita instrutor autônomo; norma estadual pendente",
        "https://portal.detran.rn.gov.br/servicos/habilitacao/primeirahabilitacao",
    ),
    "RS": (
        "Portaria DETRAN/RS 99/2026",
        "https://publicacoeslegais.detran.rs.gov.br/portaria-detran-rs-n-99-2026",
    ),
    "RO": ("Portaria 454/2026", "https://diof.ro.gov.br/data/uploads/2026/02/DOE-25-02-2026.pdf"),
    "RR": (
        "Ato em DOE/RR a identificar",
        "https://api.transparencia.rr.gov.br/storage/legislacoes/9e80c6d6-5944-4401-943c-1100f9ff97f3.pdf",
    ),
    "SC": (
        "Portarias DETRAN/SC 125 e 275/2026",
        "https://mtsp.detran.sc.gov.br/portarias_web/uploads/portarias/2026/1769460523_Portaria%20125_26%20-%20Instrutores%20Aut%C3%B4nomos.pdf",
    ),
    "SP": (
        "Norma estadual específica ainda não localizada",
        "https://detran.sp.gov.br/cnhpaulista/",
    ),
    "SE": (
        "Portaria DETRAN/SE 095/2026",
        "https://arquivos.detran.se.gov.br/Portaria_095_2026.pdf",
    ),
    "TO": ("Norma estadual em fonte primária ainda não localizada", ""),
}


class Command(BaseCommand):
    help = "Cadastra 27 análises preliminares como REVIEW_REQUIRED; nunca aprova UFs."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Efetivar a criação após inspeção")

    @transaction.atomic
    def handle(self, *args, **options):
        if len(EVIDENCE) != 27:
            raise CommandError("Inventário não contém exatamente 27 UFs.")
        units = {unit.code: unit for unit in FederativeUnit.objects.all()}
        missing = sorted(set(EVIDENCE) - units.keys())
        if missing:
            raise CommandError(f"Catálogo territorial incompleto: {', '.join(missing)}")
        existing = RegulatoryReadiness.objects.filter(
            provider_type=INSTRUCTOR_PROVIDER_TYPE,
            capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
        ).count()
        self.stdout.write(f"UFs=27 EXISTING_READINESS={existing} NEW_POSSIBLE={27 - existing}")
        if not options["apply"]:
            self.stdout.write("DRY_RUN=YES; use --apply para criar somente registros ausentes.")
            return
        created = 0
        for uf, (reference, url) in EVIDENCE.items():
            item, was_created = RegulatoryReadiness.objects.get_or_create(
                federative_unit=units[uf],
                provider_type=INSTRUCTOR_PROVIDER_TYPE,
                capability=INSTRUCTOR_PUBLICATION_CAPABILITY,
                defaults={
                    "status": RegulatoryReadiness.Status.REVIEW_REQUIRED,
                    "source_reference": reference,
                    "source_url": url,
                    "notes": (
                        "Triagem inicial sem confirmação humana de vigência. Consulte "
                        "docs/REGULATORY_READINESS_27_UFS.md; não publicar antes "
                        "da aprovação explícita."
                    ),
                },
            )
            if was_created:
                created += 1
                AuditEvent.objects.create(
                    action="territories.regulatory_readiness_research_seed",
                    target_type="RegulatoryReadiness",
                    target_id=item.id,
                    reason_code="INITIAL_RESEARCH",
                    metadata={"uf": uf, "status": item.status, "source_reference": reference},
                )
        self.stdout.write(f"CREATED_REVIEW_REQUIRED={created} APPROVED_BY_COMMAND=0")
