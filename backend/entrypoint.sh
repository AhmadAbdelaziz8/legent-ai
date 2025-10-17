#!/bin/bash
set -e

# Start VNC services first
./scripts/start_all.sh
./scripts/novnc_startup.sh

echo "✨ VNC Desktop is ready!"
echo "➡️  Open http://localhost:8080 in your browser to access the desktop"

# Start FastAPI in the background
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Keep the container running
wait
