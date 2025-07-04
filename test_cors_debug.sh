#!/bin/bash
# CORS Debug Script - Test CORS functionality with curl commands

echo "=== CORS Debug Script ==="
echo "Testing CORS configuration for EvoAgentX backend"
echo ""

BASE_URL="http://localhost:8000"

echo "1. Checking if server is running..."
curl -I "$BASE_URL/status" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server is accessible"
else
    echo "❌ Server is not running. Start it with:"
    echo "uvicorn server.main:sio_app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

echo ""
echo "2. Testing OPTIONS preflight request to health endpoint..."
curl -H "Origin: app://obsidian.md" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     "$BASE_URL/api/obsidian/health" \
     -v 2>&1 | grep -E "(< HTTP|< Access-Control|< Content-Type)"

echo ""
echo "3. Testing actual GET request to health endpoint..."
curl -H "Origin: app://obsidian.md" \
     "$BASE_URL/api/obsidian/health" \
     -v 2>&1 | grep -E "(< HTTP|< Access-Control|< Content-Type)"

echo ""
echo "4. Testing GET request to status endpoint..."
curl -H "Origin: app://obsidian.md" \
     "$BASE_URL/status" \
     -v 2>&1 | grep -E "(< HTTP|< Access-Control|< Content-Type)"

echo ""
echo "5. Testing response body for health endpoint..."
echo "Response from /api/obsidian/health:"
curl -H "Origin: app://obsidian.md" \
     "$BASE_URL/api/obsidian/health" \
     -s | jq '.' 2>/dev/null || curl -H "Origin: app://obsidian.md" "$BASE_URL/api/obsidian/health" -s

echo ""
echo "6. Testing response body for status endpoint..."
echo "Response from /status:"
curl -H "Origin: app://obsidian.md" \
     "$BASE_URL/status" \
     -s | jq '.' 2>/dev/null || curl -H "Origin: app://obsidian.md" "$BASE_URL/status" -s

echo ""
echo "=== Expected CORS Headers ==="
echo "Access-Control-Allow-Origin: *"
echo "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH"
echo "Access-Control-Allow-Headers: Accept, Content-Type, Authorization, X-Requested-With, Origin, User-Agent, Cache-Control, Pragma"
echo "Access-Control-Allow-Credentials: true"
echo ""
echo "If you see these headers in the responses above, CORS is working correctly!"
