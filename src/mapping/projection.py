from __future__ import annotations

import math
from typing import Optional, Tuple


def pixel_to_bearing(
    u: float,
    v: float,
    w: int,
    h: int,
    hfov_deg: float,
    vfov_deg: float,
) -> Tuple[float, float]:
    """
    Convert pixel coordinates to camera-relative bearing angles.
    Returns (azimuth_deg, elevation_deg). Positive azimuth is left, positive elevation is up.
    """
    if w <= 0 or h <= 0:
        raise ValueError("Image width/height must be positive")
    x = (u - (w * 0.5)) / (w * 0.5)
    y = (v - (h * 0.5)) / (h * 0.5)
    azimuth = x * (hfov_deg * 0.5)
    elevation = -y * (vfov_deg * 0.5)
    return azimuth, elevation


def bearing_to_ground_xy(
    azimuth_deg: float,
    elevation_deg: float,
    alt_m: float,
    gimbal_pitch_deg: float,
    yaw_deg: float,
    yaw0_deg: float,
    gimbal_yaw_deg: float = 0.0,
) -> Optional[Tuple[float, float]]:
    """
    Project a camera bearing to a flat ground plane.
    Returns (x, y) in meters in the map session frame (+x forward from yaw0, +y left).
    """
    total_elev_deg = elevation_deg + gimbal_pitch_deg
    if total_elev_deg >= -1e-3:
        return None

    total_az_deg = yaw_deg + gimbal_yaw_deg + azimuth_deg
    elev_rad = math.radians(total_elev_deg)
    ground_dist = alt_m / math.tan(-elev_rad)

    heading_rad = math.radians(total_az_deg - yaw0_deg)
    x = ground_dist * math.cos(heading_rad)
    y = ground_dist * math.sin(heading_rad)
    return x, y
