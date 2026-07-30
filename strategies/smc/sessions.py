"""Trading session windows and ICT "kill zones", in UTC."""

from dataclasses import dataclass
from datetime import datetime, time


@dataclass(frozen=True)
class SessionWindow:
    name: str
    start: time
    end: time


SESSIONS: tuple[SessionWindow, ...] = (
    SessionWindow("sydney", time(21, 0), time(6, 0)),
    SessionWindow("tokyo", time(0, 0), time(9, 0)),
    SessionWindow("london", time(7, 0), time(16, 0)),
    SessionWindow("new_york", time(12, 0), time(21, 0)),
)

KILL_ZONES: tuple[SessionWindow, ...] = (
    SessionWindow("london_open_killzone", time(7, 0), time(10, 0)),
    SessionWindow("new_york_open_killzone", time(12, 0), time(15, 0)),
)


def _in_window(t: time, window: SessionWindow) -> bool:
    if window.start <= window.end:
        return window.start <= t <= window.end
    return t >= window.start or t <= window.end


def active_sessions(timestamp: datetime) -> list[str]:
    t = timestamp.time()
    return [s.name for s in SESSIONS if _in_window(t, s)]


def is_kill_zone(timestamp: datetime) -> bool:
    t = timestamp.time()
    return any(_in_window(t, kz) for kz in KILL_ZONES)
