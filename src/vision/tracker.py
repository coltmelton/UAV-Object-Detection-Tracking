from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from config import TRACK_IOU_THRESH, TRACK_MAX_AGE
from vision.detector import Detection


def iou(a: list[float], b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    if union <= 0.0:
        return 0.0
    return inter / union


@dataclass
class Track:
    id: int
    bbox: list[float]
    cls: str
    conf: float
    age: int = 0
    hits: int = 1


class SimpleSORT:
    def __init__(self, iou_thresh: float = TRACK_IOU_THRESH, max_age: int = TRACK_MAX_AGE):
        self._iou_thresh = iou_thresh
        self._max_age = max_age
        self._next_id = 1
        self._tracks: List[Track] = []

    def _match(self, dets: List[Detection]) -> List[tuple[int, int]]:
        matches: List[tuple[int, int]] = []
        used_dets = set()
        for t_idx, track in enumerate(self._tracks):
            best_iou = 0.0
            best_d = None
            for d_idx, det in enumerate(dets):
                if d_idx in used_dets:
                    continue
                score = iou(track.bbox, det.bbox)
                if score > best_iou:
                    best_iou = score
                    best_d = d_idx
            if best_d is not None and best_iou >= self._iou_thresh:
                matches.append((t_idx, best_d))
                used_dets.add(best_d)
        return matches

    def update(self, dets: List[Detection]) -> List[Track]:
        matches = self._match(dets)
        matched_tracks = {t for t, _ in matches}
        matched_dets = {d for _, d in matches}

        for t_idx, d_idx in matches:
            det = dets[d_idx]
            track = self._tracks[t_idx]
            track.bbox = det.bbox
            track.cls = det.cls
            track.conf = det.conf
            track.age = 0
            track.hits += 1

        for idx, track in enumerate(list(self._tracks)):
            if idx not in matched_tracks:
                track.age += 1

        self._tracks = [t for t in self._tracks if t.age <= self._max_age]

        for d_idx, det in enumerate(dets):
            if d_idx in matched_dets:
                continue
            self._tracks.append(
                Track(
                    id=self._next_id,
                    bbox=det.bbox,
                    cls=det.cls,
                    conf=det.conf,
                )
            )
            self._next_id += 1

        return list(self._tracks)
