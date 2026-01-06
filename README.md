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
