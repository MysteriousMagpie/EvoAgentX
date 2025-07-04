#!/usr/bin/env python3
"""
Test script to verify CORS functionality for the Obsidian plugin API.
This script tests that the FastAPI backend properly handles CORS requests
from the Obsidian plugin environment.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_cors():
    """Test CORS configuration with Obsidian origins"""
    print("=== Testing CORS Configuration ===\n")
    
    # Test 1: OPTIONS preflight for health endpoint
    print("Testing OPTIONS preflight for /api/obsidian/health...")
    try:
        response = requests.options(
            f"{BASE_URL}/api/obsidian/health",
            headers={
                "Origin": "app://obsidian.md",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ OPTIONS preflight successful\n")
        else:
            print("❌ OPTIONS preflight failed\n")
            
    except Exception as e:
        print(f"❌ OPTIONS test failed: {e}\n")
    
    # Test 2: Actual GET request to health endpoint  
    print("Testing GET request to /api/obsidian/health...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/obsidian/health",
            headers={"Origin": "app://obsidian.md"}
        )
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ GET request successful\n")
        else:
            print("❌ GET request failed\n")
            
    except Exception as e:
        print(f"❌ GET test failed: {e}\n")
    
    # Test 3: Test status endpoint
    print("Testing GET request to /status...")
    try:
        response = requests.get(
            f"{BASE_URL}/status",
            headers={"Origin": "app://obsidian.md"}
        )
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print("✅ Status endpoint successful\n")
        else:
            print("❌ Status endpoint failed\n")
            
    except Exception as e:
        print(f"❌ Status test failed: {e}\n")

    # Test 4: Test with different origins
    test_origins = [
        "app://obsidian.md",
        "capacitor://localhost", 
        "http://localhost:5173",
        "http://localhost"
    ]
    
    print("Testing different origins...")
    for origin in test_origins:
        try:
            response = requests.get(
                f"{BASE_URL}/api/obsidian/health",
                headers={"Origin": origin}
            )
            cors_origin = response.headers.get('Access-Control-Allow-Origin', 'Not Set')
            print(f"Origin: {origin} -> CORS: {cors_origin}")
            
        except Exception as e:
            print(f"❌ Origin {origin} failed: {e}")
    
    print("\n=== CORS Test Complete ===")

def test_server_running():
    """Check if the server is running and accessible"""
    print("Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    if test_server_running():
        test_cors()
    else:
        print("\nPlease start the server first with:")
        print("uvicorn server.main:sio_app --host 0.0.0.0 --port 8000 --reload")
        print("or")
        print("python -m server.main")
