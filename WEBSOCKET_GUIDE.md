# WebSocket Connection Guide for VaultPilot

## 🚀 Quick Reconnection

If you get disconnected from the WebSocket, use one of these methods:

### Method 1: Quick Reconnection Script
```bash
python reconnect_websocket.py
```

### Method 2: Command Line Reconnection
```bash
python reconnect_websocket.py your_vault_id
```

### Method 3: Manual Test
```bash
python test_websocket_reconnect.py
```

## 🔍 Troubleshooting WebSocket Disconnections

### Check Server Status
```bash
curl http://127.0.0.1:8000/status
curl http://127.0.0.1:8000/ws/status
```

### Common Causes of Disconnections

1. **Server Restart**: The development server auto-reloads when files change
2. **Network Issues**: Temporary network connectivity problems
3. **Timeout**: Long periods of inactivity (>30 seconds)
4. **Resource Limits**: Server overload or memory issues

### WebSocket Status Information

- **Endpoint**: `ws://127.0.0.1:8000/ws/obsidian`
- **Status Check**: `http://127.0.0.1:8000/ws/status`
- **Server Health**: `http://127.0.0.1:8000/health`

## 🔧 Automatic Reconnection

The WebSocket connection includes built-in features:

- **Ping/Pong**: Keepalive messages every 30 seconds
- **Connection Monitoring**: Server tracks active connections
- **Graceful Disconnect**: Proper cleanup on disconnect
- **Error Handling**: JSON parsing and connection error recovery

## 🛠️ For Developers

### WebSocket Message Types
- `ping` - Keepalive/test message
- `pong` - Server response to ping
- `connection` - Connection status updates
- `chat` - Real-time chat updates
- `workflow_progress` - Workflow status
- `copilot` - AI suggestions
- `vault_sync` - Vault synchronization
- `error` - Error notifications

### Example Client Code
```python
import asyncio
import websockets
import json

async def connect_to_vaultpilot(vault_id="default"):
    url = f"ws://127.0.0.1:8000/ws/obsidian?vault_id={vault_id}"
    
    async with websockets.connect(url) as websocket:
        # Send ping
        await websocket.send(json.dumps({
            "type": "ping",
            "data": {"client": "custom"}
        }))
        
        # Listen for responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
```

## 📊 Monitoring

Use the WebSocket status endpoint to monitor connections:

```bash
# Check active connections
curl http://127.0.0.1:8000/ws/status | jq

# Expected response:
{
  "websocket_available": true,
  "active_connections": 1,
  "active_vaults": ["default"],
  "connection_details": {
    "default": 1
  },
  "endpoint": "ws://127.0.0.1:8000/ws/obsidian",
  "timestamp": 1751611512.038551
}
```

## ⚡ Quick Commands

```bash
# Start server
python run_server.py --dev

# Test connection
python reconnect_websocket.py

# Check server status
curl http://127.0.0.1:8000/status

# Check WebSocket status
curl http://127.0.0.1:8000/ws/status

# Kill and restart server if needed
pkill -f "run_server.py" && python run_server.py --dev
```
