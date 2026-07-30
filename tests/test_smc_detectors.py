from datetime import UTC, datetime

import pandas as pd

from strategies.smc.fair_value_gap import detect_fair_value_gaps
from strategies.smc.levels import cluster_levels
from strategies.smc.liquidity import detect_liquidity_sweeps
from strategies.smc.order_blocks import detect_order_blocks
from strategies.smc.sessions import is_kill_zone
from strategies.smc.structure import StructureEventKind, detect_structure_events, find_swing_points


def _df_from_ohlc(
    rows: list[tuple[float, float, float, float]], volume: float = 100.0
) -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=len(rows), freq="h")
    return pd.DataFrame(
        {
            "open": [r[0] for r in rows],
            "high": [r[1] for r in rows],
            "low": [r[2] for r in rows],
            "close": [r[3] for r in rows],
            "volume": [volume] * len(rows),
        },
        index=index,
    )


def test_find_swing_points_detects_local_extremes():
    # A clean V shape: down then up, with a single low pivot in the middle.
    closes = [10, 9, 8, 7, 6, 7, 8, 9, 10]
    rows = [(c, c + 0.1, c - 0.1, c) for c in closes]
    df = _df_from_ohlc(rows)

    swings = find_swing_points(df, lookback=2)
    lows = [s for s in swings if not s.is_high]
    assert any(abs(s.price - 5.9) < 0.2 for s in lows)


def test_detect_structure_events_finds_bullish_choch_after_downtrend():
    # Downtrend (lower highs, lower lows), then a rally that's confirmed as
    # a swing high above the last swing high -> registers as a bullish CHoCH.
    closes = [10, 9, 9.5, 8, 8.5, 7, 7.5, 6, 8, 6.5, 8.2]
    rows = [(c, c + 0.1, c - 0.1, c) for c in closes]
    df = _df_from_ohlc(rows)

    events = detect_structure_events(df, lookback=1)
    assert any(e.kind == StructureEventKind.CHOCH_BULLISH for e in events)


def test_detect_order_blocks_finds_bullish_block_before_displacement():
    # A down candle followed by a large up-displacement candle.
    rows = [
        (1.10, 1.101, 1.095, 1.098),  # down candle (order block candidate)
        (1.098, 1.150, 1.097, 1.149),  # strong bullish displacement
    ]
    # pad with flat candles so ATR has data
    flat = [(1.10, 1.101, 1.099, 1.10)] * 20
    df = _df_from_ohlc(flat + rows)

    blocks = detect_order_blocks(df, displacement_atr_multiple=1.0, atr_period=14)
    assert any(b.bullish for b in blocks)


def test_detect_fair_value_gaps_finds_bullish_gap():
    rows = [
        (1.10, 1.105, 1.099, 1.104),  # candle 1: high = 1.105
        (1.104, 1.120, 1.103, 1.118),  # displacement candle
        (1.118, 1.125, 1.110, 1.120),  # candle 3: low = 1.110 > candle1 high (1.105)
    ]
    df = _df_from_ohlc(rows)
    gaps = detect_fair_value_gaps(df)
    assert len(gaps) == 1
    assert gaps[0].bullish is True
    assert gaps[0].bottom == 1.105
    assert gaps[0].top == 1.110


def test_detect_liquidity_sweeps_finds_bullish_sweep():
    closes = [10, 9, 8, 7, 6, 7, 8]
    rows = [(c, c + 0.1, c - 0.1, c) for c in closes]
    df = _df_from_ohlc(rows)
    swings = find_swing_points(df, lookback=1)

    # Add a bar that wicks below the swept low but closes back above it.
    sweep_row = pd.DataFrame(
        {"open": [8.5], "high": [8.6], "low": [5.5], "close": [8.4], "volume": [100.0]},
        index=[df.index[-1] + pd.Timedelta(hours=1)],
    )
    df_with_sweep = pd.concat([df, sweep_row])

    sweeps = detect_liquidity_sweeps(df_with_sweep, swings)
    assert any(s.bullish for s in sweeps)


def test_cluster_levels_groups_nearby_swings():
    from strategies.smc.structure import SwingPoint

    swings = [
        SwingPoint(timestamp=datetime(2026, 1, 1, tzinfo=UTC), price=1.1000, is_high=True),
        SwingPoint(timestamp=datetime(2026, 1, 2, tzinfo=UTC), price=1.1001, is_high=True),
        SwingPoint(timestamp=datetime(2026, 1, 3, tzinfo=UTC), price=1.0500, is_high=False),
    ]
    levels = cluster_levels(swings, tolerance_pct=0.001)
    resistance_levels = [lv for lv in levels if lv.is_resistance]
    assert len(resistance_levels) == 1
    assert resistance_levels[0].touches == 2


def test_is_kill_zone_true_during_london_open():
    ts = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
    assert is_kill_zone(ts) is True


def test_is_kill_zone_false_outside_windows():
    ts = datetime(2026, 1, 1, 18, 0, tzinfo=UTC)
    assert is_kill_zone(ts) is False
