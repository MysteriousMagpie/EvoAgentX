#!/usr/bin/env python3
"""
Test script to verify CORS functionality for the Obsidian plugin API.
This script tests that the FastAPI backend properly handles CORS requests
from the Obsidian plugin environment.
"""

import requests
import json
import time
import subprocess
import os
import signal
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:8000"
HEALTH_ENDPOINT = "/api/obsidian/health"

# Origins that should be allowed
TEST_ORIGINS = [
    "app://obsidian.md",
    "capacitor://localhost",
    "http://localhost",
    "http://localhost:5173"
]

def start_server():
    """Start the FastAPI server in the background"""
    print("Starting FastAPI server...")
    env = os.environ.copy()
    env['PYTHONPATH'] = '/Users/malachiledbetter/Documents/GitHub/EvoAgentX'
    
    process = subprocess.Popen([
        '/Users/malachiledbetter/Documents/GitHub/EvoAgentX/venv/bin/python',
        '-m', 'uvicorn',
        'server.main:app',
        '--host', '0.0.0.0',
        '--port', '8000'
    ], cwd='/Users/malachiledbetter/Documents/GitHub/EvoAgentX', env=env)
    
    # Wait for server to start
    time.sleep(3)
    return process

def test_health_endpoint():
    """Test the health endpoint with GET and OPTIONS requests"""
    print("\n=== Testing Health Endpoint ===")
    
    # Test GET request
    print("Testing GET /api/obsidian/health...")
    try:
        response = requests.get(urljoin(BASE_URL, HEALTH_ENDPOINT))
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        print("✅ GET request successful")
    except Exception as e:
        print(f"❌ GET request failed: {e}")
        return False
    
    # Test OPTIONS request
    print("\nTesting OPTIONS /api/obsidian/health...")
    try:
        response = requests.options(urljoin(BASE_URL, HEALTH_ENDPOINT))
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        assert response.status_code == 200
        print("✅ OPTIONS request successful")
    except Exception as e:
        print(f"❌ OPTIONS request failed: {e}")
        return False
    
    return True

def test_cors_headers():
    """Test CORS headers with different origins"""
    print("\n=== Testing CORS Headers ===")
    
    for origin in TEST_ORIGINS:
        print(f"\nTesting origin: {origin}")
        
        # Test CORS preflight request
        headers = {
            'Origin': origin,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        try:
            response = requests.options(urljoin(BASE_URL, HEALTH_ENDPOINT), headers=headers)
            print(f"Preflight status: {response.status_code}")
            
            # Check CORS headers
            cors_headers = {k: v for k, v in response.headers.items() if k.lower().startswith('access-control')}
            print(f"CORS headers: {json.dumps(cors_headers, indent=2)}")
            
            assert response.status_code == 200
            assert 'access-control-allow-origin' in response.headers
            print(f"✅ CORS preflight successful for {origin}")
            
            # Test actual request with origin
            response = requests.get(urljoin(BASE_URL, HEALTH_ENDPOINT), headers={'Origin': origin})
            print(f"GET with origin status: {response.status_code}")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
            print(f"✅ GET with origin successful for {origin}")
            
        except Exception as e:
            print(f"❌ CORS test failed for {origin}: {e}")
            return False
    
    return True

def test_other_endpoints():
    """Test CORS on other API endpoints"""
    print("\n=== Testing Other Endpoints ===")
    
    endpoints = [
        "/api/obsidian/agents",
        "/api/obsidian/conversations"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting OPTIONS {endpoint}...")
        headers = {
            'Origin': 'app://obsidian.md',
            'Access-Control-Request-Method': 'GET'
        }
        
        try:
            response = requests.options(urljoin(BASE_URL, endpoint), headers=headers)
            print(f"Status: {response.status_code}")
            assert response.status_code == 200
            print(f"✅ OPTIONS successful for {endpoint}")
        except Exception as e:
            print(f"❌ OPTIONS failed for {endpoint}: {e}")
            return False
    
    return True

def main():
    """Run all CORS tests"""
    print("🚀 Starting CORS tests for EvoAgentX API")
    
    # Start server
    server_process = start_server()
    
    try:
        # Run tests
        success = True
        success &= test_health_endpoint()
        success &= test_cors_headers()
        success &= test_other_endpoints()
        
        if success:
            print("\n🎉 All CORS tests passed!")
            print("\nThe FastAPI backend is now properly configured for:")
            print("✅ Handling OPTIONS requests for CORS preflight")
            print("✅ Allowing requests from Obsidian plugin origins")
            print("✅ Returning proper CORS headers")
            print("✅ Health endpoint returns {'status': 'ok'}")
        else:
            print("\n❌ Some tests failed")
            return 1
            
    finally:
        # Clean up
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
