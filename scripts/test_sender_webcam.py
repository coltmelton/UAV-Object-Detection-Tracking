import argparse
import asyncio
import os
import sys
import time

import cv2
import websockets

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from util.fps import FPSLimiter
from util.jpeg import encode_jpeg_b64


def build_message(frame_id: int, jpeg_b64: str) -> dict:
    t_ms = int(time.time() * 1000)
    return {
        "type": "frame",
        "t_ms": t_ms,
        "frame_id": frame_id,
        "jpeg_b64": jpeg_b64,
        "telemetry": {
            "lat": 42.2808,
            "lon": -83.7430,
            "alt_m": 35.2,
            "yaw_deg": 120.0,
            "gimbal_pitch_deg": -45.0,
            "gimbal_yaw_deg": 0.0,
        },
        "map_session": {
            "active": True,
            "lat0": 42.2807,
            "lon0": -83.7429,
            "yaw0_deg": 118.0,
            "size_m": 100.0,
        },
    }


async def run(ws_url: str, cam_index: int) -> None:
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError("Failed to open webcam")

    limiter = FPSLimiter(8)
    frame_id = 0

    async with websockets.connect(ws_url, max_size=4 * 1024 * 1024) as ws:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            jpeg_b64 = encode_jpeg_b64(frame)
            msg = build_message(frame_id, jpeg_b64)
            await ws.send(json_dumps(msg))
            await ws.recv()
            frame_id += 1
            limiter.sleep()

    cap.release()


def json_dumps(obj: dict) -> str:
    import json

    return json.dumps(obj, separators=(",", ":"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ws", required=True, help="ws://host:port/ws")
    parser.add_argument("--cam", type=int, default=0)
    args = parser.parse_args()

    asyncio.run(run(args.ws, args.cam))


if __name__ == "__main__":
    main()
