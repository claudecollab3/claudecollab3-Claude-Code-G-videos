from pydantic import BaseModel


class StrategyResponse(BaseModel):
    name: str
    enabled: bool


class StrategyToggleRequest(BaseModel):
    enabled: bool
