#!/bin/bash

# Setup ChromaDB Docker Container for Testing
# This script sets up a ChromaDB container for local development and testing

set -e

echo "🔧 Setting up ChromaDB Docker container..."

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Stop existing container if running
if docker ps -q -f name=chroma-test > /dev/null; then
    echo "🛑 Stopping existing ChromaDB container..."
    docker stop chroma-test
fi

# Remove existing container if exists
if docker ps -aq -f name=chroma-test > /dev/null; then
    echo "🗑️  Removing existing ChromaDB container..."
    docker rm chroma-test
fi

# Create data directory
mkdir -p ./chroma-data
chmod 755 ./chroma-data

# Pull latest ChromaDB image
echo "📦 Pulling ChromaDB image..."
docker pull chromadb/chroma:latest

# Start ChromaDB container
echo "🚀 Starting ChromaDB container..."
docker run -d \
    --name chroma-test \
    -v "$(pwd)/chroma-data:/data" \
    -p 8001:8000 \
    chromadb/chroma:latest

# Wait for container to be ready
echo "⏳ Waiting for ChromaDB to be ready..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    
    if curl -s http://localhost:8001/api/v2/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    
    retry_count=$((retry_count + 1))
    echo "   Attempt $retry_count/$max_retries - waiting..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ ChromaDB failed to start after $max_retries attempts"
    exit 1
fi

# Test connection
echo "🧪 Testing ChromaDB connection..."
response=$(curl -s http://localhost:8001/api/v2/heartbeat)
echo "   Response: $response"

echo ""
echo "🎉 ChromaDB setup complete!"
echo "   Container name: chroma-test"
echo "   HTTP API: http://localhost:8001"
echo "   Data directory: $(pwd)/chroma-data"
echo ""
echo "To stop: docker stop chroma-test"
echo "To remove: docker rm chroma-test"
