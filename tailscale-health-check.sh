#!/bin/bash

# Health check script for Tailscale connectivity
echo "🔍 Tailscale Health Check for PDF RAG Q&A System"
echo "================================================"

# Check if Tailscale is running
if ! command -v tailscale &> /dev/null; then
    echo "❌ Tailscale not found. Please install Tailscale first."
    exit 1
fi

# Get Tailscale status
echo "📡 Tailscale Status:"
tailscale status

# Get Tailscale IP
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null | head -n1)
if [ -z "$TAILSCALE_IP" ]; then
    echo "❌ Could not get Tailscale IP. Make sure Tailscale is connected."
    exit 1
else
    echo "✅ Tailscale IP: $TAILSCALE_IP"
fi

echo ""
echo "🏥 Service Health Checks:"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running"
    exit 1
else
    echo "✅ Docker is running"
fi

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker containers are running"
    
    # Test frontend accessibility
    if curl -s "http://localhost:3000" >/dev/null; then
        echo "✅ Frontend accessible on localhost:3000"
        if curl -s "http://$TAILSCALE_IP:3000" >/dev/null; then
            echo "✅ Frontend accessible via Tailscale: http://$TAILSCALE_IP:3000"
        else
            echo "❌ Frontend not accessible via Tailscale"
        fi
    else
        echo "❌ Frontend not accessible on localhost"
    fi
    
    # Test backend accessibility
    if curl -s "http://localhost:8000" >/dev/null; then
        echo "✅ Backend accessible on localhost:8000"
        if curl -s "http://$TAILSCALE_IP:8000" >/dev/null; then
            echo "✅ Backend accessible via Tailscale: http://$TAILSCALE_IP:8000"
        else
            echo "❌ Backend not accessible via Tailscale"
        fi
    else
        echo "❌ Backend not accessible on localhost"
    fi
else
    echo "❌ No Docker containers are running. Run ./start-tailscale.sh first."
fi

echo ""
echo "🌐 Access URLs (if all services are healthy):"
echo "   Frontend: http://$TAILSCALE_IP:3000"
echo "   Backend API: http://$TAILSCALE_IP:8000"
echo "   API Docs: http://$TAILSCALE_IP:8000/docs"
