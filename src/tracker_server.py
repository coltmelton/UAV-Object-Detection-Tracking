from __future__ import annotations

import argparse
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from protocol import FrameMessage, TracksMessage
from util.jpeg import decode_jpeg_b64
from util.logging import setup_logging
from vision.detector import YOLODetector
from vision.pipeline import run_pipeline
from vision.tracker import SimpleSORT


def now_ms() -> int:
    return int(time.time() * 1000)


app = FastAPI()
detector: YOLODetector | None = None
tracker: SimpleSORT | None = None


@app.on_event("startup")
async def _startup() -> None:
    global detector, tracker
    try:
        detector = YOLODetector()
        tracker = SimpleSORT()
    except Exception:
        detector = None
        tracker = None


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            msg = FrameMessage.model_validate_json(raw)
            frame_bgr = decode_jpeg_b64(msg.jpeg_b64)
            tracks = run_pipeline(frame_bgr, msg.telemetry, msg.map_session, detector, tracker)
            resp = TracksMessage(t_ms=now_ms(), frame_id=msg.frame_id, tracks=tracks)
            await websocket.send_text(resp.model_dump_json())
    except WebSocketDisconnect:
        return


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
