from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from ultralytics import YOLO

from config import CONF_THRESH


@dataclass
class Detection:
    cls: str
    conf: float
    bbox: list[float]


class YOLODetector:
    def __init__(self, model_path: str = "yolov8n.pt", conf_thresh: float = CONF_THRESH):
        self._model = YOLO(model_path)
        self._conf = conf_thresh

    def detect(self, frame_bgr: np.ndarray) -> List[Detection]:
        results = self._model.predict(frame_bgr, conf=self._conf, verbose=False)
        dets: List[Detection] = []
        if not results:
            return dets

        names = results[0].names
        boxes = results[0].boxes
        if boxes is None:
            return dets

        for box in boxes:
            cls_id = int(box.cls.item())
            cls_name = names.get(cls_id, str(cls_id))
            conf = float(box.conf.item())
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            dets.append(Detection(cls=cls_name, conf=conf, bbox=[x1, y1, x2, y2]))
        return dets
