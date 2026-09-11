import hashlib
from urllib.parse import quote

from django.conf import settings
from django.utils import timezone

from .models import DataMode, MarketplaceEvent


def normalize_brazilian_whatsapp(value: str) -> str:
    digits = "".join(character for character in value if character.isdigit())
    if digits.startswith("55"):
        digits = digits[2:]
    if len(digits) not in {10, 11} or digits[0] == "0" or digits[:2].endswith("0"):
        raise ValueError("Informe um WhatsApp brasileiro válido com DDD.")
    return f"+55{digits}"


def anonymous_session_hash(request) -> str:
    if not request.session.session_key:
        request.session.create()
    material = f"{settings.SECRET_KEY}:{request.session.session_key}".encode()
    return hashlib.sha256(material).hexdigest()


def record_marketplace_event(
    *, request, event_type, instructor=None, source="", category="", city="", uf=""
):
    now = timezone.now()
    bucket = now.replace(minute=0, second=0, microsecond=0)
    event, created = MarketplaceEvent.objects.get_or_create(
        event_type=event_type,
        instructor=instructor,
        session_hash=anonymous_session_hash(request),
        dedupe_bucket=bucket,
        defaults={
            "source": source[:40],
            "category": category[:8],
            "city": city[:100],
            "uf": uf[:2],
            "data_mode": DataMode.SYNTHETIC
            if instructor is None or instructor.is_demo
            else DataMode.REAL,
        },
    )
    return event, created


def whatsapp_destination(*, instructor, category: str) -> str:
    channel = instructor.contact_channel
    message = (
        "Olá! Encontrei seu perfil no InstrutorProCNH e gostaria de informações "
        f"sobre aulas para categoria {category}."
    )
    return f"https://wa.me/{channel.whatsapp_e164.removeprefix('+')}?text={quote(message)}"
