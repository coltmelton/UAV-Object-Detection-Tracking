#!/usr/bin/env bash
set -euo pipefail

HOST_ADDR="${1:-0.0.0.0}"
PORT="${2:-8765}"

python src/tracker_server.py --host "$HOST_ADDR" --port "$PORT"
