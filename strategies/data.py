"""Converts persisted Candle rows into pandas DataFrames for indicator and
pattern analysis, so that's the only place the ORM-to-DataFrame shape lives."""

import pandas as pd

from database.models.market_data import Candle

OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]


def candles_to_dataframe(candles: list[Candle]) -> pd.DataFrame:
    if not candles:
        return pd.DataFrame(columns=OHLCV_COLUMNS)

    df = pd.DataFrame(
        {
            "timestamp": [c.timestamp for c in candles],
            "open": [c.open for c in candles],
            "high": [c.high for c in candles],
            "low": [c.low for c in candles],
            "close": [c.close for c in candles],
            "volume": [c.volume for c in candles],
        }
    )
    return df.set_index("timestamp").sort_index()
