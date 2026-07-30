"""Feature engineering shared by every model in the ensemble.

`build_feature_vector` turns a `MarketContext` into a fixed-order numeric
dict so every model — however different its internals — sees the same
inputs. `FEATURE_NAMES` defines that fixed order; `feature_dict_to_vector`
converts the dict to the plain list scikit-learn/XGBoost/LightGBM expect.
"""

from strategies.base import MarketContext
from strategies.indicators import adx, atr, bollinger_bands, ema, macd, rsi
from strategies.smc.sessions import is_kill_zone

FEATURE_NAMES: tuple[str, ...] = (
    "h1_rsi",
    "h1_macd_hist",
    "h1_adx",
    "h1_atr_pct",
    "h1_bb_percent_b",
    "h1_ema_fast_slow_diff_pct",
    "h4_ema_fast_slow_diff_pct",
    "m15_rsi",
    "volume_ratio",
    "is_kill_zone",
)


def _volume_ratio(df) -> float:
    if len(df) < 21 or "volume" not in df:
        return 1.0
    avg = df["volume"].iloc[-21:-1].mean()
    if avg == 0:
        return 1.0
    return float(df["volume"].iloc[-1] / avg)


def build_feature_vector(context: MarketContext) -> dict[str, float]:
    features: dict[str, float] = dict.fromkeys(FEATURE_NAMES, 0.0)

    h1 = context.timeframes.get("H1")
    h4 = context.timeframes.get("H4")
    m15 = context.timeframes.get("M15")

    if h1 is not None and len(h1) >= 60:
        price = float(h1["close"].iloc[-1])
        features["h1_rsi"] = float(rsi(h1["close"], 14).iloc[-1])
        _, _, hist = macd(h1["close"])
        features["h1_macd_hist"] = float(hist.iloc[-1])
        features["h1_adx"] = float(adx(h1, 14).iloc[-1])

        atr_value = float(atr(h1, 14).iloc[-1])
        features["h1_atr_pct"] = (atr_value / price * 100) if price else 0.0

        upper, _, lower = bollinger_bands(h1["close"], 20)
        band_width = float(upper.iloc[-1] - lower.iloc[-1])
        features["h1_bb_percent_b"] = (
            (price - float(lower.iloc[-1])) / band_width if band_width else 0.5
        )

        fast = float(ema(h1["close"], 50).iloc[-1])
        slow = float(ema(h1["close"], 200).iloc[-1])
        features["h1_ema_fast_slow_diff_pct"] = ((fast - slow) / slow * 100) if slow else 0.0

        features["volume_ratio"] = _volume_ratio(h1)
        features["is_kill_zone"] = 1.0 if is_kill_zone(h1.index[-1]) else 0.0

    if h4 is not None and len(h4) >= 200:
        fast4 = float(ema(h4["close"], 50).iloc[-1])
        slow4 = float(ema(h4["close"], 200).iloc[-1])
        features["h4_ema_fast_slow_diff_pct"] = ((fast4 - slow4) / slow4 * 100) if slow4 else 0.0

    if m15 is not None and len(m15) >= 20:
        features["m15_rsi"] = float(rsi(m15["close"], 14).iloc[-1])

    return {name: (0.0 if value != value else value) for name, value in features.items()}


def feature_dict_to_vector(features: dict[str, float]) -> list[float]:
    return [features.get(name, 0.0) for name in FEATURE_NAMES]
