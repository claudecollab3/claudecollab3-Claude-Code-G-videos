import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from broker.instruments import InstrumentCategory
from database.models.broker_credential import BrokerType


class BrokerCredentialCreateRequest(BaseModel):
    broker_type: BrokerType
    broker_name: str = Field(max_length=128)
    server: str = Field(default="", max_length=128)
    login: str = Field(default="", max_length=128)
    password: str = Field(default="", max_length=256)
    investor_password: str | None = Field(default=None, max_length=256)


class BrokerCredentialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    broker_type: BrokerType
    broker_name: str
    server: str
    login: str
    is_active: bool
    created_at: datetime


class AccountInfoResponse(BaseModel):
    login: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    currency: str
    leverage: int
    server: str


class InstrumentResponse(BaseModel):
    symbol: str
    category: InstrumentCategory
    description: str
