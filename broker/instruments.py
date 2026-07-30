"""Default supported instrument catalog: Gold, Bitcoin, major Forex pairs,
major indices, and crypto pairs, per the product requirements.

This is a static reference list, not a database table — broker adapters
remain the source of truth for what a given account can actually trade. It
gives the UI, AI symbol universe, and backtesting sensible, documented
defaults instead of a hardcoded list buried in each of those modules.
"""

import enum
from dataclasses import dataclass


class InstrumentCategory(str, enum.Enum):
    FOREX = "forex"
    METAL = "metal"
    CRYPTO = "crypto"
    INDEX = "index"


@dataclass(frozen=True)
class Instrument:
    symbol: str
    category: InstrumentCategory
    description: str


DEFAULT_INSTRUMENTS: tuple[Instrument, ...] = (
    Instrument("XAUUSD", InstrumentCategory.METAL, "Gold vs US Dollar"),
    Instrument("BTCUSD", InstrumentCategory.CRYPTO, "Bitcoin vs US Dollar"),
    Instrument("ETHUSD", InstrumentCategory.CRYPTO, "Ethereum vs US Dollar"),
    Instrument("EURUSD", InstrumentCategory.FOREX, "Euro vs US Dollar"),
    Instrument("GBPUSD", InstrumentCategory.FOREX, "British Pound vs US Dollar"),
    Instrument("USDJPY", InstrumentCategory.FOREX, "US Dollar vs Japanese Yen"),
    Instrument("USDCHF", InstrumentCategory.FOREX, "US Dollar vs Swiss Franc"),
    Instrument("AUDUSD", InstrumentCategory.FOREX, "Australian Dollar vs US Dollar"),
    Instrument("USDCAD", InstrumentCategory.FOREX, "US Dollar vs Canadian Dollar"),
    Instrument("NZDUSD", InstrumentCategory.FOREX, "New Zealand Dollar vs US Dollar"),
    Instrument("US30", InstrumentCategory.INDEX, "Dow Jones Industrial Average"),
    Instrument("US500", InstrumentCategory.INDEX, "S&P 500"),
    Instrument("NAS100", InstrumentCategory.INDEX, "Nasdaq 100"),
    Instrument("GER40", InstrumentCategory.INDEX, "DAX 40"),
)


def get_instrument(symbol: str) -> Instrument | None:
    return next((i for i in DEFAULT_INSTRUMENTS if i.symbol == symbol.upper()), None)
