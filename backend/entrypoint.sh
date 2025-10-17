#!/bin/bash
set -e

# AWS credentials will be mounted from host's ~/.aws directory
# Set AWS environment variables
export AWS_PROFILE=default
export AWS_DEFAULT_REGION=${AWS_REGION}

# Start VNC services first
./scripts/start_all.sh
./scripts/novnc_startup.sh

echo "✨ VNC Desktop is ready!"
echo "➡️  Open http://localhost:8080 in your browser to access the desktop"

# Start FastAPI in the background
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Keep the container running
wait