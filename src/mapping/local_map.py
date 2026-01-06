from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class MapSessionState:
    active: bool
    lat0: float
    lon0: float
    yaw0_deg: float
    size_m: float

    @classmethod
    def from_message(cls, msg) -> "MapSessionState":
        return cls(
            active=bool(msg.active),
            lat0=float(msg.lat0),
            lon0=float(msg.lon0),
            yaw0_deg=float(msg.yaw0_deg),
            size_m=float(msg.size_m),
        )


def clamp_to_map(x: float, y: float, size_m: float) -> Tuple[float, float]:
    half = size_m * 0.5
    x = max(-half, min(half, x))
    y = max(-half, min(half, y))
    return x, y
