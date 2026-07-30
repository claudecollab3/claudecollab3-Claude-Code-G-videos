"""Volume, volatility, spread-widening, and basic manipulation heuristics,
used as pre-trade filters alongside strategy signals themselves."""

import pandas as pd

from strategies.indicators import atr as _atr


def is_volume_spike(df: pd.DataFrame, *, lookback: int = 20, multiple: float = 2.0) -> bool:
    if len(df) < lookback + 1 or "volume" not in df:
        return False
    avg_volume = df["volume"].iloc[-lookback - 1 : -1].mean()
    if avg_volume == 0:
        return False
    return bool(df["volume"].iloc[-1] > multiple * avg_volume)


def volatility_percentile(df: pd.DataFrame, *, period: int = 14, lookback: int = 100) -> float:
    """Where the latest ATR sits (0-100) relative to its recent history — a
    rough, symbol-agnostic volatility-regime measure."""
    atr_series = _atr(df, period).dropna()
    if atr_series.empty:
        return 50.0
    recent = atr_series.iloc[-lookback:]
    return float((recent <= recent.iloc[-1]).mean() * 100)


def is_spread_widening(
    current_spread_points: float, average_spread_points: float, *, multiple: float = 2.0
) -> bool:
    if average_spread_points <= 0:
        return False
    return current_spread_points > multiple * average_spread_points


def is_suspected_manipulation(df: pd.DataFrame, *, wick_body_ratio: float = 3.0) -> bool:
    """Flags an abnormally long-wicked candle with a tiny body relative to
    its range on a volume spike — a coarse proxy for stop hunts / spoofing-
    style price action, not a definitive detector."""
    if df.empty:
        return False
    last = df.iloc[-1]
    body = abs(last["close"] - last["open"])
    full_range = last["high"] - last["low"]
    if full_range == 0:
        return False
    wick = full_range - body
    return (wick / max(body, 1e-9)) > wick_body_ratio and is_volume_spike(df)
