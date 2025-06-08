#!/usr/bin/env python3
"""
Test FastAPI server functionality
"""
import sys
import os
sys.path.append('/Users/justin/LLMS/App/backend')

from fastapi.testclient import TestClient
from app.main import app

def test_server_endpoints():
    """Test basic server endpoints"""
    print("🧪 Testing FastAPI Server Endpoints")
    print("=" * 40)
    
    client = TestClient(app)
    
    # 1. Test health check
    print("\n1. Testing health check endpoint...")
    try:
        response = client.get("/")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ Health check passed")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
    
    # 2. Test collections endpoint
    print("\n2. Testing collections endpoint...")
    try:
        response = client.get("/collections/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            collections = response.json()
            print(f"   Found {len(collections)} collections")
            print("   ✅ Collections endpoint working")
        else:
            print(f"   Response: {response.text}")
            print("   ⚠️  Collections endpoint returned non-200 status")
    except Exception as e:
        print(f"   ❌ Collections endpoint failed: {e}")
    
    # 3. Test Q&A endpoints structure (without actual queries)
    print("\n3. Testing Q&A endpoint structure...")
    try:
        # Test invalid request to see if endpoint exists
        response = client.post("/qa/ask", json={})
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [422, 400]:  # Validation error expected
            print("   ✅ Q&A endpoint exists and validates input")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Q&A endpoint test failed: {e}")
    
    print("\n" + "=" * 40)
    print("Server endpoint tests completed!")

if __name__ == "__main__":
    test_server_endpoints()
