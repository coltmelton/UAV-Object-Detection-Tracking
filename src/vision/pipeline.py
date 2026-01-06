from __future__ import annotations

from typing import List, Optional

import numpy as np

from config import CAMERA_HFOV_DEG, CAMERA_VFOV_DEG
from mapping.local_map import clamp_to_map
from mapping.projection import bearing_to_ground_xy, pixel_to_bearing
from protocol import MapSession, Telemetry, Track
from vision.detector import YOLODetector
from vision.tracker import SimpleSORT


def run_pipeline(
    frame_bgr: np.ndarray,
    telemetry: Telemetry,
    map_session: MapSession,
    detector: Optional[YOLODetector],
    tracker: Optional[SimpleSORT],
) -> List[Track]:
    if detector is None or tracker is None:
        return []

    dets = detector.detect(frame_bgr)
    tracks = tracker.update(dets)

    h, w = frame_bgr.shape[:2]
    out: List[Track] = []
    for trk in tracks:
        x1, y1, x2, y2 = trk.bbox
        cx = (x1 + x2) * 0.5
        cy = (y1 + y2) * 0.5

        map_xy = None
        if map_session.active:
            az, el = pixel_to_bearing(cx, cy, w, h, CAMERA_HFOV_DEG, CAMERA_VFOV_DEG)
            ground_xy = bearing_to_ground_xy(
                az,
                el,
                telemetry.alt_m,
                telemetry.gimbal_pitch_deg,
                telemetry.yaw_deg,
                map_session.yaw0_deg,
                telemetry.gimbal_yaw_deg,
            )
            if ground_xy is not None:
                gx, gy = clamp_to_map(ground_xy[0], ground_xy[1], map_session.size_m)
                map_xy = [gx, gy]

        out.append(
            Track(
                id=trk.id,
                cls=trk.cls,
                conf=trk.conf,
                bbox=[float(x1), float(y1), float(x2), float(y2)],
                map_xy_m=map_xy,
            )
        )

    return out
