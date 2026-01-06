import base64
from typing import Optional

import cv2
import numpy as np


def encode_jpeg_b64(frame_bgr: np.ndarray, quality: int = 85) -> str:
    encode_params = [int(cv2.IMWRITE_JPEG_QUALITY), int(quality)]
    ok, buf = cv2.imencode(".jpg", frame_bgr, encode_params)
    if not ok:
        raise ValueError("Failed to encode frame as JPEG")
    return base64.b64encode(buf.tobytes()).decode("ascii")


def decode_jpeg_b64(jpeg_b64: str) -> np.ndarray:
    data = base64.b64decode(jpeg_b64)
    np_buf = np.frombuffer(data, dtype=np.uint8)
    frame = cv2.imdecode(np_buf, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode JPEG buffer")
    return frame
