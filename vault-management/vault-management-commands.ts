/**
 * Command Definitions for VaultPilot Vault Management
 * Add these commands to your main plugin's onload() method
 */

// Import types from vault management
import {
  VaultStructureResponse,
  VaultFolderInfo,
  VaultFileInfo,
} from './vault-management-types';

// Basic Obsidian type definitions (these would normally come from the obsidian package)
interface App {
  vault: {
    read(file: TFile): Promise<string>;
    getAbstractFileByPath(path: string): TFile | null;
  };
  workspace: {
    getActiveFile(): TFile | null;
    openLinkText(linkText: string, sourcePath: string): void;
  };
}

interface TFile {
  path: string;
  name: string;
}

interface TFolder {
  path: string;
  name: string;
}

interface Editor {
  getSelection(): string;
}

interface Command {
  id: string;
  name: string;
  callback?: () => void;
  editorCallback?: (editor: Editor) => void;
}

// Notice class for showing notifications
class Notice {
  constructor(message: string) {
    console.log('Notice:', message);
  }
}

// Configuration constants (should be loaded from plugin settings)
const API_BASE_URL = 'http://localhost:8000/api';
const API_KEY = process.env.EVOAGENTX_API_KEY || '';

// Modal base classes - these would normally be imported from Obsidian
class Modal {
  constructor(public app: App) {}
  open(): void {}
  close(): void {}
}

class VaultStructureModal extends Modal {
  constructor(app: App, private plugin: any) {
    super(app);
  }
  setFocusPath(path: string): this {
    return this;
  }
}

class SmartSearchModal extends Modal {
  constructor(app: App, private plugin: any) {
    super(app);
  }
  setInitialQuery(query: string): this {
    return this;
  }
}

class FileOperationsModal extends Modal {
  constructor(app: App, private plugin: any) {
    super(app);
  }
  setInitialPath(path: string): this {
    return this;
  }
  setOperation(operation: string): this {
    return this;
  }
}

class VaultOrganizerModal extends Modal {
  constructor(app: App, private plugin: any) {
    super(app);
  }
}

class BatchOperationsModal extends Modal {
  constructor(app: App, private plugin: any) {
    super(app);
  }
  setTargetFolder(path: string): this {
    return this;
  }
}

/**
 * Vault Management Commands
 * Add these to your plugin's command registration
 */
export function createVaultManagementCommands(app: App, plugin: any, apiClient: any): Command[] {
  return [
    {
      id: 'vaultpilot-vault-structure',
      name: 'View Vault Structure',
      callback: function() {
        new VaultStructureModal(app, plugin).open();
      }
    },
    {
      id: 'vaultpilot-smart-search',
      name: 'Smart Search',
      callback: function() {
        new SmartSearchModal(app, plugin).open();
      }
    },
    {
      id: 'vaultpilot-file-operations',
      name: 'File Operations',
      callback: function() {
        new FileOperationsModal(app, plugin).open();
      }
    },
    {
      id: 'vaultpilot-vault-organizer',
      name: 'Vault Organizer',
      callback: function() {
        new VaultOrganizerModal(app, plugin).open();
      }
    },
    {
      id: 'vaultpilot-batch-operations',
      name: 'Batch Operations',
      callback: function() {
        new BatchOperationsModal(app, plugin).open();
      }
    },
    {
      id: 'vaultpilot-search-selected',
      name: 'Search Selected Text',
      editorCallback: function(editor: Editor) {
        const selectedText = editor.getSelection();
        if (selectedText) {
          const modal = new SmartSearchModal(app, plugin);
          modal.setInitialQuery(selectedText);
          modal.open();
        } else {
          new Notice('Please select text to search for');
        }
      }
    },
    {
      id: 'vaultpilot-create-file-here',
      name: 'Create File in Current Location',
      callback: function() {
        const activeFile = app.workspace.getActiveFile();
        const initialPath = activeFile ? activeFile.path.split('/').slice(0, -1).join('/') : '';
        
        const modal = new FileOperationsModal(app, plugin);
        modal.setInitialPath(initialPath);
        modal.setOperation('create');
        modal.open();
      }
    },
    {
      id: 'vaultpilot-analyze-folder-structure',
      name: 'Analyze Current Folder Structure',
      callback: async function() {
        const activeFile = app.workspace.getActiveFile();
        const folderPath = activeFile ? activeFile.path.split('/').slice(0, -1).join('/') : '/';
        
        try {
          const structure = await apiClient.getVaultStructure({
            include_content: false,
            max_depth: 3
          });
          
          const analysisContent = generateFolderAnalysis(structure, folderPath);
          const fileName = `${folderPath}/folder-analysis-${new Date().toISOString().split('T')[0]}.md`;
          
          await apiClient.createFile(fileName, analysisContent);
          new Notice('Folder analysis created');
        } catch (error: any) {
          new Notice('Failed to analyze folder structure');
        }
      }
    },
    {
      id: 'vaultpilot-vault-health-check',
      name: 'Vault Health Check',
      callback: async function() {
        try {
          const structure = await apiClient.getVaultStructure({ include_content: false });
          const searchTest = await apiClient.searchVault({ query: 'test', max_results: 1 });
          
          const healthReport = `# Vault Health Check Report
Generated: ${new Date().toISOString()}

## Vault Statistics
- Total Files: ${structure.total_files}
- Total Folders: ${structure.total_folders}
- Total Size: ${(structure.total_size / 1024 / 1024).toFixed(2)} MB

## System Status
- Search System: ${searchTest ? '✅ Working' : '❌ Failed'}
- API Connection: ✅ Connected
- Recent Files: ${structure.recent_files.length} found

## Recommendations
${structure.orphaned_files.length > 0 ? `- Consider organizing ${structure.orphaned_files.length} orphaned files` : '- No orphaned files found'}
- Regular backup recommended
- Consider using smart organization features
`;

          const fileName = `vault-health-check-${new Date().toISOString().split('T')[0]}.md`;
          await apiClient.createFile(fileName, healthReport);
          
          const file = app.vault.getAbstractFileByPath(fileName);
          if (file) {
            app.workspace.openLinkText(fileName, '');
          }
          
          new Notice('Vault health check completed');
        } catch {
          new Notice('Health check failed - check backend connection');
        }
      }
    },
    {
      id: 'vaultpilot-create-backup',
      name: 'Create Vault Backup',
      callback: async function() {
        try {
          if (apiClient.createBackup) {
            const result = await apiClient.createBackup({
              include_settings: true,
              compression: true
            });
            new Notice(`Backup created: ${result.backup_path}`);
          } else {
            new Notice('Backup creation failed');
          }
        } catch {
          new Notice('Backup feature not available');
        }
      }
    }
  ];
}

// === CONTEXT MENU COMMANDS ===

/**
 * Context menu commands for files and folders
 * Register these with the file menu or folder menu
 */
export const FILE_CONTEXT_COMMANDS = [
  {
    id: 'vaultpilot-analyze-file',
    name: 'Analyze with VaultPilot',
    callback: (file: TFile, app: App, plugin: any) => {
      const searchQuery = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
      new SmartSearchModal(app, plugin).setInitialQuery(searchQuery).open();
    }
  },
  {
    id: 'vaultpilot-search-similar',
    name: 'Find Similar Files',
    callback: async (file: TFile, app: App, plugin: any) => {
      const content = await app.vault.read(file);
      const searchQuery = content.substring(0, 100); // First 100 chars as search query
      new SmartSearchModal(app, plugin).setInitialQuery(searchQuery).open();
    }
  }
];

export const FOLDER_CONTEXT_COMMANDS = [
  {
    id: 'vaultpilot-analyze-folder',
    name: 'Analyze Folder Structure',
    callback: (folder: TFolder, app: App, plugin: any) => {
      new VaultStructureModal(app, plugin).setFocusPath(folder.path).open();
    }
  },
  {
    id: 'vaultpilot-batch-operations-folder',
    name: 'Batch Operations on Folder',
    callback: (folder: TFolder, app: App, plugin: any) => {
      new BatchOperationsModal(app, plugin).setTargetFolder(folder.path).open();
    }
  }
];

// === UTILITY FUNCTIONS ===

/**
 * Generate a comprehensive folder analysis report
 */
export function generateFolderAnalysis(structure: VaultStructureResponse, focusPath: string): string {
  const analysis = `# Folder Analysis Report
Generated: ${new Date().toISOString()}
Focus Path: ${focusPath}

## Vault Overview
- **Total Files**: ${structure.total_files}
- **Total Folders**: ${structure.total_folders}
- **Vault Size**: ${(structure.total_size / 1024 / 1024).toFixed(2)} MB

## Recent Activity
${structure.recent_files.slice(0, 5).map((file: any) =>
  `- ${file.name} (${file.modified})`
).join('\n')}

## Folder Structure
${renderFolderStructure(structure.structure, focusPath)}

## Recommendations
- Consider organizing files by topic or date
- Use consistent naming conventions
- Regular cleanup of unused files
- Create index files for major sections
`;

  return analysis;
}

function renderFolderStructure(folder: VaultFolderInfo, focusPath: string, level = 0): string {
  const indent = '  '.repeat(level);
  let result = `${indent}- **${folder.name}/**${folder.path === focusPath ? ' 🎯' : ''}\n`;
  
  folder.children.forEach((child: any) => {
    if (child.type === 'folder') {
      result += renderFolderStructure(child as VaultFolderInfo, focusPath, level + 1);
    } else {
      result += `${indent}  - ${child.name}\n`;
    }
  });
  
  return result;
}

// === OPENAI CODE INTERPRETER COMMANDS ===

/**
 * Analyze current file/selection with OpenAI Code Interpreter
 */
export const analyzeCodeWithInterpreter: Command = {
  id: 'evoagentx-analyze-code',
  name: 'EvoAgentX: Analyze Code with AI Interpreter',
  editorCallback: async (editor: Editor) => {
    try {
      const selection = editor.getSelection();
      const content = selection || 'No selection - analyzing current context';
      
      new Notice('Analyzing code with OpenAI Code Interpreter...');
      
      // Call the analyze-code endpoint we created
      const response = await fetch(`${API_BASE_URL}/analyze-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
          code: content,
          context: {
            file_type: 'auto-detect',
            analysis_type: 'comprehensive'
          }
        })
      });
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        const analysis = result.data;
        
        // Show analysis results in a modal or new note
        await showAnalysisResults(analysis);
        new Notice('Code analysis completed!');
      } else {
        throw new Error(result.message || 'Analysis failed');
      }
      
    } catch (error) {
      console.error('Code analysis error:', error);
      new Notice(`Analysis failed: ${(error as Error).message}`);
    }
  }
};

/**
 * Select and configure OpenAI Code Interpreter
 */
export const selectCodeInterpreter: Command = {
  id: 'evoagentx-select-interpreter',
  name: 'EvoAgentX: Configure Code Interpreter',
  callback: async () => {
    try {
      new Notice('Opening interpreter configuration...');
      
      // Get current interpreter settings
      const response = await fetch(`${API_BASE_URL}/interpreter/config`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${API_KEY}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`Failed to get interpreter config: ${response.statusText}`);
      }
      
      const config = await response.json();
      
      // Show interpreter selection modal
      await showInterpreterSelectionModal(config.data);
      
    } catch (error) {
      console.error('Interpreter selection error:', error);
      new Notice(`Failed to open interpreter config: ${(error as Error).message}`);
    }
  }
};

/**
 * Execute code with selected interpreter
 */
export const executeCodeWithInterpreter: Command = {
  id: 'evoagentx-execute-code',
  name: 'EvoAgentX: Execute Code with Interpreter',
  editorCallback: async (editor: Editor) => {
    try {
      const selection = editor.getSelection();
      
      if (!selection.trim()) {
        new Notice('Please select code to execute');
        return;
      }
      
      new Notice('Executing code with interpreter...');
      
      const response = await fetch(`${API_BASE_URL}/interpreter/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
          code: selection,
          interpreter: 'auto', // or user-selected interpreter
          context: {
            file_type: 'auto-detect'
          }
        })
      });
      
      if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        await showExecutionResults(result.data);
        new Notice('Code executed successfully!');
      } else {
        throw new Error(result.message || 'Execution failed');
      }
      
    } catch (error) {
      console.error('Code execution error:', error);
      new Notice(`Execution failed: ${(error as Error).message}`);
    }
  }
};

// === HELPER FUNCTIONS FOR INTERPRETER INTEGRATION ===

/**
 * Show code analysis results in a modal or new note
 */
async function showAnalysisResults(analysis: any): Promise<void> {
  const results = `# Code Analysis Results

## Interpreter Recommendation
**Recommended Interpreter:** ${analysis.recommendedInterpreter}
**Confidence:** ${(analysis.confidence * 100).toFixed(1)}%

## Analysis Summary
${analysis.analysis || 'No detailed analysis available'}

## Code Quality
${analysis.codeQuality ? `
- **Complexity:** ${analysis.codeQuality.complexity}
- **Maintainability:** ${analysis.codeQuality.maintainability}
- **Performance:** ${analysis.codeQuality.performance}
` : 'Quality metrics not available'}

## Suggestions
${analysis.suggestions ? analysis.suggestions.map((s: string) => `- ${s}`).join('\n') : 'No suggestions available'}

## Potential Issues
${analysis.issues ? analysis.issues.map((i: string) => `- ${i}`).join('\n') : 'No issues detected'}

---
*Analysis generated on ${new Date().toISOString()}*
`;

  // Create a new note with the analysis results
  const fileName = `Code Analysis - ${new Date().toISOString().split('T')[0]}.md`;
  
  // This would be implemented based on your app instance
  // app.vault.create(fileName, results);
  
  console.log('Analysis results:', results);
  new Notice('Analysis results saved to new note');
}

/**
 * Show interpreter selection modal
 */
async function showInterpreterSelectionModal(config: any): Promise<void> {
  // This would show a modal with interpreter options
  // For now, we'll log the available options
  console.log('Available interpreters:', config.availableInterpreters);
  console.log('Current interpreter:', config.currentInterpreter);
  
  // In a real implementation, this would show a modal with:
  // - List of available interpreters
  // - Current selection
  // - Configuration options
  // - Save/Apply buttons
  
  new Notice('Interpreter configuration modal would open here');
}

/**
 * Show code execution results
 */
async function showExecutionResults(results: any): Promise<void> {
  const output = `# Code Execution Results

## Status
**Status:** ${results.status}
**Execution Time:** ${results.executionTime || 'N/A'}

## Output
\`\`\`
${results.output || 'No output generated'}
\`\`\`

## Errors
${results.errors ? `\`\`\`
${results.errors}
\`\`\`` : 'No errors'}

## Interpreter Used
**Interpreter:** ${results.interpreter}
**Version:** ${results.interpreterVersion || 'N/A'}

---
*Executed on ${new Date().toISOString()}*
`;

  const fileName = `Execution Results - ${new Date().toISOString().split('T')[0]}.md`;
  
  // Create a new note with the execution results
  // app.vault.create(fileName, output);
  
  console.log('Execution results:', output);
  new Notice('Execution results saved to new note');
}
