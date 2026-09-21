from dataclasses import dataclass

from django.conf import settings

NOT_GRANTED = "NOT_GRANTED"
CONTROLLED_PILOT = "CONTROLLED_PILOT"
FULL_PRODUCTION = "FULL_PRODUCTION"
AUTHORIZATION_STATES = {NOT_GRANTED, CONTROLLED_PILOT, FULL_PRODUCTION}
INSTRUCTOR_REGISTRATION_DISABLED = "DISABLED"
INSTRUCTOR_REGISTRATION_PRODUCTION = "PRODUCTION"
INSTRUCTOR_REGISTRATION_STATES = {
    INSTRUCTOR_REGISTRATION_DISABLED,
    INSTRUCTOR_REGISTRATION_PRODUCTION,
}
INSTRUCTOR_REGISTRATION_CAPABILITIES = {
    "REAL_ACCOUNT_REGISTRATION",
    "REAL_PERSONAL_DATA",
    "REAL_INSTRUCTOR_REGISTRATION",
}


@dataclass(frozen=True)
class Capability:
    setting: str
    pilot_allowed: bool


CAPABILITIES = {
    "REAL_ACCOUNT_REGISTRATION": Capability("REAL_ACCOUNT_REGISTRATION", True),
    "REAL_PERSONAL_DATA": Capability("REAL_PERSONAL_DATA", True),
    "REAL_STUDENT_USE": Capability("REAL_STUDENT_USE", True),
    "REAL_INSTRUCTOR_REGISTRATION": Capability("REAL_INSTRUCTOR_REGISTRATION", True),
    "REAL_MARKETPLACE_SEARCH": Capability("REAL_MARKETPLACE_SEARCH", True),
    "REAL_WHATSAPP_CONTACT": Capability("REAL_WHATSAPP_CONTACT", True),
    "REAL_MARKETPLACE_ANALYTICS": Capability("REAL_MARKETPLACE_ANALYTICS", True),
    "REAL_DOCUMENT_UPLOADS": Capability("REAL_DOCUMENT_UPLOADS", False),
    "REAL_AUTOMATIC_PUBLICATION": Capability("REAL_AUTOMATIC_PUBLICATION", False),
    "REAL_PAYMENTS": Capability("REAL_PAYMENTS", False),
    "REAL_PRO_BILLING": Capability("REAL_PRO_BILLING", False),
}


def authorization_state() -> str:
    return getattr(settings, "REAL_PRODUCTION_AUTHORIZATION", NOT_GRANTED)


def configured(name: str) -> bool:
    return bool(getattr(settings, CAPABILITIES[name].setting, False))


def instructor_registration_mode() -> str:
    return getattr(settings, "INSTRUCTOR_REGISTRATION_MODE", INSTRUCTOR_REGISTRATION_DISABLED)


def enabled(name: str) -> bool:
    if (
        name in INSTRUCTOR_REGISTRATION_CAPABILITIES
        and instructor_registration_mode() == INSTRUCTOR_REGISTRATION_PRODUCTION
    ):
        return configured(name)
    state = authorization_state()
    capability = CAPABILITIES[name]
    if state == NOT_GRANTED:
        return False
    if state == CONTROLLED_PILOT:
        return capability.pilot_allowed and configured(name)
    return state == FULL_PRODUCTION and configured(name)


def configuration_errors() -> list[str]:
    state = authorization_state()
    registration_mode = instructor_registration_mode()
    errors = []
    if state not in AUTHORIZATION_STATES:
        return ["REAL_PRODUCTION_AUTHORIZATION_INVALID"]
    if registration_mode not in INSTRUCTOR_REGISTRATION_STATES:
        errors.append("INSTRUCTOR_REGISTRATION_MODE_INVALID")
    if registration_mode == INSTRUCTOR_REGISTRATION_PRODUCTION:
        errors.extend(
            f"{name}_REQUIRED_FOR_INSTRUCTOR_PRODUCTION"
            for name in sorted(INSTRUCTOR_REGISTRATION_CAPABILITIES)
            if not configured(name)
        )
    globally_authorized = set(CAPABILITIES)
    if registration_mode == INSTRUCTOR_REGISTRATION_PRODUCTION:
        globally_authorized -= INSTRUCTOR_REGISTRATION_CAPABILITIES
    if state == NOT_GRANTED and any(configured(name) for name in globally_authorized):
        errors.append("CAPABILITY_ENABLED_WITHOUT_AUTHORIZATION")
    if state == CONTROLLED_PILOT:
        errors.extend(
            f"{name}_FORBIDDEN_IN_CONTROLLED_PILOT"
            for name, capability in CAPABILITIES.items()
            if not capability.pilot_allowed and configured(name)
        )
    return errors
