from django.core.management.base import BaseCommand
from django.db import transaction

from apps.territories.models import Country, FederativeUnit

UFS = {
    "AC": ("Acre", "12"),
    "AL": ("Alagoas", "27"),
    "AP": ("Amapá", "16"),
    "AM": ("Amazonas", "13"),
    "BA": ("Bahia", "29"),
    "CE": ("Ceará", "23"),
    "DF": ("Distrito Federal", "53"),
    "ES": ("Espírito Santo", "32"),
    "GO": ("Goiás", "52"),
    "MA": ("Maranhão", "21"),
    "MT": ("Mato Grosso", "51"),
    "MS": ("Mato Grosso do Sul", "50"),
    "MG": ("Minas Gerais", "31"),
    "PA": ("Pará", "15"),
    "PB": ("Paraíba", "25"),
    "PR": ("Paraná", "41"),
    "PE": ("Pernambuco", "26"),
    "PI": ("Piauí", "22"),
    "RJ": ("Rio de Janeiro", "33"),
    "RN": ("Rio Grande do Norte", "24"),
    "RS": ("Rio Grande do Sul", "43"),
    "RO": ("Rondônia", "11"),
    "RR": ("Roraima", "14"),
    "SC": ("Santa Catarina", "42"),
    "SP": ("São Paulo", "35"),
    "SE": ("Sergipe", "28"),
    "TO": ("Tocantins", "17"),
}
FIRST_WAVE = {"RS", "SC", "SP", "RJ", "ES"}


class Command(BaseCommand):
    help = "Cria ou atualiza o catálogo territorial nacional sem dados pessoais."

    @transaction.atomic
    def handle(self, *args, **options):
        country, _ = Country.objects.update_or_create(code="BR", defaults={"name": "Brasil"})
        for code, (name, ibge_code) in UFS.items():
            FederativeUnit.objects.update_or_create(
                code=code,
                defaults={
                    "country": country,
                    "name": name,
                    "ibge_code": ibge_code,
                    "commercial_status": "FIRST_WAVE" if code in FIRST_WAVE else "PREPARATION",
                },
            )
        self.stdout.write(self.style.SUCCESS("Catálogo territorial sincronizado: Brasil e 27 UFs."))
