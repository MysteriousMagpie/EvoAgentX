# Agent Quick Reference Card

## 🚨 Emergency Debug Commands

### **For 422 Errors (Data Validation Issues):**
```bash
# 1. Find the failing endpoint
@workspace /api/obsidian/conversation/history

# 2. Find the data model
@workspace BaseModel.*Conversation
@workspace class.*ConversationHistory

# 3. Find the request code
@workspace fetch.*conversation/history
@workspace POST.*conversation/history
```

### **For 500 Errors (Server Issues):**
```bash
# 1. Check server logs
@workspace logger.error
@workspace print.*error
@workspace Exception

# 2. Find the route handler
@workspace @app.post.*[endpoint]
@workspace def.*[endpoint_function]
```

### **For 404 Errors (Missing Endpoints):**
```bash
# 1. Verify route registration
@workspace @app.post
@workspace @router.post
@workspace app.include_router

# 2. Check URL patterns
@workspace /api/
@workspace router.*prefix
```

## 🔍 Investigation Workflow

### **Step 1: Identify Error Type**
- **422**: Data validation failed → Check request payload vs model
- **500**: Server error → Check backend logs and exception handling
- **404**: Route not found → Check route registration and URL patterns
- **403/401**: Permission denied → Check authentication/authorization
- **CORS**: Options preflight failed → Check CORS configuration

### **Step 2: Search Strategy**
```markdown
**For Backend Issues:**
- Route definitions: `@app.post`, `@router.post`
- Models: `BaseModel`, `@dataclass`
- Validation: `HTTPException`, `ValidationError`
- Config: `CORS`, `middleware`

**For Frontend Issues:**
- Requests: `fetch`, `axios`, `XMLHttpRequest`
- Components: `useState`, `useEffect`, `onClick`
- Types: `interface`, `type`, `Props`
- Errors: `try`, `catch`, `error`
```

### **Step 3: File Targets (EvoAgentX Specific)**
```markdown
**Backend:**
- `#file:evoagentx/api.py` - Main API routes
- `#file:server/main.py` - FastAPI app setup
- `#file:evoagentx/models/` - Data models

**Frontend:**
- `#file:client/src/` - React components
- `#file:client/src/services/` - API clients

**Plugin:**
- `#file:examples/obsidian-plugin/` - Obsidian plugin code
```

## 🛠️ Common Fixes

### **422 Validation Errors:**
```python
# Backend: Add better error logging
except ValidationError as e:
    logger.error(f"Validation failed: {e.json()}")
    raise HTTPException(422, detail=e.errors())
```

```javascript
// Frontend: Validate payload before sending
console.log("Payload:", JSON.stringify(payload, null, 2));
```

### **CORS Issues:**
```python
# Backend: Configure CORS properly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Type Mismatches:**
```typescript
// Frontend: Ensure types match backend
interface ConversationHistoryRequest {
    message: string;
    timestamp?: number;
    agent_id: string;
    session_id?: string;
}
```

## 📋 Agent Checklist

### **Before Making Changes:**
- [ ] Search for existing error patterns: `@workspace [error_message]`
- [ ] Find the relevant files: `#file:[filename]`
- [ ] Understand the expected vs actual behavior
- [ ] Check for recent changes in git history

### **When Proposing Fixes:**
- [ ] Quote specific code snippets showing the issue
- [ ] Explain the mismatch clearly
- [ ] Provide exact code changes needed
- [ ] Suggest verification steps

### **After Implementing Fixes:**
- [ ] Test the specific error scenario
- [ ] Verify no new errors were introduced
- [ ] Document the solution for future reference

## 🎯 Agent Communication Templates

### **Problem Identification:**
```markdown
**Issue Type:** [Backend Validation/Frontend Request/CORS/etc.]
**Error Code:** [422/500/404/etc.]
**Root Cause:** [Specific technical cause]
**Files Involved:** 
- Backend: `#file:[backend_file]`
- Frontend: `#file:[frontend_file]`
```

### **Solution Proposal:**
```markdown
**Fix Required:** [Brief description]
**Code Changes:**
[Specific code snippets with file paths]

**Verification:**
1. [Specific test step]
2. [Expected result]
```

## 🚀 Quick Test Commands

```bash
# Test API endpoint
curl -X POST http://localhost:8000/api/obsidian/conversation/history \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "agent_id": "test_agent"}'

# Check Python syntax
python -m py_compile evoagentx/api.py

# Check TypeScript types
cd client && npm run type-check

# Validate JSON
echo '{"test": "value"}' | python -m json.tool
```

---
*Use this reference card for quick debugging of EvoAgentX issues. Focus on systematic investigation and clear communication.*
