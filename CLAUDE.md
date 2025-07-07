# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📚 Documentation Navigation

For comprehensive information about EvoAgentX, refer to these key documents:

- **[📊 Implementation Status Index](./docs/IMPLEMENTATION_STATUS_INDEX.md)** - Complete overview of all features and their current status
- **[📖 Documentation Guide](./docs/DOCUMENTATION_GUIDE.md)** - Navigate all documentation by role and use case  
- **[⚡ Quick Start Guide](./docs/quickstart.md)** - Get up and running quickly
- **[💻 Development Guide](./docs/development.md)** - Detailed development workflow
- **[🔌 Obsidian Integration](./docs/obsidian-integration.md)** - Complete Obsidian setup and plugin development
- **[📱 Frontend API Documentation](./docs/api/FRONTEND_API_DOCUMENTATION.md)** - Complete TypeScript API reference

## Core Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt
# or for development with all extras
pip install -e .[dev]

# Start the main server
python -m uvicorn server.main:sio_app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest
# with coverage
pytest --cov=evoagentx --cov-report=term-missing
```

### Testing & Quality
```bash
# Run all tests
pytest

# Run tests with coverage (configured for 80% minimum)
pytest --cov=evoagentx/utils --cov=evoagentx/optimizers --cov-report=term-missing --cov-branch

# Run specific test file
pytest tests/test_specific_module.py

# Run linting
ruff check .

# TypeScript testing (intelligence-parser)
cd intelligence-parser
npm test
npm run lint
npm run build
```

### CLI Usage
```bash
# Execute code in Docker container
python -m evoagentx.cli run -c "print('hello')"
python -m evoagentx.cli run --runtime node:20 -c "console.log(42)"

# Smart execution with intelligent interpreter selection
python -m evoagentx.cli run-smart -c "code here" --language python --security medium

# OpenAI Code Interpreter
python -m evoagentx.cli run-openai -c "code here" --files file1.py file2.csv

# Self-improvement workflow
python -m evoagentx.cli self-improve --goal "improve performance"
```

## Architecture Overview

### Core Components
- **evoagentx/**: Main Python package with modular architecture
  - **core/**: Base classes, message handling, configuration
  - **agents/**: Agent system with manager, customization, and generation
  - **workflow/**: Workflow generation, execution, and graph management
  - **models/**: LLM integrations (OpenAI, LiteLLM, OpenRouter, SiliconFlow)
  - **optimizers/**: AFlow, TextGrad, SEW optimization algorithms
  - **tools/**: Docker interpreter, OpenAI Code Interpreter, search tools
  - **benchmark/**: GSM8K, HumanEval, MBPP, HotPotQA evaluation systems

### Server Architecture
- **server/**: FastAPI-based API server with WebSocket support
  - **main.py**: Main server with CORS, validation, and dev-pipe integration
  - **api/**: API endpoints for Obsidian integration, workflow management
  - **core/**: WebSocket managers and macOS Calendar integration
  - **models/**: Pydantic schemas and data models

### Frontend Integration
- **intelligence-parser/**: TypeScript package for message parsing
- **vault-management/**: TypeScript components for Obsidian integration
- **evoagentx_integration/**: Enhanced API routes and WebSocket handlers

## Key Patterns

### Agent System
- Agents are created via `AgentManager` and can be customized with `CustomizeAgent`
- Workflows are generated using `WorkFlowGenerator` and executed with `WorkFlow`
- Action graphs define agent interactions with `ActionGraph` and `QAActionGraph`

### Model Configuration
```python
from evoagentx.models import OpenAILLMConfig, OpenAILLM

config = OpenAILLMConfig(
    model="gpt-4o-mini",
    openai_key=os.getenv("OPENAI_API_KEY"),
    stream=True,
    output_response=True
)
llm = OpenAILLM(config=config)
```

### Workflow Creation
```python
from evoagentx.workflow import WorkFlowGenerator, WorkFlow
from evoagentx.agents import AgentManager

goal = "Generate html code for the Tetris game"
workflow_graph = WorkFlowGenerator(llm=llm).generate_workflow(goal)
agent_manager = AgentManager()
agent_manager.add_agents_from_workflow(workflow_graph, llm_config=config)
workflow = WorkFlow(graph=workflow_graph, agent_manager=agent_manager, llm=llm)
output = workflow.execute()
```

## Development Guidelines

### Testing
- Use pytest for all Python tests
- Maintain 80% code coverage minimum (configured in pyproject.toml)
- Use pytest-asyncio for async tests
- Mock external dependencies with pytest-mock

### Code Quality
- Use ruff for linting and formatting
- Follow pydantic models for data validation
- Use proper type hints throughout
- Handle errors gracefully with try-catch blocks

### API Development
- All API endpoints should include proper CORS headers
- Use FastAPI dependency injection for shared resources
- Implement proper validation with Pydantic models
- Include comprehensive error handling and logging

### Obsidian Integration
- WebSocket connections use `/ws/obsidian` endpoint
- API routes are prefixed with `/api/obsidian/`
- Support real-time communication for vault updates
- Handle conversation history and agent interactions

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `ALLOWED_ORIGINS`: CORS origins for development (optional)

## Common Issues

### Server Startup
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that port 8000 is available or change the port
- Verify OpenAI API key is properly set

### Testing
- Run tests from the project root directory
- Use `pytest -v` for verbose output when debugging
- Check that all test data files exist in `tests/data/`

### Development
- Use `--reload` flag for automatic server restarts during development
- Check CORS configuration if frontend requests are failing
- Monitor server logs for WebSocket connection issues

## Performance Considerations

- Use async/await for all I/O operations
- Implement proper connection pooling for database operations
- Cache expensive computations where appropriate
- Monitor memory usage with large datasets in benchmarks
- Use streaming responses for long-running operations