# EvoAgentX Repository Structure

This document describes the organized structure of the EvoAgentX repository after cleanup and reorganization.

## 📁 Root Directory Structure

```
EvoAgentX/
├── 📁 client/                 # Frontend React application
├── 📁 data/                   # Data files and datasets
├── 📁 demos/                  # Demo scripts and examples
├── 📁 deploy/                 # Deployment configurations
├── 📁 docs/                   # Documentation (organized by type)
├── 📁 evoagentx/             # Main Python package
├── 📁 examples/              # Code examples and samples
├── 📁 intelligence-parser/   # Intelligence parser module
├── 📁 scripts/               # Shell scripts and utilities
├── 📁 server/                # Backend server application
├── 📁 tests/                 # Python test files
├── 📁 typescript/            # TypeScript modules and tests
├── 📁 vault-management/      # Obsidian vault management
├── 📄 package.json           # Node.js dependencies
├── 📄 pyproject.toml         # Python project configuration
├── 📄 requirements.txt       # Python dependencies
└── 📄 README.md              # Main project documentation
```

## 📚 Directory Details

### `/client` - Frontend Application
- React-based frontend with TypeScript
- Modern UI components with TailwindCSS
- Vite build system

### `/demos` - Demonstration Scripts
- `demo_implementation.py` - Core functionality demo
- `demo_intent_classifier.py` - Intent classification demo
- `demo_vault_access.py` - Vault access demo
- `comprehensive_test_suite.py` - Advanced testing demo

### `/docs` - Documentation (Organized)
```
docs/
├── api/                      # API documentation
│   └── FRONTEND_API_DOCUMENTATION.md
├── conversations/            # Conversation logs
│   └── CONVERSATION_HISTORY_422_FIX.md
├── guides/                   # User guides
│   ├── AGENT_CODEBASE_ANALYSIS_CONFIG.md
│   ├── AGENT_QUICK_REFERENCE.md
│   ├── ASK_AGENT_MODE_STATUS.md
│   └── INTENT_CLASSIFIER_SUMMARY.md
└── implementation/          # Implementation docs
    ├── FINAL_IMPLEMENTATION_SUMMARY.md
    └── IMPLEMENTATION_SUMMARY.md
```

### `/evoagentx` - Main Python Package
- Core AI agent functionality
- Workflow management
- Memory systems
- Optimization algorithms

### `/scripts` - Utility Scripts
- `start-dev.sh` - Development server startup
- `start-server.sh` - Production server startup
- `start-obsidian-server.sh` - Obsidian integration server
- `setup-obsidian.sh` - Obsidian setup script
- `end-dev.sh` - Development cleanup

### `/tests` - Python Tests
- Comprehensive test suite with 87% coverage
- Integration tests
- Unit tests for all modules
- Mock and fixture configurations

### `/typescript` - TypeScript Modules
```
typescript/
├── parsers/                 # Parser implementations
│   └── intelligenceParser.ts
├── tests/                   # TypeScript tests
│   ├── enhanced-parser.test.ts
│   ├── intelligenceParser.test.ts
│   └── testInsert.ts
└── db.ts                    # Database utilities
```

### `/vault-management` - Obsidian Integration
- `vault-management-api-client.ts` - API client for vault operations
- `vault-management-commands.ts` - Obsidian plugin commands
- `vault-management-types.ts` - TypeScript type definitions

## 🚀 Quick Start

### Development Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Start development server
./scripts/start-dev.sh
```

### Running Tests
```bash
# Python tests
python -m pytest tests/

# TypeScript tests
npm test

# All tests with coverage
python -m pytest tests/ --cov=evoagentx
```

### Building for Production
```bash
# Build frontend
cd client && npm run build

# Build backend
python setup.py build

# Deploy
./scripts/start-server.sh
```

## 🔧 Configuration Files

- `package.json` - Node.js project configuration
- `pyproject.toml` - Python project metadata
- `jest.config.js` - TypeScript test configuration
- `tsconfig.json` - TypeScript compiler settings
- `eslint.config.js` - Code linting rules
- `mkdocs.yml` - Documentation generation

## 📝 Key Features

1. **Modular Architecture** - Separated concerns across directories
2. **Comprehensive Testing** - 87% Python test coverage
3. **Type Safety** - Full TypeScript support
4. **Modern Tooling** - Latest development tools and practices
5. **Clear Documentation** - Organized and comprehensive docs
6. **Production Ready** - Deployment scripts and configurations

## 🧹 Cleanup Benefits

- **Reduced Clutter** - Files organized by purpose and type
- **Easier Navigation** - Logical directory structure
- **Better Maintainability** - Clear separation of concerns
- **Improved Testing** - Centralized test organization
- **Enhanced Development** - Better development experience

This reorganized structure maintains all functionality while providing a much cleaner and more maintainable codebase.
