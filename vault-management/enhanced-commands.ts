/**
 * Enhanced VaultPilot Commands with Keyboard Shortcuts and Performance Optimizations
 * 
 * This file extends the original vault management commands with:
 * - Standardized keyboard shortcuts
 * - Progress indicators for long operations
 * - Response time optimizations
 * - Enhanced user experience features
 */

import { App, Editor, Command, Notice, Modal, TFile } from 'obsidian';
import { VaultPilotEnhancementManager } from './enhanced-ui-components';

// Enhanced Modal Classes with Progress Indicators

class EnhancedVaultStructureModal extends Modal {
    private enhancementManager: VaultPilotEnhancementManager;

    constructor(app: App, plugin: any, enhancementManager: VaultPilotEnhancementManager) {
        super(app);
        this.enhancementManager = enhancementManager;
    }

    async onOpen() {
        const { contentEl } = this;
        contentEl.createEl('h2', { text: 'Vault Structure Analysis' });
        
        // Create loading indicator
        const loadingEl = contentEl.createEl('div', { 
            text: 'Analyzing vault structure...',
            cls: 'loading-indicator'
        });

        try {
            // Use optimized request
            const result = await this.enhancementManager.makeOptimizedRequest(
                '/api/obsidian/enhanced/vault/analyze',
                { vault_path: '/' }
            );

            loadingEl.remove();
            this.displayResults(contentEl, result.data);
        } catch (error: any) {
            loadingEl.textContent = `Error: ${error.message}`;
        }
    }

    private displayResults(container: HTMLElement, data: any) {
        const resultsEl = container.createEl('div', { cls: 'vault-analysis-results' });
        
        // Display analysis results
        resultsEl.createEl('h3', { text: 'Analysis Results' });
        
        const statsEl = resultsEl.createEl('div', { cls: 'vault-stats' });
        statsEl.createEl('p', { text: `Total Files: ${data.analysis.total_files}` });
        statsEl.createEl('p', { text: `Total Folders: ${data.analysis.total_folders}` });
        
        // Display insights
        const insightsEl = resultsEl.createEl('div', { cls: 'vault-insights' });
        insightsEl.createEl('h4', { text: 'Insights' });
        
        const insightsList = insightsEl.createEl('ul');
        data.analysis.insights.forEach((insight: string) => {
            insightsList.createEl('li', { text: insight });
        });

        // Display optimization suggestions  
        const suggestionsEl = resultsEl.createEl('div', { cls: 'optimization-suggestions' });
        suggestionsEl.createEl('h4', { text: 'Optimization Suggestions' });
        
        const suggestionsList = suggestionsEl.createEl('ul');
        data.analysis.optimization_suggestions.forEach((suggestion: string) => {
            suggestionsList.createEl('li', { text: suggestion });
        });

        // Display performance metrics
        if (data.performance) {
            const perfEl = resultsEl.createEl('div', { cls: 'performance-metrics' });
            perfEl.createEl('h4', { text: 'Performance' });
            perfEl.createEl('p', { text: `Response Time: ${(data.performance.response_time * 1000).toFixed(0)}ms` });
            perfEl.createEl('p', { text: `Cache Hit: ${data.performance.cache_hit ? 'Yes' : 'No'}` });
            
            if (data.performance.optimizations_applied.length > 0) {
                perfEl.createEl('p', { text: `Optimizations: ${data.performance.optimizations_applied.join(', ')}` });
            }
        }
    }
}

class EnhancedSmartSearchModal extends Modal {
    private enhancementManager: VaultPilotEnhancementManager;
    private initialQuery: string = '';

    constructor(app: App, plugin: any, enhancementManager: VaultPilotEnhancementManager) {
        super(app);
        this.enhancementManager = enhancementManager;
    }

    setInitialQuery(query: string): this {
        this.initialQuery = query;
        return this;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.createEl('h2', { text: 'Smart Search' });

        // Create search input
        const searchContainer = contentEl.createEl('div', { cls: 'search-container' });
        const searchInput = searchContainer.createEl('input', {
            type: 'text',
            placeholder: 'Enter search query...',
            value: this.initialQuery
        });

        searchInput.style.cssText = `
            width: 100%;
            padding: 8px 12px;
            margin-bottom: 16px;
            border: 1px solid var(--background-modifier-border);
            border-radius: 4px;
            font-size: 14px;
        `;

        // Create search button
        const searchButton = searchContainer.createEl('button', { 
            text: 'Search (Ctrl+Enter)',
            cls: 'mod-cta'
        });

        // Results container
        const resultsEl = contentEl.createEl('div', { cls: 'search-results' });

        // Search handler
        const performSearch = async () => {
            const query = searchInput.value.trim();
            if (!query) return;

            resultsEl.empty();
            resultsEl.createEl('div', { text: 'Searching...', cls: 'loading' });

            try {
                const result = await this.enhancementManager.makeOptimizedRequest(
                    '/api/obsidian/vault/search',
                    { 
                        query,
                        search_type: 'content',
                        max_results: 20
                    }
                );

                this.displaySearchResults(resultsEl, result.data.results);
            } catch (error: any) {
                resultsEl.empty();
                resultsEl.createEl('div', { 
                    text: `Search failed: ${error.message}`,
                    cls: 'error'
                });
            }
        };

        // Event listeners
        searchButton.addEventListener('click', performSearch);
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                performSearch();
            } else if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Focus input
        setTimeout(() => searchInput.focus(), 100);
    }

    private displaySearchResults(container: HTMLElement, results: any[]) {
        container.empty();
        
        if (results.length === 0) {
            container.createEl('div', { text: 'No results found', cls: 'no-results' });
            return;
        }

        container.createEl('h3', { text: `Found ${results.length} results` });

        const resultsList = container.createEl('div', { cls: 'results-list' });
        
        results.forEach(result => {
            const resultEl = resultsList.createEl('div', { cls: 'search-result-item' });
            
            const titleEl = resultEl.createEl('div', { 
                text: result.file_path,
                cls: 'result-title'
            });
            
            titleEl.style.cssText = `
                font-weight: bold;
                margin-bottom: 4px;
                cursor: pointer;
                color: var(--interactive-accent);
            `;

            titleEl.addEventListener('click', () => {
                this.app.workspace.openLinkText(result.file_path, '');
                this.close();
            });

            if (result.context) {
                resultEl.createEl('div', { 
                    text: result.context,
                    cls: 'result-context'
                });
            }

            if (result.score) {
                resultEl.createEl('div', { 
                    text: `Relevance: ${(result.score * 100).toFixed(0)}%`,
                    cls: 'result-score'
                });
            }
        });
    }
}

class EnhancedWorkflowModal extends Modal {
    private enhancementManager: VaultPilotEnhancementManager;

    constructor(app: App, plugin: any, enhancementManager: VaultPilotEnhancementManager) {
        super(app);
        this.enhancementManager = enhancementManager;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.createEl('h2', { text: 'Workflow Execution' });

        // Create goal input
        const goalContainer = contentEl.createEl('div', { cls: 'goal-container' });
        goalContainer.createEl('label', { text: 'Goal:' });
        
        const goalInput = goalContainer.createEl('textarea', {
            placeholder: 'Describe what you want to accomplish...'
        });

        goalInput.style.cssText = `
            width: 100%;
            height: 80px;
            padding: 8px;
            margin: 8px 0 16px 0;
            border: 1px solid var(--background-modifier-border);
            border-radius: 4px;
            resize: vertical;
        `;

        // Execute button
        const executeButton = contentEl.createEl('button', {
            text: 'Execute Workflow (Ctrl+Enter)',
            cls: 'mod-cta'
        });

        // Results container
        const resultsEl = contentEl.createEl('div', { cls: 'workflow-results' });

        // Execute handler
        const executeWorkflow = async () => {
            const goal = goalInput.value.trim();
            if (!goal) {
                new Notice('Please enter a goal for the workflow');
                return;
            }

            executeButton.disabled = true;
            executeButton.textContent = 'Executing...';

            try {
                const result = await this.enhancementManager.makeOptimizedRequest(
                    '/api/obsidian/enhanced/workflow',
                    { goal, context: {} }
                );

                this.displayWorkflowResults(resultsEl, result.data);
            } catch (error: any) {
                resultsEl.empty();
                resultsEl.createEl('div', { 
                    text: `Workflow failed: ${error.message}`,
                    cls: 'error'
                });
            } finally {
                executeButton.disabled = false;
                executeButton.textContent = 'Execute Workflow (Ctrl+Enter)';
            }
        };

        // Event listeners
        executeButton.addEventListener('click', executeWorkflow);
        goalInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                executeWorkflow();
            }
        });

        // Focus input
        setTimeout(() => goalInput.focus(), 100);
    }

    private displayWorkflowResults(container: HTMLElement, data: any) {
        container.empty();
        
        container.createEl('h3', { text: 'Workflow Completed' });
        
        const statusEl = container.createEl('div', { cls: 'workflow-status' });
        statusEl.createEl('p', { text: `Status: ${data.status}` });
        statusEl.createEl('p', { text: `Operation ID: ${data.operation_id}` });
        statusEl.createEl('p', { text: `Execution Time: ${(data.execution_time * 1000).toFixed(0)}ms` });

        if (data.optimizations_applied && data.optimizations_applied.length > 0) {
            statusEl.createEl('p', { text: `Optimizations: ${data.optimizations_applied.join(', ')}` });
        }

        // Display keyboard shortcuts info
        const shortcutsEl = container.createEl('div', { cls: 'workflow-shortcuts' });
        shortcutsEl.createEl('h4', { text: 'Available Actions' });
        
        Object.entries(data.keyboard_shortcuts).forEach(([action, shortcut]) => {
            shortcutsEl.createEl('p', { text: `${action}: ${shortcut}` });
        });
    }
}

// Enhanced Command Creation Function
export function createEnhancedVaultPilotCommands(
    app: App, 
    plugin: any, 
    enhancementManager: VaultPilotEnhancementManager
): Command[] {
    
    return [
        // === CORE ENHANCED COMMANDS ===
        {
            id: 'vaultpilot-enhanced-vault-structure',
            name: 'View Enhanced Vault Structure',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'v' }],
            callback: () => {
                new EnhancedVaultStructureModal(app, plugin, enhancementManager).open();
            }
        },

        {
            id: 'vaultpilot-enhanced-smart-search',
            name: 'Enhanced Smart Search',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 's' }],
            callback: () => {
                new EnhancedSmartSearchModal(app, plugin, enhancementManager).open();
            }
        },

        {
            id: 'vaultpilot-enhanced-workflow',
            name: 'Enhanced Workflow Execution',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'w' }],
            callback: () => {
                new EnhancedWorkflowModal(app, plugin, enhancementManager).open();
            }
        },

        // === AI-ENHANCED COMMANDS ===
        {
            id: 'vaultpilot-enhanced-chat',
            name: 'Enhanced AI Chat',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'c' }],
            callback: async () => {
                // Open enhanced chat modal with optimized backend
                const result = await enhancementManager.makeOptimizedRequest(
                    '/api/obsidian/enhanced/chat',
                    { 
                        message: 'Hello! How can I help you with your vault today?',
                        conversation_id: `chat_${Date.now()}`
                    }
                );
                
                new Notice(`Chat response: ${result.data.message}`);
            }
        },

        {
            id: 'vaultpilot-enhanced-copilot',
            name: 'Enhanced AI Copilot',
            hotkeys: [{ modifiers: ['Ctrl'], key: ' ' }],
            editorCallback: async (editor: Editor) => {
                const cursor = editor.getCursor();
                const text = editor.getValue();
                const position = editor.posToOffset(cursor);

                try {
                    const result = await enhancementManager.makeOptimizedRequest(
                        '/api/obsidian/enhanced/copilot',
                        { 
                            text,
                            cursor_position: position,
                            context: {}
                        }
                    );

                    // Display suggestions
                    const suggestions = result.data.suggestions;
                    if (suggestions && suggestions.length > 0) {
                        const suggestion = suggestions[0];
                        
                        // Insert suggestion at cursor
                        editor.replaceRange(
                            suggestion,
                            cursor,
                            cursor
                        );

                        new Notice(`Copilot suggestion applied (${result.data.response_time.toFixed(0)}ms)`);
                    }
                } catch (error: any) {
                    new Notice(`Copilot error: ${error.message}`);
                }
            }
        },

        // === QUICK ACTIONS ===
        {
            id: 'vaultpilot-quick-note-enhanced',
            name: 'Quick Note (Enhanced)',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'n' }],
            callback: async () => {
                const fileName = `Quick Note ${new Date().toISOString().slice(0, 19)}.md`;
                const content = `# Quick Note\n\nCreated: ${new Date().toLocaleString()}\n\n`;
                
                await app.vault.create(fileName, content);
                const file = app.vault.getAbstractFileByPath(fileName);
                if (file) {
                    app.workspace.openLinkText(fileName, '');
                }
                
                new Notice(`Quick note created: ${fileName}`);
            }
        },

        {
            id: 'vaultpilot-task-from-selection-enhanced',
            name: 'Create Task from Selection (Enhanced)',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 't' }],
            editorCallback: async (editor: Editor) => {
                const selection = editor.getSelection();
                if (!selection) {
                    new Notice('Please select text to create a task');
                    return;
                }

                const taskContent = `## Task: ${selection}\n\n- [ ] ${selection}\n- Created: ${new Date().toLocaleString()}\n- Status: Not Started\n\n### Notes\n\n`;
                
                const fileName = `Task - ${selection.slice(0, 30).replace(/[^a-zA-Z0-9]/g, ' ')}.md`;
                
                try {
                    await app.vault.create(fileName, taskContent);
                    new Notice(`Task created: ${fileName}`);
                } catch (error: any) {
                    new Notice(`Failed to create task: ${error.message}`);
                }
            }
        },

        // === PERFORMANCE AND ANALYTICS ===
        {
            id: 'vaultpilot-performance-stats',
            name: 'Show Performance Statistics',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'p' }],
            callback: async () => {
                try {
                    const result = await enhancementManager.makeOptimizedRequest(
                        '/api/obsidian/enhanced/performance',
                        {}
                    );

                    const cacheStats = enhancementManager.getCacheStats();
                    
                    new Notice(
                        `Performance Stats:\n` +
                        `Cache Size: ${cacheStats.size} items\n` +
                        `Active Requests: ${cacheStats.activeRequests}\n` +
                        `Backend: ${JSON.stringify(result.data)}`
                    );
                } catch (error: any) {
                    new Notice(`Failed to get performance stats: ${error.message}`);
                }
            }
        },

        {
            id: 'vaultpilot-keyboard-shortcuts-help',
            name: 'Show Keyboard Shortcuts',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'h' }],
            callback: () => {
                const shortcuts = enhancementManager.getShortcutReference();
                
                let shortcutText = '## VaultPilot Keyboard Shortcuts\n\n';
                for (const [shortcut, command] of Object.entries(shortcuts)) {
                    shortcutText += `- **${shortcut}**: ${command}\n`;
                }
                
                // Create temporary note with shortcuts
                app.workspace.openLinkText('VaultPilot Shortcuts', '', true);
                
                // Focus on active editor and insert content
                setTimeout(() => {
                    const activeView = app.workspace.getActiveViewOfType('markdown' as any);
                    if (activeView && (activeView as any).editor) {
                        (activeView as any).editor.setValue(shortcutText);
                    }
                }, 100);
            }
        },

        // === VAULT HEALTH AND MAINTENANCE ===
        {
            id: 'vaultpilot-enhanced-health-check',
            name: 'Enhanced Vault Health Check',
            hotkeys: [{ modifiers: ['Ctrl', 'Shift'], key: 'h' }],
            callback: async () => {
                try {
                    const result = await enhancementManager.makeOptimizedRequest(
                        '/api/obsidian/enhanced/vault/analyze',
                        { vault_path: '/', health_check: true }
                    );

                    const reportContent = `# Vault Health Report\n\n` +
                        `Generated: ${new Date().toLocaleString()}\n\n` +
                        `## Statistics\n` +
                        `- Files: ${result.data.analysis.total_files}\n` +
                        `- Folders: ${result.data.analysis.total_folders}\n\n` +
                        `## Insights\n` +
                        result.data.analysis.insights.map((insight: string) => `- ${insight}`).join('\n') + '\n\n' +
                        `## Optimization Suggestions\n` +
                        result.data.analysis.optimization_suggestions.map((suggestion: string) => `- ${suggestion}`).join('\n') + '\n\n' +
                        `## Performance\n` +
                        `- Response Time: ${(result.data.performance.response_time * 1000).toFixed(0)}ms\n` +
                        `- Cache Hit: ${result.data.performance.cache_hit ? 'Yes' : 'No'}\n` +
                        `- Optimizations Applied: ${result.data.performance.optimizations_applied.join(', ')}\n`;

                    const fileName = `Vault Health Report ${new Date().toISOString().slice(0, 10)}.md`;
                    await app.vault.create(fileName, reportContent);
                    app.workspace.openLinkText(fileName, '');
                    
                    new Notice('Vault health report generated');
                } catch (error: any) {
                    new Notice(`Health check failed: ${error.message}`);
                }
            }
        }
    ];
}

// Export helper function for integration
export function integrateEnhancedCommands(app: App, plugin: any): VaultPilotEnhancementManager {
    // Create enhancement manager
    const enhancementManager = new VaultPilotEnhancementManager(app, plugin);
    
    // Register all enhanced commands
    const commands = createEnhancedVaultPilotCommands(app, plugin, enhancementManager);
    
    commands.forEach(command => {
        plugin.addCommand(command);
    });
    
    // Store reference for cleanup
    plugin.enhancementManager = enhancementManager;
    
    new Notice('VaultPilot enhanced commands loaded with keyboard shortcuts!');
    
    return enhancementManager;
}
