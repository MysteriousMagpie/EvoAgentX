# Fix CORS Response Headers - Backend Issue

## Problem Description
The VaultPilot frontend is receiving CORS errors when making requests to the FastAPI backend. The browser is blocking cross-origin requests because of "invalid or missing response headers."

**Error Message:**
```
A cross-origin resource sharing (CORS) request was blocked because of invalid or missing response headers of the request or the associated preflight request.
```

## Current Backend Setup
- **Framework:** FastAPI 
- **CORS Config Location:** `evoagentx_integration/cors_config.py`
- **Expected Backend URL:** `http://localhost:8000`
- **Frontend Origins:** Obsidian plugin (`app://obsidian.md`) + local development ports

## Tasks to Fix

### 1. Verify CORS Middleware is Applied
**Check your main FastAPI app file** (likely `main.py` or `app.py`) and ensure:

```python
from fastapi import FastAPI
from evoagentx_integration.cors_config import setup_cors

app = FastAPI()

# THIS MUST BE CALLED - verify it exists:
setup_cors(app, development=True)  # Set to True for development

# Include your routes AFTER CORS setup
app.include_router(obsidian_router, prefix="/api/obsidian")
```

### 2. Verify Headers in Responses
Add debug logging to see what headers are actually being sent:

```python
@app.middleware("http")
async def debug_cors_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Debug: Print response headers
    print(f"Response headers for {request.method} {request.url.path}:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"  {header}: {value}")
    
    return response
```

### 3. Handle OPTIONS Preflight Requests
Ensure your FastAPI app properly handles preflight requests:

```python
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Max-Age": "3600"
        }
    )
```

### 4. Test CORS Configuration
Run this test from your backend directory:

```python
# test_cors.py
import requests

def test_cors():
    base_url = "http://localhost:8000"
    
    # Test 1: OPTIONS preflight
    print("Testing OPTIONS preflight...")
    try:
        response = requests.options(
            f"{base_url}/api/obsidian/health",
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
    except Exception as e:
        print(f"OPTIONS test failed: {e}")
    
    # Test 2: Actual GET request  
    print("\nTesting GET request...")
    try:
        response = requests.get(
            f"{base_url}/api/obsidian/health",
            headers={"Origin": "app://obsidian.md"}
        )
        print(f"Status: {response.status_code}")
        print("CORS Headers:")
        for header, value in response.headers.items():
            if 'access-control' in header.lower():
                print(f"  {header}: {value}")
    except Exception as e:
        print(f"GET test failed: {e}")

if __name__ == "__main__":
    test_cors()
```

### 5. Common Issues to Check

1. **CORS middleware order**: CORS middleware must be added BEFORE route definitions
2. **Missing health endpoint**: Ensure `/api/obsidian/health` endpoint exists and responds
3. **Server not running**: Verify FastAPI server is actually running on port 8000
4. **Port conflicts**: Check if another service is using port 8000

### 6. Expected Working Headers
After fixing, these headers should be present in responses:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: Accept, Content-Type, Authorization, X-Requested-With, Origin, User-Agent, Cache-Control, Pragma
Access-Control-Allow-Credentials: true
```

### 7. Quick Debug Commands

```bash
# Check if server is running
curl -I http://localhost:8000/status

# Test CORS headers specifically
curl -H "Origin: app://obsidian.md" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: Content-Type" -X OPTIONS http://localhost:8000/api/obsidian/health -v

# Check actual endpoint response
curl -H "Origin: app://obsidian.md" http://localhost:8000/api/obsidian/health -v
```

## Priority Order
1. Verify `setup_cors()` is called in main app file
2. Check server is running and accessible  
3. Test with the debug script above
4. Add the OPTIONS handler if preflight requests are failing
5. Add debug middleware to see actual headers being sent

The issue is likely that either:
- CORS middleware isn't properly applied to the FastAPI app
- The server isn't running/accessible 
- OPTIONS preflight requests aren't being handled correctly

Focus on #1 first - make sure `setup_cors(app, development=True)` is actually being called in your main FastAPI application file.
