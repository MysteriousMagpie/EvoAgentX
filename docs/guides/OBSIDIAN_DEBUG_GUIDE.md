# Obsidian Plugin Integration Debug Guide

## Quick Reference for 422 Unprocessable Entity Errors

### **Immediate Investigation Steps**

1. **Find the problematic endpoint handler:**
   ```bash
   # Search for the conversation history endpoint
   @workspace /api/obsidian/conversation/history
   ```

2. **Locate the request model:**
   ```bash
   # Search for the data model expecting the request
   @workspace ConversationHistory
   @workspace conversation_history
   @workspace BaseModel
   ```

3. **Find the frontend request code:**
   ```bash
   # Search for the code making the request
   @workspace fetch.*conversation/history
   @workspace POST.*conversation/history
   @workspace axios.*conversation/history
   ```

### **Common 422 Error Patterns in EvoAgentX**

#### **Backend Validation Issues:**
```python
# Typical FastAPI model validation
class ConversationHistoryRequest(BaseModel):
    message: str
    timestamp: Optional[int] = None
    agent_id: str
    session_id: Optional[str] = None

# Common causes of 422:
# - Missing required fields (message, agent_id)
# - Wrong data types (string instead of int for timestamp)
# - Extra fields not defined in model
# - Null values for non-optional fields
```

#### **Frontend Request Issues:**
```javascript
// Problematic request patterns
const badPayload = {
    msg: "Hello",           // Wrong field name (should be 'message')
    timestamp: "now",       // Wrong type (should be number or null)
    // Missing required 'agent_id' field
};

// Correct payload structure
const goodPayload = {
    message: "Hello",
    timestamp: Date.now(),
    agent_id: "agent_001",
    session_id: "session_123"
};
```

### **Debugging Commands for Copilot Agents**

#### **Search Patterns:**
```markdown
**For Backend Analysis:**
- `@workspace @app.post.*conversation/history`
- `@workspace class.*ConversationHistory`
- `@workspace HTTPException.*422`
- `@workspace ValidationError`

**For Frontend Analysis:**
- `@workspace fetch.*obsidian.*conversation`
- `@workspace POST.*api/obsidian`
- `@workspace JSON.stringify`
- `@workspace Content-Type.*application/json`

**For Plugin Analysis:**
- `@workspace obsidian-plugin`
- `@workspace manifest.json`
- `@workspace requestUrl`
- `@workspace Notice.*error`
```

#### **File Targets:**
```markdown
**Backend Files:**
- `#file:evoagentx/api.py` - Main API routes
- `#file:server/api/` - API route handlers
- `#file:evoagentx/models/` - Pydantic models

**Frontend Files:**
- `#file:client/src/` - React components
- `#file:examples/obsidian-plugin/` - Plugin code

**Configuration Files:**
- `#file:requirements.txt` - Python dependencies
- `#file:client/package.json` - Frontend dependencies
- `#file:examples/obsidian-plugin/manifest.json` - Plugin manifest
```

### **Step-by-Step 422 Resolution**

#### **Step 1: Identify the Exact Endpoint**
```markdown
**Agent Action:**
1. Search for the failing route: `@workspace /api/obsidian/conversation/history`
2. Look for FastAPI route decorators: `@app.post` or `@router.post`
3. Find the function handling this endpoint
```

#### **Step 2: Examine Request Model**
```markdown
**Agent Action:**
1. Find the Pydantic model used for request validation
2. Note all required fields and their types
3. Check for any field aliases or validators
4. Look for Optional vs required fields
```

#### **Step 3: Trace Frontend Request**
```markdown
**Agent Action:**
1. Find where the request is made (likely in plugin or client code)
2. Examine the payload being sent
3. Compare field names and types with backend model
4. Check if Content-Type header is set correctly
```

#### **Step 4: Compare and Fix**
```markdown
**Agent Action:**
1. Create a side-by-side comparison of expected vs actual payload
2. Identify specific mismatches (field names, types, missing fields)
3. Propose specific code changes to fix the mismatch
4. Suggest adding logging to verify the fix
```

### **Common Fixes for EvoAgentX**

#### **Backend Fixes:**
```python
# Add detailed error logging
@app.post("/api/obsidian/conversation/history")
async def conversation_history(request: ConversationHistoryRequest):
    try:
        # Process request
        pass
    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        raise HTTPException(status_code=422, detail=e.errors())
```

#### **Frontend Fixes:**
```javascript
// Add payload validation before sending
const payload = {
    message: message,
    timestamp: Date.now(),
    agent_id: selectedAgent,
    session_id: currentSession
};

console.log("Sending payload:", payload); // Debug logging

fetch('/api/obsidian/conversation/history', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
});
```

### **Verification Steps**

#### **For Agents to Suggest:**
```markdown
1. **Add logging:** Console.log the payload before sending
2. **Test manually:** Use curl or Postman to test the endpoint
3. **Check response:** Look at the detailed error message in 422 response
4. **Validate schema:** Ensure frontend and backend models match
5. **Test incrementally:** Start with minimal payload and add fields
```

#### **Manual Testing Commands:**
```bash
# Test the endpoint manually
curl -X POST http://localhost:8000/api/obsidian/conversation/history \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "agent_id": "test_agent"}'

# Check backend logs for detailed error info
tail -f logs/evoagentx.log

# Validate JSON payload
echo '{"message": "test"}' | python -m json.tool
```

This guide provides agents with specific patterns and commands to quickly diagnose and fix the type of 422 error you encountered.
