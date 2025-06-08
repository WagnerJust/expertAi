#!/usr/bin/env python3
"""
Test FastAPI server startup and basic endpoints
"""
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

from fastapi.testclient import TestClient
from app.main import app

def test_server_startup():
    """Test server startup and basic endpoints"""
    print("🚀 Testing FastAPI Server")
    print("=" * 40)
    
    # Create test client
    client = TestClient(app)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = client.get("/")
    print(f"   Health check: {response.status_code} - {response.json()}")
    
    # Test collections endpoint
    print("\n2. Testing collections endpoint...")
    response = client.get("/collections")
    print(f"   Collections: {response.status_code}")
    if response.status_code == 200:
        collections = response.json()
        print(f"   Found {len(collections)} collections")
    else:
        print(f"   Error: {response.text}")
    
    # Test Q&A health endpoint (should exist)
    print("\n3. Testing Q&A health endpoint...")
    response = client.get("/qa/health")
    print(f"   Q&A Health: {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.json()}")
    else:
        print(f"   Error: {response.text}")
    
    print("\n" + "=" * 40)
    print("Server tests completed!")

if __name__ == "__main__":
    test_server_startup()
