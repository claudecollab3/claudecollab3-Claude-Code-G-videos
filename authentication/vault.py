"""Symmetric encryption for broker credentials and API keys at rest.

Uses Fernet (AES-128-CBC + HMAC, via `cryptography`). The key comes from
`CREDENTIAL_ENCRYPTION_KEY` and must never be committed or logged. Generate
one with `Vault.generate_key()` and store it in a secrets manager / `.env`
(gitignored) — never hardcode it.
"""

from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

from config import get_settings


class VaultConfigurationError(RuntimeError):
    """Raised when CREDENTIAL_ENCRYPTION_KEY is missing or invalid."""


class VaultDecryptionError(RuntimeError):
    """Raised when a ciphertext cannot be decrypted (wrong key or tampering)."""


class Vault:
    def __init__(self, key: str):
        if not key:
            raise VaultConfigurationError(
                "CREDENTIAL_ENCRYPTION_KEY is not set. Generate one with "
                "Vault.generate_key() and set it in the environment before "
                "storing any broker credentials."
            )
        try:
            self._fernet = Fernet(key.encode("utf-8"))
        except (ValueError, TypeError) as exc:
            raise VaultConfigurationError(
                "CREDENTIAL_ENCRYPTION_KEY is not a valid Fernet key"
            ) from exc

    @staticmethod
    def generate_key() -> str:
        return Fernet.generate_key().decode("utf-8")

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise VaultDecryptionError(
                "Could not decrypt value: wrong key or corrupted data"
            ) from exc


@lru_cache
def get_vault() -> Vault:
    return Vault(get_settings().credential_encryption_key)
