import base64
import hashlib
import hmac
import re

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


class ProtectedIdentifierConfigurationError(RuntimeError):
    pass


def normalize_cpf(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 11 or digits == digits[0] * 11:
        raise ValueError("CPF inválido.")
    for size in (9, 10):
        total = sum(int(digits[index]) * (size + 1 - index) for index in range(size))
        check = (total * 10) % 11
        check = 0 if check == 10 else check
        if check != int(digits[size]):
            raise ValueError("CPF inválido.")
    return digits


def _fernet() -> Fernet:
    configured = settings.PII_FIELD_ENCRYPTION_KEY
    try:
        return Fernet(configured.encode("ascii"))
    except (ValueError, TypeError) as exc:
        raise ProtectedIdentifierConfigurationError(
            "A chave de proteção de dados pessoais não está configurada corretamente."
        ) from exc


def encrypt_identifier(value: str) -> str:
    return _fernet().encrypt(value.encode("ascii")).decode("ascii")


def decrypt_identifier(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode("ascii")).decode("ascii")
    except InvalidToken as exc:
        raise ProtectedIdentifierConfigurationError(
            "Não foi possível abrir o identificador protegido."
        ) from exc


def fingerprint_identifier(value: str) -> str:
    key = settings.PII_FINGERPRINT_KEY
    if len(key) < 32:
        raise ProtectedIdentifierConfigurationError(
            "A chave separada de índice cego não está configurada corretamente."
        )
    return hmac.new(key.encode(), value.encode("ascii"), hashlib.sha256).hexdigest()


def mask_cpf(last2: str) -> str:
    return f"***.***.***-{last2}" if last2 else ""


def generate_fernet_key() -> str:
    return base64.urlsafe_b64encode(__import__("os").urandom(32)).decode("ascii")
