#!/bin/bash

echo "=== Sprint 3 PDF RAG System Health Check ==="
echo "Timestamp: $(date)"
echo

# Check if containers are running
echo "1. Checking Docker containers..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep app-

echo
echo "2. Testing backend health..."
curl -s -w "Status: %{http_code}\n" http://localhost:8000/ || echo "Backend not responding"

echo
echo "3. Testing collections endpoint..."
curl -s -w "Status: %{http_code}\n" http://localhost:8000/collections/ || echo "Collections endpoint not responding"

echo
echo "4. Testing system stats..."
curl -s -w "Status: %{http_code}\n" http://localhost:8000/qa/admin/system-stats || echo "System stats not responding"

echo
echo "=== Health Check Complete ==="
