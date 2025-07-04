#!/usr/bin/env python3
"""
Test script for vault management API endpoints
"""
import requests
import json
import os
from pathlib import Path

API_BASE = "http://localhost:8000/api/obsidian"

def test_api_endpoints():
    """Test the vault management API endpoints"""
    print("Testing Vault Management API Endpoints...")
    print("Note: This requires the server to be running on localhost:8000")
    
    # Test data
    test_data = {
        "structure_request": {
            "include_content": False,
            "max_depth": 3,
            "file_types": ["md"]
        },
        "file_operation_request": {
            "operation": "create",
            "file_path": "/test/api-test.md",
            "content": "# API Test\\n\\nThis file was created via API.",
            "create_missing_folders": True
        },
        "search_request": {
            "query": "test",
            "search_type": "content",
            "max_results": 10,
            "include_context": True
        },
        "batch_request": {
            "operations": [
                {
                    "operation": "create",
                    "file_path": "/test/batch1.md",
                    "content": "# Batch Test 1",
                    "create_missing_folders": True
                },
                {
                    "operation": "create",
                    "file_path": "/test/batch2.md",
                    "content": "# Batch Test 2",
                    "create_missing_folders": True
                }
            ],
            "continue_on_error": True
        },
        "organization_request": {
            "organization_goal": "Organize notes better",
            "preferences": {"structure": "topic-based"},
            "dry_run": True
        }
    }
    
    endpoints = [
        ("vault/structure", "POST", test_data["structure_request"]),
        ("vault/file/operation", "POST", test_data["file_operation_request"]),
        ("vault/search", "POST", test_data["search_request"]),
        ("vault/file/batch", "POST", test_data["batch_request"]),
        ("vault/organize", "POST", test_data["organization_request"])
    ]
    
    print(f"\\nTesting {len(endpoints)} endpoints...")
    
    for endpoint, method, data in endpoints:
        url = f"{API_BASE}/{endpoint}"
        print(f"\\n→ Testing {method} {endpoint}")
        
        try:
            if method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Success: {type(result).__name__} response received")
                # Print a summary of the response
                if isinstance(result, dict):
                    keys = list(result.keys())[:3]  # First 3 keys
                    print(f"    Keys: {keys}{'...' if len(result) > 3 else ''}")
            else:
                print(f"  ✗ Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection Error: Server not running on {API_BASE}")
            print(f"    Start the server with: python -m uvicorn server.main:app --reload")
            break
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout: Request took too long")
        except Exception as e:
            print(f"  ✗ Exception: {str(e)}")
    
    print("\\n" + "="*50)
    print("API endpoint testing completed!")
    print("\\nTo start the server:")
    print("  cd /path/to/EvoAgentX")
    print("  python -m uvicorn server.main:app --reload")

if __name__ == "__main__":
    test_api_endpoints()
