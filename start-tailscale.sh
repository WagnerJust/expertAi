#!/bin/bash

# Script to start the application with Tailscale support
# This will build and run all services accessible via Tailscale

echo "🚀 Starting PDF RAG Q&A System with Tailscale support..."

# Get the Tailscale IP address
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null | head -n1)

if [ -z "$TAILSCALE_IP" ]; then
    echo "⚠️  Warning: Could not detect Tailscale IP. Make sure Tailscale is running."
    echo "You can still access the app via localhost or your local network IP."
else
    echo "📡 Tailscale IP detected: $TAILSCALE_IP"
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker compose down

# Build and start services
echo "🏗️  Building and starting services..."
docker compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
if [ ! -z "$TAILSCALE_IP" ]; then
    echo "   Frontend (Tailscale): http://$TAILSCALE_IP:3000"
fi
echo "   Backend API: http://localhost:8000"
if [ ! -z "$TAILSCALE_IP" ]; then
    echo "   Backend API (Tailscale): http://$TAILSCALE_IP:8000"
fi
echo "   Ollama Service: http://localhost:11434"
if [ ! -z "$TAILSCALE_IP" ]; then
    echo "   Ollama Service (Tailscale): http://$TAILSCALE_IP:11434"
fi
echo ""
echo "📋 To view logs: docker compose logs -f"
echo "🛑 To stop: docker compose down"
