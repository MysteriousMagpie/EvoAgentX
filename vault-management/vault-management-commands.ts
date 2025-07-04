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
