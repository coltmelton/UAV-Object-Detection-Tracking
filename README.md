# Drone Tracker (Python)

## Run
```
cd tracker
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/tracker_server.py --host 0.0.0.0 --port 8765
```

## Test (webcam)
```
python scripts/test_sender_webcam.py --ws ws://127.0.0.1:8765/ws
```

## Test + live viewer (webcam)
```
python scripts/test_sender_viewer.py --ws ws://127.0.0.1:8765/ws --cam 0
```

## Test + live viewer (DroidCam IP stream)
```
python scripts/test_sender_viewer.py --ws ws://127.0.0.1:8765/ws --video http://PHONE_IP:4747/video
```

## Reduce latency (lower res + JPEG quality)
```
python scripts/test_sender_viewer.py --ws ws://127.0.0.1:8765/ws --video http://PHONE_IP:4747/video --resize 640 --jpeg-quality 60 --fps 6
```
