# Vault Management Integration

This document explains the new vault management capabilities that enable agents to access, analyze, and modify Obsidian vault structure and files.

## Overview

The vault management system provides comprehensive tools for:
- **Vault Structure Access**: Read and analyze folder hierarchies and file organization
- **File Operations**: Create, update, delete, move, and copy files
- **Intelligent Search**: Search vault content with AI-powered analysis
- **Batch Operations**: Perform multiple file operations efficiently
- **Vault Reorganization**: AI-assisted vault structure optimization

## Components

### 1. VaultManagerAgent (`evoagentx/agents/vault_manager.py`)

A specialized agent that combines multiple AI sub-agents with direct file operation tools:

- **Structure Agent**: Analyzes vault organization and provides recommendations
- **File Manager Agent**: Plans file operations based on user requests
- **Search Agent**: Provides intelligent analysis of search results
- **Organization Agent**: Creates comprehensive reorganization strategies

### 2. Vault Tools (`evoagentx/tools/vault_tools_simple.py`)

Core utilities for vault operations:
- `get_vault_structure()`: Scan and analyze vault hierarchy
- `create_file()`, `update_file()`, `delete_file()`: Basic file operations
- `move_file()`, `copy_file()`: File manipulation operations
- `search_vault()`: Content and metadata search
- `batch_file_operations()`: Efficient batch processing

### 3. API Endpoints (`server/api/obsidian.py`)

REST API endpoints for vault management:

#### `POST /api/obsidian/vault/structure`
Get comprehensive vault structure with AI analysis.

**Request:**
```json
{
  "include_content": false,
  "max_depth": null,
  "file_types": ["md", "txt"]
}
```

**Response:**
```json
{
  "vault_name": "MyVault",
  "total_files": 42,
  "total_folders": 8,
  "total_size": 1024000,
  "structure": { /* folder hierarchy */ },
  "recent_files": [ /* recent file info */ ],
  "orphaned_files": [ /* unlinked files */ ]
}
```

#### `POST /api/obsidian/vault/file/operation`
Perform individual file operations.

**Request:**
```json
{
  "operation": "create",
  "file_path": "/path/to/new/file.md",
  "content": "# New File\n\nContent here...",
  "create_missing_folders": true
}
```

#### `POST /api/obsidian/vault/file/batch`
Perform multiple file operations efficiently.

**Request:**
```json
{
  "operations": [
    {
      "operation": "create",
      "file_path": "/notes/new1.md",
      "content": "Content 1"
    },
    {
      "operation": "move",
      "file_path": "/notes/old.md",
      "destination_path": "/archive/old.md"
    }
  ],
  "continue_on_error": true
}
```

#### `POST /api/obsidian/vault/search`
Intelligent search with AI analysis.

**Request:**
```json
{
  "query": "machine learning concepts",
  "search_type": "content",
  "file_types": ["md"],
  "max_results": 20,
  "include_context": true
}
```

#### `POST /api/obsidian/vault/organize`
AI-assisted vault reorganization planning.

**Request:**
```json
{
  "organization_goal": "Organize notes by topic and create a better hierarchy",
  "preferences": {
    "folder_structure": "topic-based",
    "naming_convention": "kebab-case"
  },
  "dry_run": true
}
```

## Usage Examples

### Python Usage

```python
from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig

# Initialize
llm_config = OpenAILLMConfig(model="gpt-4o-mini", openai_key="your-key")
vault_manager = VaultManagerAgent(llm_config=llm_config, vault_root="/path/to/vault")

# Get vault structure with AI analysis
structure = vault_manager.get_vault_structure(include_content=True)
print(structure["ai_analysis"]["recommendations"])

# Create files
result = vault_manager.create_file("new-note.md", "# New Note\n\nContent here...")

# Intelligent search
search_results = vault_manager.intelligent_search("machine learning", "content")
print(search_results["ai_insights"]["knowledge_gaps"])

# Batch operations
operations = [
    {"operation": "create", "file_path": "note1.md", "content": "Content 1"},
    {"operation": "create", "file_path": "note2.md", "content": "Content 2"}
]
batch_result = vault_manager.batch_file_operations(operations)
```

### API Usage

```bash
# Get vault structure
curl -X POST "http://localhost:8000/api/obsidian/vault/structure" \\
  -H "Content-Type: application/json" \\
  -d '{"include_content": false, "max_depth": 3}'

# Create a file
curl -X POST "http://localhost:8000/api/obsidian/vault/file/operation" \\
  -H "Content-Type: application/json" \\
  -d '{
    "operation": "create",
    "file_path": "/notes/new-note.md",
    "content": "# New Note\\n\\nThis is a new note.",
    "create_missing_folders": true
  }'

# Search vault
curl -X POST "http://localhost:8000/api/obsidian/vault/search" \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "important concepts",
    "search_type": "content",
    "max_results": 10
  }'
```

## Integration with Obsidian Plugin

The vault management system integrates with the Obsidian plugin to provide:

1. **Real-time Vault Access**: Agents can now read and modify vault structure
2. **File Operations**: Create, edit, move, and organize files through agent commands
3. **Smart Search**: AI-powered search with context and recommendations
4. **Bulk Operations**: Efficiently handle large-scale vault reorganization

## Error Handling

The system includes comprehensive error handling:

- **File System Errors**: Permission issues, missing files, etc.
- **Validation Errors**: Invalid paths, unsupported operations
- **Batch Operation Errors**: Continue-on-error support for bulk operations
- **AI Processing Errors**: Fallback to basic operations when AI fails

## Security Considerations

- **Path Validation**: All file paths are validated to prevent directory traversal
- **Permission Checks**: Respects file system permissions
- **Vault Boundaries**: Operations are restricted to the specified vault root
- **Content Filtering**: File content is validated before processing

## Future Enhancements

Planned improvements include:
- **Backup/Restore**: Automated vault backup before major operations
- **Version Control**: Integration with git for change tracking
- **Template System**: Smart file creation from templates
- **Link Management**: Automatic link updating during file moves
- **Conflict Resolution**: AI-assisted resolution of file conflicts

## Troubleshooting

### Common Issues

1. **"No access to vault structure"**: 
   - Ensure vault_root is correctly set
   - Check file system permissions
   - Verify vault path exists

2. **API endpoint errors**:
   - Check server logs for detailed error messages
   - Verify request schema matches documentation
   - Ensure OpenAI API key is configured

3. **File operation failures**:
   - Check file permissions
   - Verify paths are within vault boundaries
   - Ensure parent directories exist (or use `create_missing_folders`)

### Debug Mode

Enable debug logging to see detailed operation information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show detailed information about file operations, AI processing, and error conditions.
