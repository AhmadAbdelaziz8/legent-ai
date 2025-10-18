#!/bin/bash

echo "🔧 Fixing VNC Connection Configuration..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Rebuild and start services
echo "Rebuilding and starting services..."
docker-compose up --build -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

# Check VNC service status
echo "Checking VNC service status..."
curl -s http://localhost:8000/vnc/status | jq .

# Check if noVNC is accessible
echo "Checking noVNC accessibility..."
curl -s -I http://localhost:8080 | head -1

echo "✅ VNC connection should now work at http://localhost:8080"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "🖥️  VNC Desktop: http://localhost:8080"


