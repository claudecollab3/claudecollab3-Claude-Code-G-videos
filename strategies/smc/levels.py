"""Support/Resistance and Supply/Demand zone helpers built on swing points:
nearby swing highs/lows are clustered into levels, and a level with more
touches is treated as stronger."""

from dataclasses import dataclass

from strategies.smc.structure import SwingPoint


@dataclass
class Level:
    price: float
    touches: int
    is_resistance: bool


def cluster_levels(swings: list[SwingPoint], *, tolerance_pct: float = 0.001) -> list[Level]:
    levels: list[Level] = []

    for swing in swings:
        matched = next(
            (
                lv
                for lv in levels
                if lv.is_resistance == swing.is_high
                and abs(lv.price - swing.price) / swing.price <= tolerance_pct
            ),
            None,
        )
        if matched is not None:
            matched.touches += 1
            matched.price = (matched.price + swing.price) / 2
        else:
            levels.append(Level(price=swing.price, touches=1, is_resistance=swing.is_high))

    return sorted(levels, key=lambda lv: lv.touches, reverse=True)
