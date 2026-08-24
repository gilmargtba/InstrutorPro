SENSITIVE_KEYS = {"password", "token", "secret", "cpf", "document", "diagnosis"}


def redact_metadata(value):
    if not isinstance(value, dict):
        return {}
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else item for key, item in value.items()
    }
