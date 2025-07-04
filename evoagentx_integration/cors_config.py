"""
CORS Configuration for VaultPilot Integration

This file configures Cross-Origin Resource Sharing (CORS) to allow
VaultPilot (running in Obsidian) to communicate with your EvoAgentX server.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, development: bool = True):
    """
    Configure CORS middleware for VaultPilot integration
    
    Args:
        app: FastAPI application instance
        development: Whether running in development mode (more permissive CORS)
    """
    
    if development:
        # Development CORS - more permissive for local testing
        origins = [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:5174",  # Alternative Vite port
            "http://localhost:3000",  # React dev server
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174", 
            "http://127.0.0.1:3000",
            "app://obsidian.md",      # Obsidian desktop app
            "capacitor://localhost",  # Obsidian mobile
            "ionic://localhost",      # Alternative mobile scheme
            "*"                       # Allow all origins in development
        ]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=[
                "Accept",
                "Accept-Language", 
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Origin",
                "User-Agent",
                "Cache-Control",
                "Pragma"
            ],
            expose_headers=[
                "Content-Length",
                "Content-Type", 
                "Date",
                "Server"
            ],
            max_age=3600  # Cache preflight requests for 1 hour
        )
        
    else:
        # Production CORS - more restrictive
        origins = [
            "app://obsidian.md",      # Obsidian desktop app
            "capacitor://localhost",  # Obsidian mobile
            "ionic://localhost",      # Alternative mobile scheme
            # Add your production domains here:
            # "https://yourdomain.com",
            # "https://api.yourdomain.com"
        ]
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Accept",
                "Content-Type", 
                "Authorization",
                "X-Requested-With"
            ],
            max_age=86400  # Cache preflight requests for 24 hours
        )
        
    print(f"CORS configured for VaultPilot integration (development={development})")


def add_cors_headers(response):
    """
    Manually add CORS headers to a response if needed
    
    Use this for custom responses that bypass the middleware.
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Custom CORS handler for complex scenarios
async def custom_cors_handler(request, call_next):
    """
    Custom CORS middleware for special handling
    
    Add this if you need custom CORS logic:
    
    @app.middleware("http")
    async def cors_handler(request: Request, call_next):
        return await custom_cors_handler(request, call_next)
    """
    
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Max-Age"] = "3600"
        return response
    
    # Process the request
    response = await call_next(request)
    
    # Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response


# WebSocket CORS handling
def setup_websocket_cors():
    """
    Configure CORS for WebSocket connections
    
    Note: WebSocket CORS is handled differently than HTTP CORS.
    Most modern browsers allow WebSocket connections from any origin
    to localhost, but you may need special handling for production.
    """
    
    # WebSocket connections from Obsidian are typically allowed
    # since they originate from the desktop app, not a browser
    pass


# Development testing utilities
def test_cors_setup():
    """
    Test CORS configuration with common requests
    
    Use this to verify your CORS setup is working correctly.
    """
    import requests
    
    # Test basic GET request
    try:
        response = requests.get("http://localhost:8000/status", 
                              headers={"Origin": "app://obsidian.md"})
        print(f"GET /status: {response.status_code}")
        print(f"CORS headers: {response.headers.get('Access-Control-Allow-Origin')}")
    except Exception as e:
        print(f"GET test failed: {e}")
    
    # Test OPTIONS preflight
    try:
        response = requests.options("http://localhost:8000/api/obsidian/chat",
                                  headers={
                                      "Origin": "app://obsidian.md",
                                      "Access-Control-Request-Method": "POST",
                                      "Access-Control-Request-Headers": "Content-Type"
                                  })
        print(f"OPTIONS preflight: {response.status_code}")
        print(f"Allowed methods: {response.headers.get('Access-Control-Allow-Methods')}")
    except Exception as e:
        print(f"OPTIONS test failed: {e}")


if __name__ == "__main__":
    # Run CORS tests
    print("Testing CORS configuration...")
    test_cors_setup()
