from django.core.exceptions import ValidationError


def normalize_cnpj(value):
    return "".join(character for character in (value or "") if character.isdigit())


def _check_digit(digits, weights):
    remainder = sum(int(digit) * weight for digit, weight in zip(digits, weights, strict=True)) % 11
    return "0" if remainder < 2 else str(11 - remainder)


def validate_cnpj(value):
    digits = normalize_cnpj(value)
    if not digits:
        return
    if len(digits) != 14 or len(set(digits)) == 1:
        raise ValidationError("Informe um CNPJ válido.", code="invalid_cnpj")
    first = _check_digit(digits[:12], (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    second = _check_digit(digits[:12] + first, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))
    if digits[-2:] != first + second:
        raise ValidationError("Informe um CNPJ válido.", code="invalid_cnpj")
