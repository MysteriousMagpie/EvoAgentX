/**
 * Command Definitions for VaultPilot Vault Management
 * Add these commands to your main plugin's onload() method
 */

import { Command } from 'obsidian';

/**
 * Vault Management Commands
 * Add these to your plugin's command registration
 */
export const VAULT_MANAGEMENT_COMMANDS: Command[] = [
  {
    id: 'vaultpilot-vault-structure',
    name: 'View Vault Structure',
    callback: function() {
      // Open VaultStructureModal
      new VaultStructureModal(this.app, this).open();
    }
  },
  {
    id: 'vaultpilot-smart-search',
    name: 'Smart Vault Search',
    callback: function() {
      // Open SmartSearchModal
      new SmartSearchModal(this.app, this).open();
    }
  },
  {
    id: 'vaultpilot-file-operations',
    name: 'File Operations Manager',
    callback: function() {
      // Open FileOperationsModal
      new FileOperationsModal(this.app, this).open();
    }
  },
  {
    id: 'vaultpilot-organize-vault',
    name: 'AI Vault Organization',
    callback: function() {
      // Open VaultOrganizerModal
      new VaultOrganizerModal(this.app, this).open();
    }
  },
  {
    id: 'vaultpilot-batch-operations',
    name: 'Batch File Operations',
    callback: function() {
      // Open BatchOperationsModal
      new BatchOperationsModal(this.app, this).open();
    }
  },
  {
    id: 'vaultpilot-quick-search-selection',
    name: 'Quick Search Selected Text',
    editorCallback: function(editor) {
      const selection = editor.getSelection();
      if (selection.trim()) {
        const modal = new SmartSearchModal(this.app, this);
        modal.setInitialQuery(selection.trim());
        modal.open();
      } else {
        new Notice('Please select text to search for');
      }
    }
  },
  {
    id: 'vaultpilot-create-file-here',
    name: 'Create File Here',
    callback: function() {
      const activeFile = this.app.workspace.getActiveFile();
      const initialPath = activeFile ? activeFile.parent?.path || '' : '';
      const modal = new FileOperationsModal(this.app, this);
      modal.setInitialPath(initialPath);
      modal.setOperation('create');
      modal.open();
    }
  },
  {
    id: 'vaultpilot-analyze-current-folder',
    name: 'Analyze Current Folder Structure',
    callback: function() {
      const activeFile = this.app.workspace.getActiveFile();
      const folderPath = activeFile ? activeFile.parent?.path || '' : '';
      
      this.apiClient.getVaultStructure({
        include_content: false,
        max_depth: 2
      }).then(structure => {
        // Create analysis note
        const analysisContent = this.generateFolderAnalysis(structure, folderPath);
        const fileName = `Folder Analysis - ${folderPath || 'Root'} - ${new Date().toISOString().split('T')[0]}.md`;
        
        this.apiClient.createFile(fileName, analysisContent);
        new Notice('Folder analysis created');
      }).catch(error => {
        new Notice('Failed to analyze folder structure');
        console.error(error);
      });
    }
  },
  {
    id: 'vaultpilot-vault-health-check',
    name: 'Vault Health Check',
    callback: async function() {
      try {
        const structure = await this.apiClient.getVaultStructure({ include_content: false });
        const searchTest = await this.apiClient.searchVault({ query: 'test', max_results: 1 });
        
        const healthReport = `# Vault Health Check - ${new Date().toLocaleString()}

## Structure Analysis
- **Total Files**: ${structure.total_files}
- **Total Folders**: ${structure.total_folders}
- **Total Size**: ${(structure.total_size / 1024 / 1024).toFixed(2)} MB
- **Orphaned Files**: ${structure.orphaned_files.length}

## Search Performance
- **Search Response Time**: ${searchTest.search_time.toFixed(2)}s
- **Search Results**: ${searchTest.total_results} found

## Recommendations
${structure.orphaned_files.length > 0 ? '- Consider linking or organizing orphaned files' : '- No orphaned files found ✓'}
${structure.total_files > 1000 ? '- Large vault detected - consider folder organization' : '- Vault size is manageable ✓'}
${searchTest.search_time > 1 ? '- Search performance could be improved' : '- Search performance is good ✓'}

## Connection Status
- **Backend Connection**: ✓ Connected
- **Vault Management**: ✓ Available
- **Features**: Structure Analysis, Search, File Operations, Organization
`;

        const fileName = `Vault Health Check - ${new Date().toISOString().split('T')[0]}.md`;
        await this.apiClient.createFile(fileName, healthReport);
        
        // Open the health report
        const file = this.app.vault.getAbstractFileByPath(fileName);
        if (file) {
          await this.app.workspace.getLeaf().openFile(file);
        }
        
        new Notice('Vault health check completed');
      } catch (error) {
        new Notice('Health check failed - check backend connection');
        console.error(error);
      }
    }
  },
  {
    id: 'vaultpilot-backup-vault',
    name: 'Create Vault Backup',
    callback: async function() {
      try {
        const backupName = `vault-backup-${Date.now()}`;
        const result = await this.apiClient.createVaultBackup({
          backup_name: backupName,
          include_settings: true,
          compress: true
        });
        
        if (result.success) {
          new Notice(`Backup created: ${result.backup_path}`);
        } else {
          new Notice('Backup creation failed');
        }
      } catch (error) {
        new Notice('Backup feature not available');
        console.error(error);
      }
    }
  }
];

/**
 * Register commands in your plugin's onload method:
 * 
 * onload() {
 *   // Register vault management commands
 *   VAULT_MANAGEMENT_COMMANDS.forEach(command => {
 *     this.addCommand({
 *       ...command,
 *       callback: command.callback.bind(this),
 *       editorCallback: command.editorCallback?.bind(this)
 *     });
 *   });
 * }
 */

// === RIBBON ICONS ===

export const VAULT_MANAGEMENT_RIBBON_ICONS = [
  {
    icon: 'folder-tree',
    title: 'View Vault Structure',
    callback: 'vaultpilot-vault-structure'
  },
  {
    icon: 'search',
    title: 'Smart Search',
    callback: 'vaultpilot-smart-search'
  },
  {
    icon: 'settings',
    title: 'File Operations',
    callback: 'vaultpilot-file-operations'
  }
];

/**
 * Add ribbon icons in your plugin's onload method:
 * 
 * onload() {
 *   if (this.settings.enableVaultManagement) {
 *     VAULT_MANAGEMENT_RIBBON_ICONS.forEach(icon => {
 *       this.addRibbonIcon(icon.icon, icon.title, () => {
 *         this.app.commands.executeCommandById(icon.callback);
 *       });
 *     });
 *   }
 * }
 */

// === CONTEXT MENU ITEMS ===

export const VAULT_MANAGEMENT_CONTEXT_MENU = {
  // File context menu items
  file: [
    {
      title: 'AI Search Related',
      icon: 'search',
      callback: (file: TFile) => {
        const query = file.basename;
        new SmartSearchModal(this.app, this).setInitialQuery(query).open();
      }
    },
    {
      title: 'Analyze File Context',
      icon: 'brain-circuit',
      callback: async (file: TFile) => {
        const content = await this.app.vault.read(file);
        const searchQuery = content.split(' ').slice(0, 10).join(' ');
        new SmartSearchModal(this.app, this).setInitialQuery(searchQuery).open();
      }
    }
  ],
  
  // Folder context menu items
  folder: [
    {
      title: 'Analyze Folder Structure',
      icon: 'folder-tree',
      callback: (folder: TFolder) => {
        new VaultStructureModal(this.app, this).setFocusPath(folder.path).open();
      }
    },
    {
      title: 'Batch Operations on Folder',
      icon: 'layers',
      callback: (folder: TFolder) => {
        new BatchOperationsModal(this.app, this).setTargetFolder(folder.path).open();
      }
    }
  ]
};

// === HOTKEYS ===

export const VAULT_MANAGEMENT_HOTKEYS = {
  'vaultpilot-smart-search': {
    modifiers: ['Mod', 'Shift'],
    key: 'F'
  },
  'vaultpilot-vault-structure': {
    modifiers: ['Mod', 'Shift'],
    key: 'T'
  },
  'vaultpilot-quick-search-selection': {
    modifiers: ['Mod', 'Alt'],
    key: 'F'
  }
};

/**
 * Register hotkeys in your plugin's onload method:
 * 
 * onload() {
 *   Object.entries(VAULT_MANAGEMENT_HOTKEYS).forEach(([commandId, hotkey]) => {
 *     this.addCommand({
 *       id: commandId,
 *       name: VAULT_MANAGEMENT_COMMANDS.find(cmd => cmd.id === commandId)?.name || commandId,
 *       hotkeys: [hotkey],
 *       callback: () => this.app.commands.executeCommandById(commandId)
 *     });
 *   });
 * }
 */

// === HELPER FUNCTIONS ===

export function generateFolderAnalysis(structure: VaultStructureResponse, focusPath: string): string {
  return `# Folder Analysis: ${focusPath || 'Root'}

Generated on: ${new Date().toLocaleString()}

## Overview
- **Total Files**: ${structure.total_files}
- **Total Folders**: ${structure.total_folders}
- **Total Size**: ${(structure.total_size / 1024).toFixed(2)} KB

## Structure
${renderFolderStructure(structure.structure, focusPath)}

## Recent Activity
${structure.recent_files.slice(0, 5).map(file => 
  `- **${file.name}** (${file.modified}) - ${file.size} bytes`
).join('\n')}

## Recommendations
- Consider organizing files by topic or date
- Check for duplicate or similar files
- Review file naming conventions
- Link related content for better discoverability

---
*Generated by VaultPilot Vault Management*`;
}

function renderFolderStructure(folder: VaultFolderInfo, focusPath: string, level = 0): string {
  const indent = '  '.repeat(level);
  let result = `${indent}- 📁 **${folder.name}**\n`;
  
  folder.children.forEach(child => {
    if (child.type === 'folder') {
      result += renderFolderStructure(child as VaultFolderInfo, focusPath, level + 1);
    } else {
      const file = child as any;
      result += `${indent}  - 📄 ${file.name} (${file.size} bytes)\n`;
    }
  });
  
  return result;
}
