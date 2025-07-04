# Agent Codebase Analysis Configuration

## Primary Objective
Configure AI agents to autonomously navigate, analyze, and debug codebases using systematic approaches and available tools.

## Core Analysis Capabilities

### 1. **Workspace Navigation & Search**
```markdown
**Available Commands:**
- Use `@workspace` to search across all files
- Query specific file patterns: `@workspace *.py`, `@workspace *.js`
- Search for functions, classes, or variables by name
- Find imports and dependencies

**Search Strategies:**
- Look for error messages in logs or console outputs
- Search for API endpoint definitions (`/api/`, `@app.route`, `@router`)
- Find configuration files (`.env`, `config.py`, `settings.json`)
- Locate test files to understand expected behavior
```

### 2. **Error Analysis Workflow**
```markdown
**Step 1: Identify Error Type**
- HTTP status codes (4xx = client/request issue, 5xx = server issue)
- Frontend errors (check browser console, component rendering)
- Backend errors (check server logs, API responses)

**Step 2: Trace Error Source**
- For API errors: Find the route handler and request validation
- For frontend errors: Locate the component making the request
- For database errors: Check model definitions and migrations

**Step 3: Compare Expected vs Actual**
- Find API documentation or schema definitions
- Compare request payload with expected format
- Check data types, required fields, and validation rules
```

### 3. **Code Investigation Patterns**

#### **For Backend Issues:**
```markdown
**Search Priority:**
1. Route definitions: `@app.post`, `@router.post`, `app.post(`
2. Request models: `BaseModel`, `@dataclass`, `interface`
3. Validation logic: `validate`, `schema`, `required`
4. Error handling: `try`, `except`, `catch`, `throw`

**Key Files to Check:**
- API route files (`api.py`, `routes.js`, `controllers/`)
- Model definitions (`models.py`, `schemas/`, `types.ts`)
- Configuration files (`settings.py`, `config.js`, `.env`)
```

#### **For Frontend/Plugin Issues:**
```markdown
**Search Priority:**
1. HTTP requests: `fetch`, `axios`, `XMLHttpRequest`
2. Event handlers: `onClick`, `onSubmit`, `addEventListener`
3. State management: `useState`, `setState`, `store`
4. Error boundaries: `try-catch`, `error`, `onError`

**Key Files to Check:**
- Component files (`.vue`, `.jsx`, `.tsx`, `.js`)
- API service files (`api.js`, `services/`, `utils/`)
- Plugin manifest files (`manifest.json`, `package.json`)
```

### 4. **Debugging Commands for Agents**

#### **VS Code Integration:**
```markdown
**Use these commands:**
- `@workspace search for [term]` - Find code patterns
- `#file:[filename]` - Reference specific files
- `#selection` - Analyze selected code
- Ask about terminal output with specific error messages
- Request unit tests for suspicious functions
```

#### **Problem Diagnosis Questions:**
```markdown
**Ask yourself:**
1. "What was the last working state?" - Check git history
2. "What changed recently?" - Look for recent commits/modifications
3. "Are all dependencies installed?" - Check package files
4. "Is the data format correct?" - Compare schema expectations
5. "Are environment variables set?" - Check .env files
```

### 5. **Systematic Investigation Template**

```markdown
**For HTTP 422 Errors (like in the original issue):**

1. **Find the endpoint handler:**
   Search: `@workspace /api/obsidian/conversation/history`

2. **Locate request model/schema:**
   Search: `@workspace ConversationHistory` or `@workspace conversation_history`

3. **Find frontend request code:**
   Search: `@workspace fetch.*conversation/history` or `@workspace conversation/history`

4. **Compare payload structure:**
   - Check what the backend expects (schema/model definition)
   - Check what the frontend sends (request body)
   - Identify mismatches in field names, types, or required fields

5. **Test hypothesis:**
   - Suggest adding console.log to inspect payload
   - Recommend backend logging to see received data
   - Propose schema validation fixes
```

### 6. **Agent Communication Protocol**

```markdown
**When reporting findings:**
1. **State the problem type:** "This is a [backend validation/frontend request/configuration] issue"
2. **Show the evidence:** Quote relevant code snippets from files
3. **Explain the mismatch:** "Backend expects X, but frontend sends Y"
4. **Propose specific fix:** Provide exact code changes needed
5. **Suggest verification:** "Test this by [specific action]"

**Code block format for fixes:**
Use 4 backticks with language and filepath comments for precise suggestions
```

### 7. **Tool-Specific Commands**

```markdown
**For FastAPI backends:**
- Search for `BaseModel` classes
- Look for `@app.post` or `@router.post` decorators
- Check `HTTPException` and validation errors

**For React/Vue frontends:**
- Search for `useState`, `useEffect` hooks
- Look for API service functions
- Check error handling in components

**For Node.js:**
- Search for `express` routes and middleware
- Look for request validation middleware
- Check error handling patterns
```

## EvoAgentX-Specific Investigation Patterns

### **FastAPI Backend Analysis**
```markdown
**Primary Search Targets:**
- `/api/obsidian/*` endpoints in `evoagentx/api.py`
- Request models in `evoagentx/models/`
- Validation logic in route handlers
- CORS configuration for Obsidian plugin

**Common Issues:**
- Pydantic model validation failures (422 errors)
- Missing or incorrect field types
- CORS preflight request handling
- Authentication/authorization middleware
```

### **Obsidian Plugin Frontend**
```markdown
**Primary Search Targets:**
- Plugin manifest in `examples/obsidian-plugin/`
- API client code making requests to backend
- TypeScript interfaces matching backend models
- Error handling in plugin components

**Common Issues:**
- Payload structure mismatches
- Missing required fields in requests
- Incorrect content-type headers
- Network connectivity issues
```

### **Client Application**
```markdown
**Primary Search Targets:**
- React components in `client/src/`
- API service functions
- State management (contexts, stores)
- Vite configuration and build issues

**Common Issues:**
- Component rendering errors
- State synchronization problems
- Build configuration conflicts
- Proxy/CORS issues in development
```

## Implementation Checklist

### **For Agents Analyzing This Codebase:**
- [ ] Search for recent changes in git history
- [ ] Check if all services are running (FastAPI backend, Vite frontend)
- [ ] Verify environment variables are properly set
- [ ] Ensure dependencies are installed (`requirements.txt`, `package.json`)
- [ ] Look for error patterns in console/terminal output
- [ ] Compare request/response schemas between frontend and backend
- [ ] Test API endpoints independently using curl or Postman
- [ ] Validate plugin manifest and permissions for Obsidian integration

### **Quick Diagnostic Commands:**
```bash
# Check if backend is running
curl http://localhost:8000/api/obsidian/health

# Check frontend build
cd client && npm run build

# Check Python environment
python -c "import evoagentx; print('OK')"

# Check for syntax errors
python -m py_compile evoagentx/api.py
```

## Implementation Notes
- Always reference specific files using `#file:` notation
- Use `@workspace` searches to gather context before making recommendations
- Provide concrete code examples with proper file paths
- Test hypotheses by suggesting specific debugging steps
- Prioritize systematic investigation over assumptions
- For EvoAgentX specifically, focus on the FastAPI-Obsidian-Client triangle of communication

This configuration enables agents to methodically analyze the EvoAgentX codebase, identify problems, and provide actionable solutions using available IDE and copilot tools.
