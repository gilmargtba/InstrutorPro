from decimal import Decimal

from django.db import migrations


FREE = {
    "PUBLIC_PROFILE": "Perfil público",
    "WHATSAPP_CONTACT": "Contato pelo WhatsApp",
    "BASIC_ANALYTICS": "Estatísticas básicas",
}
PRO = {
    "ADVANCED_ANALYTICS": "Estatísticas avançadas",
    "CALENDAR": "Agenda profissional",
    "EXTRA_PHOTOS": "Fotos adicionais",
    "MULTIPLE_VEHICLES": "Múltiplos veículos",
    "FEATURED_PLACEMENT": "Posicionamento em destaque",
    "LEAD_MANAGEMENT": "Gestão de contatos",
    "DEMAND_INSIGHTS": "Inteligência de demanda",
}


def seed(apps, schema_editor):
    Plan = apps.get_model("marketplace", "Plan")
    Entitlement = apps.get_model("marketplace", "Entitlement")
    PlanEntitlement = apps.get_model("marketplace", "PlanEntitlement")
    free, _ = Plan.objects.get_or_create(code="FREE", defaults={"name": "Free", "description": "Fundação gratuita do marketplace.", "status": "ACTIVE", "billing_interval": "NONE", "price_amount": Decimal("0"), "display_order": 10, "is_public": True})
    pro, _ = Plan.objects.get_or_create(code="PRO", defaults={"name": "Pro", "description": "Estrutura preparada; oferta comercial ainda não aprovada.", "status": "DRAFT", "billing_interval": "MONTHLY", "price_amount": None, "display_order": 20, "is_public": False})
    for plan, values in ((free, FREE), (pro, PRO)):
        for code, name in values.items():
            entitlement, _ = Entitlement.objects.get_or_create(code=code, defaults={"name": name})
            PlanEntitlement.objects.get_or_create(plan=plan, entitlement=entitlement)


class Migration(migrations.Migration):
    dependencies = [("marketplace", "0007_saas_foundation")]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
