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
            "active": False,
            "lat0": 42.2807,
            "lon0": -83.7429,
            "yaw0_deg": 118.0,
            "size_m": 100.0,
        },
    }


def draw_tracks(frame_bgr, tracks: list[dict]) -> None:
    for trk in tracks:
        bbox = trk.get("bbox", [])
        if len(bbox) != 4:
            continue
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cls = trk.get("cls", "obj")
        conf = trk.get("conf", 0.0)
        trk_id = trk.get("id", -1)
        label = f"{cls} {conf:.2f} #{trk_id}"

        cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (0, 220, 0), 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame_bgr, (x1, y1 - th - 6), (x1 + tw + 4, y1), (0, 220, 0), -1)
        cv2.putText(
            frame_bgr,
            label,
            (x1 + 2, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )


def open_capture(video_source: str | None, cam_index: int) -> cv2.VideoCapture:
    if video_source:
        return cv2.VideoCapture(video_source)

    # On Windows, DirectShow is often more reliable for virtual cams.
    if sys.platform.startswith("win"):
        cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        if cap.isOpened():
            return cap
    return cv2.VideoCapture(cam_index)


def maybe_resize(frame_bgr, target_width: int | None):
    if not target_width:
        return frame_bgr
    h, w = frame_bgr.shape[:2]
    if w <= 0 or h <= 0 or w == target_width:
        return frame_bgr
    scale = target_width / float(w)
    new_h = max(1, int(h * scale))
    return cv2.resize(frame_bgr, (target_width, new_h), interpolation=cv2.INTER_AREA)


async def run(
    ws_url: str,
    cam_index: int,
    fps: int,
    video_source: str | None,
    resize_width: int | None,
    jpeg_quality: int,
) -> None:
    cap = open_capture(video_source, cam_index)
    if not cap.isOpened():
        source = video_source if video_source else f"camera index {cam_index}"
        raise RuntimeError(f"Failed to open {source}")

    limiter = FPSLimiter(fps)
    frame_id = 0

    try:
        async with websockets.connect(ws_url, max_size=4 * 1024 * 1024) as ws:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = maybe_resize(frame, resize_width)
                jpeg_b64 = encode_jpeg_b64(frame, quality=jpeg_quality)
                msg = build_message(frame_id, jpeg_b64)
                await ws.send(json_dumps(msg))
                resp = await ws.recv()
                data = json_loads(resp)
                tracks = data.get("tracks", [])
                draw_tracks(frame, tracks)
                cv2.imshow("Drone Tracker (phone cam)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                frame_id += 1
                limiter.sleep()
    finally:
        cap.release()
        cv2.destroyAllWindows()


def json_dumps(obj: dict) -> str:
    import json

    return json.dumps(obj, separators=(",", ":"))


def json_loads(text: str) -> dict:
    import json

    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ws", required=True, help="ws://host:port/ws")
    parser.add_argument("--cam", type=int, default=0)
    parser.add_argument("--video", help="Video path/URL (e.g., DroidCam http://IP:4747/video)")
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--resize", type=int, help="Resize width (e.g., 640) to reduce latency")
    parser.add_argument("--jpeg-quality", type=int, default=75, help="JPEG quality 1-100 (lower = faster)")
    args = parser.parse_args()

    asyncio.run(run(args.ws, args.cam, args.fps, args.video, args.resize, args.jpeg_quality))


if __name__ == "__main__":
    main()
