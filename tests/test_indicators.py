import numpy as np
import pandas as pd

from strategies.indicators import adx, atr, bollinger_bands, ema, macd, rsi, sma, supertrend, vwap


def _make_ohlcv(closes: list[float], volumes: list[float] | None = None) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(closes), freq="h")
    closes_arr = np.array(closes)
    return pd.DataFrame(
        {
            "open": closes_arr,
            "high": closes_arr * 1.001,
            "low": closes_arr * 0.999,
            "close": closes_arr,
            "volume": volumes or [100.0] * len(closes),
        },
        index=index,
    )


def test_ema_converges_to_constant_price():
    df = _make_ohlcv([1.1000] * 50)
    result = ema(df["close"], period=10)
    assert abs(result.iloc[-1] - 1.1000) < 1e-9


def test_sma_matches_manual_average():
    df = _make_ohlcv([1.0, 2.0, 3.0, 4.0, 5.0])
    result = sma(df["close"], period=3)
    assert result.iloc[-1] == (3.0 + 4.0 + 5.0) / 3


def test_rsi_is_bounded_and_high_for_uptrend():
    closes = [1.0 + i * 0.01 for i in range(40)]
    df = _make_ohlcv(closes)
    result = rsi(df["close"], period=14).dropna()
    assert (result >= 0).all() and (result <= 100).all()
    assert result.iloc[-1] > 60  # steady uptrend -> high RSI


def test_macd_histogram_is_difference_of_lines():
    df = _make_ohlcv([1.0 + np.sin(i / 5) * 0.05 for i in range(60)])
    macd_line, signal_line, histogram = macd(df["close"])
    diff = (macd_line - signal_line - histogram).dropna()
    assert (diff.abs() < 1e-9).all()


def test_atr_is_non_negative():
    df = _make_ohlcv([1.0 + np.sin(i / 3) * 0.02 for i in range(40)])
    result = atr(df, period=14).dropna()
    assert (result >= 0).all()


def test_bollinger_bands_ordering():
    df = _make_ohlcv([1.0 + np.sin(i / 4) * 0.03 for i in range(60)])
    upper, mid, lower = bollinger_bands(df["close"], period=20)
    valid = upper.notna() & mid.notna() & lower.notna()
    assert (upper[valid] >= mid[valid]).all()
    assert (mid[valid] >= lower[valid]).all()


def test_adx_is_bounded():
    df = _make_ohlcv([1.0 + i * 0.01 for i in range(60)])
    result = adx(df, period=14).dropna()
    assert (result >= 0).all() and (result <= 100).all()


def test_supertrend_flags_uptrend():
    df = _make_ohlcv([1.0 + i * 0.02 for i in range(60)])
    result = supertrend(df, period=10, multiplier=3.0)
    assert result["trend"].iloc[-1] == 1
    assert result["supertrend"].iloc[-1] < df["close"].iloc[-1]


def test_vwap_within_price_range():
    df = _make_ohlcv([1.0 + np.sin(i / 5) * 0.02 for i in range(30)], volumes=[100.0] * 30)
    result = vwap(df)
    assert result.iloc[-1] > df["low"].min()
    assert result.iloc[-1] < df["high"].max()
