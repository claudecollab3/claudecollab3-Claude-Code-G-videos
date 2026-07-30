"""Encrypted BrokerCredential secret helpers + reconnect-with-backoff."""

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from authentication.vault import get_vault
from broker.adapter import BrokerAdapter, BrokerConnectionError


def encrypt_broker_secret(plaintext: str) -> str:
    return get_vault().encrypt(plaintext)


def decrypt_broker_secret(ciphertext: str) -> str:
    return get_vault().decrypt(ciphertext)


@retry(
    retry=retry_if_exception_type(BrokerConnectionError),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    stop=stop_after_attempt(5),
    reraise=True,
)
async def connect_with_backoff(adapter: BrokerAdapter) -> None:
    """Connect an adapter, retrying transient failures with exponential
    backoff. Used for both the initial connection and reconnecting after an
    unexpected drop."""
    await adapter.connect()
