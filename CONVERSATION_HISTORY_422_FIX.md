# Fix for 422 Unprocessable Entity Errors on /api/obsidian/conversation/history

## Problem Diagnosis

The server was receiving 422 Unprocessable Entity errors on the `/api/obsidian/conversation/history` endpoint. Investigation revealed:

1. **Root Cause**: Client code was sending chat-like payloads to the conversation history endpoint
2. **Wrong Payload**: `{"message": "...", "agent_id": "..."}` 
3. **Expected Payload**: `{"conversation_id": "...", "limit": 50}`

## Symptoms
- HTTP 422 errors in server logs: `"POST /api/obsidian/conversation/history HTTP/1.1" 422 Unprocessable Entity`
- Client receiving validation errors about missing `conversation_id` field

## Root Cause Analysis

The conversation history endpoint expects:
```typescript
interface ConversationHistoryRequest {
  conversation_id: string;  // REQUIRED
  limit?: number;          // OPTIONAL (default: 50)
}
```

But client code was sending:
```typescript
{
  message: string;
  agent_id: string;
}
```

This suggests either:
1. Wrong endpoint URL in client code (should be `/api/obsidian/chat`)
2. Copy-paste error in client implementation
3. Misconfigured proxy/routing

## Implemented Fixes

### 1. Enhanced Error Handling
Added global FastAPI validation error handler in `server/main.py`:
- Detects common endpoint mismatches
- Provides helpful error messages pointing to correct endpoint
- Logs detailed debugging information

### 2. Specific Conversation History Error Detection
Added logic to detect when chat payloads are sent to conversation history endpoint:
```python
if is_conversation_history_endpoint and has_message_field_error:
    return JSONResponse(
        status_code=422,
        content={
            "error": "Endpoint Mismatch",
            "message": "You're sending chat data to the conversation history endpoint. Use /api/obsidian/chat instead.",
            "correct_endpoint": "/api/obsidian/chat",
            # ... helpful payload examples
        }
    )
```

### 3. Debug Logging
Added comprehensive logging for validation errors:
- Request URL and method
- Request headers
- Raw request body
- Parsed JSON body
- Detailed validation errors

## Verification

### Test Cases Added

1. **Wrong endpoint (fixed):**
```bash
curl -X POST http://localhost:8000/api/obsidian/conversation/history \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "agent_id": "test"}'
```
Response: Helpful error message pointing to `/api/obsidian/chat`

2. **Correct chat endpoint:**
```bash
curl -X POST http://localhost:8000/api/obsidian/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, test message"}'
```
Response: ✅ Works correctly

3. **Correct conversation history endpoint:**
```bash
curl -X POST http://localhost:8000/api/obsidian/conversation/history \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "some-id", "limit": 10}'
```
Response: ✅ Works correctly

## Next Steps for Client Code

### For Frontend/Plugin Developers:

1. **Check endpoint URLs** - Make sure you're using:
   - `/api/obsidian/chat` for sending messages
   - `/api/obsidian/conversation/history` for retrieving history

2. **Correct payload formats:**
   ```typescript
   // For chat
   const chatPayload = {
     message: "Your message here",
     conversation_id: "optional-conversation-id",
     context: { /* optional */ }
   };
   
   // For conversation history
   const historyPayload = {
     conversation_id: "required-conversation-id",
     limit: 50  // optional
   };
   ```

3. **Error handling** - The new error responses provide clear guidance:
   ```typescript
   if (response.status === 422) {
     const error = await response.json();
     if (error.error === "Endpoint Mismatch") {
       console.log("Use endpoint:", error.correct_endpoint);
     }
   }
   ```

## Benefits of This Fix

1. **Immediate debugging**: Developers get clear error messages instead of cryptic validation errors
2. **Self-documenting**: Error responses include example payloads
3. **Fast resolution**: Points directly to the correct endpoint and payload format
4. **Comprehensive logging**: Server logs provide full context for debugging

## Files Modified

1. `server/main.py`: Added global validation error handler
2. `server/api/obsidian.py`: Enhanced conversation history endpoint with detailed debugging
3. `CONVERSATION_HISTORY_422_FIX.md`: This documentation

The 422 errors should now be much easier to diagnose and fix, with clear guidance provided to developers about the correct endpoint and payload format to use.
