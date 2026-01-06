param(
  [string]$HostAddr = "0.0.0.0",
  [int]$Port = 8765
)

python src/tracker_server.py --host $HostAddr --port $Port
