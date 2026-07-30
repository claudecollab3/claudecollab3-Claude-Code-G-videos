"""Builds the right BrokerAdapter for a stored BrokerCredential."""

from authentication.vault import get_vault
from broker.adapter import BrokerAdapter
from broker.mt4.adapter import MT4BrokerAdapter
from broker.mt5.adapter import MT5BrokerAdapter
from broker.paper import PaperBrokerAdapter
from config import get_settings
from database.models.broker_credential import BrokerCredential, BrokerType


def build_adapter(credential: BrokerCredential) -> BrokerAdapter:
    if credential.broker_type == BrokerType.PAPER:
        return PaperBrokerAdapter()

    password = get_vault().decrypt(credential.encrypted_password)

    if credential.broker_type == BrokerType.MT5:
        return MT5BrokerAdapter(login=credential.login, password=password, server=credential.server)

    if credential.broker_type == BrokerType.MT4:
        settings = get_settings()
        return MT4BrokerAdapter(
            host=settings.mt4_bridge_host,
            push_port=settings.mt4_bridge_port,
            pull_port=settings.mt4_bridge_port + 1,
        )

    raise ValueError(f"Unsupported broker type: {credential.broker_type}")
