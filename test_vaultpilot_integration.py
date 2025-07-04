#!/usr/bin/env python3
"""
VaultPilot Integration Test Script

This script tests the VaultPilot integration endpoints to ensure everything is working correctly.
Run this after starting the EvoAgentX server to verify the integration.

Usage:
    python test_vaultpilot_integration.py [--host HOST] [--port PORT]
"""

import requests
import json
import argparse
import sys
import time
from typing import Dict, Any, Optional


def test_endpoint(url: str, method: str = "GET", data: Optional[Dict[Any, Any]] = None, expect_success: bool = True) -> bool:
    """Test a single endpoint and return success status"""
    try:
        print(f"🧪 Testing {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
                
                if expect_success and isinstance(result, dict):
                    if result.get("success") == False:
                        print(f"   ⚠️ API returned success=false")
                        return False
                        
                print(f"   ✅ Success")
                return True
                
            except json.JSONDecodeError:
                print(f"   📄 Text response: {response.text[:100]}...")
                print(f"   ✅ Success")
                return True
        else:
            print(f"   ❌ Failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test VaultPilot Integration")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print("🚀 VaultPilot Integration Test Suite")
    print(f"📍 Testing server at: {base_url}")
    print("=" * 60)
    
    tests = [
        # Core endpoints
        ("GET", "/", None, True),
        ("GET", "/health", None, True),
        
        # VaultPilot endpoints
        ("POST", "/api/obsidian/chat", {
            "message": "Hello VaultPilot!",
            "conversation_id": "test-conversation-123"
        }, True),
        
        ("POST", "/api/obsidian/copilot/complete", {
            "text": "The weather today is",
            "cursor_position": 18,
            "context": {}
        }, True),
        
        ("POST", "/api/obsidian/workflow", {
            "workflow_type": "analysis",
            "parameters": {"test": True}
        }, True),
        
        ("GET", "/api/obsidian/agents", None, True),
        
        ("POST", "/api/obsidian/vault/context", {
            "vault_path": "/test/vault"
        }, True),
    ]
    
    passed = 0
    total = len(tests)
    
    for method, endpoint, data, expect_success in tests:
        url = base_url + endpoint
        if test_endpoint(url, method, data, expect_success):
            passed += 1
        print()
        time.sleep(0.5)  # Brief pause between tests
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! VaultPilot integration is working correctly.")
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Check the server logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
