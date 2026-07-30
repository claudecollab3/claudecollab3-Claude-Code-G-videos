"""TOTP-based two-factor authentication (RFC 6238) via pyotp."""

import pyotp

from config import get_settings


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_provisioning_uri(*, secret: str, account_email: str) -> str:
    settings = get_settings()
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_email, issuer_name=settings.two_factor_issuer
    )


def verify_totp_code(*, secret: str, code: str) -> bool:
    return pyotp.totp.TOTP(secret).verify(code, valid_window=1)
