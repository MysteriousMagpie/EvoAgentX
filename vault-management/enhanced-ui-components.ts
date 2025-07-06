/**
 * Enhanced VaultPilot UI Components for Experience Improvements
 * 
 * Provides keyboard shortcuts, progress indicators, and performance optimizations
 * for the VaultPilot Obsidian plugin.
 */

// === KEYBOARD SHORTCUT SYSTEM ===

interface KeyboardShortcut {
    key: string;
    command: string;
    description: string;
    category: string;
    context: string;
}

interface ShortcutConfig {
    shortcuts: Record<string, string>;
    commands: Record<string, any>;
    reference: Record<string, KeyboardShortcut[]>;
}

export class KeyboardShortcutHandler {
    private shortcuts: Map<string, string> = new Map();
    private contexts: Set<string> = new Set();
    private currentContext: string = 'global';
    private plugin: any;
    private app: any;

    constructor(app: any, plugin: any) {
        this.app = app;
        this.plugin = plugin;
        this.setupDefaultShortcuts();
        this.registerEventListeners();
    }

    private setupDefaultShortcuts() {
        const defaultShortcuts = {
            // Core shortcuts
            'Ctrl+Shift+P': 'vaultpilot-command-palette',
            'Ctrl+Shift+S': 'vaultpilot-smart-search',
            'Ctrl+Shift+C': 'vaultpilot-chat-modal',
            'Ctrl+Shift+W': 'vaultpilot-workflow-modal',
            
            // Navigation
            'Ctrl+Shift+V': 'vaultpilot-vault-structure',
            'Ctrl+Shift+F': 'vaultpilot-file-operations',
            'Ctrl+Shift+O': 'vaultpilot-vault-organizer',
            
            // AI features
            'Ctrl+Space': 'vaultpilot-copilot-suggest',
            'Ctrl+Shift+A': 'vaultpilot-ai-complete',
            'Alt+Enter': 'vaultpilot-accept-suggestion',
            
            // Quick actions
            'Ctrl+Shift+N': 'vaultpilot-quick-note',
            'Ctrl+Shift+T': 'vaultpilot-task-from-selection',
            'Ctrl+Shift+H': 'vaultpilot-vault-health-check',
        };

        for (const [shortcut, command] of Object.entries(defaultShortcuts)) {
            this.shortcuts.set(shortcut, command);
        }
    }

    private registerEventListeners() {
        // Global keydown listener
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        
        // Context change listeners
        this.app.workspace.on('active-leaf-change', () => {
            this.updateContext();
        });
        
        this.app.workspace.on('editor-change', () => {
            this.updateContext();
        });
    }

    private handleKeyDown(event: KeyboardEvent) {
        const shortcut = this.buildShortcutString(event);
        const command = this.shortcuts.get(shortcut);
        
        if (command) {
            event.preventDefault();
            event.stopPropagation();
            this.executeCommand(command);
        }
    }

    private buildShortcutString(event: KeyboardEvent): string {
        const parts: string[] = [];
        
        if (event.ctrlKey) parts.push('Ctrl');
        if (event.altKey) parts.push('Alt');  
        if (event.shiftKey) parts.push('Shift');
        if (event.metaKey) parts.push('Meta');
        
        // Handle special keys
        if (event.key === ' ') {
            parts.push('Space');
        } else if (event.key === 'Enter') {
            parts.push('Enter');
        } else if (event.key === 'Tab') {
            parts.push('Tab');
        } else if (event.key === 'Escape') {
            parts.push('Esc');
        } else if (event.key.length === 1) {
            parts.push(event.key.toUpperCase());
        }
        
        return parts.join('+');
    }

    private updateContext() {
        const activeView = this.app.workspace.getActiveViewOfType('markdown');
        if (activeView && activeView.editor) {
            this.currentContext = 'editor';
        } else {
            this.currentContext = 'global';
        }
    }

    private executeCommand(command: string) {
        // Execute the command through Obsidian's command system
        this.app.commands.executeCommandById(command);
    }

    public addCustomShortcut(shortcut: string, command: string) {
        this.shortcuts.set(shortcut, command);
    }

    public removeShortcut(shortcut: string) {
        this.shortcuts.delete(shortcut);
    }

    public getShortcutsForContext(context: string): Record<string, string> {
        const result: Record<string, string> = {};
        
        for (const [shortcut, command] of this.shortcuts.entries()) {
            // All global shortcuts plus context-specific ones
            if (context === 'global' || this.isCommandValidForContext(command, context)) {
                result[shortcut] = command;
            }
        }
        
        return result;
    }

    private isCommandValidForContext(command: string, context: string): boolean {
        // Context validation logic
        const editorCommands = ['copilot-suggest', 'ai-complete', 'accept-suggestion', 'task-from-selection'];
        const globalCommands = ['command-palette', 'smart-search', 'chat-modal', 'workflow-modal'];
        
        if (context === 'editor') {
            return editorCommands.some(cmd => command.includes(cmd));
        }
        
        return globalCommands.some(cmd => command.includes(cmd));
    }
}

// === PROGRESS INDICATOR SYSTEM ===

interface ProgressUpdate {
    operation_id: string;
    operation_type: string;
    progress: number;
    progress_percentage: number;
    current_step: number;
    total_steps: number;
    message: string;
    eta_seconds?: number;
    status: string;
    timestamp: string;
    result_data?: any;
    error_data?: any;
}

export class ProgressIndicatorUI {
    private activeIndicators: Map<string, HTMLElement> = new Map();
    private container!: HTMLElement;
    private app: any;

    constructor(app: any) {
        this.app = app;
        this.createContainer();
    }

    private createContainer() {
        this.container = document.createElement('div');
        this.container.id = 'vaultpilot-progress-container';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 350px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }

    public showProgress(update: ProgressUpdate) {
        let indicator = this.activeIndicators.get(update.operation_id);
        
        if (!indicator) {
            indicator = this.createProgressIndicator(update);
            this.activeIndicators.set(update.operation_id, indicator);
            this.container.appendChild(indicator);
        }
        
        this.updateProgressIndicator(indicator, update);
    }

    private createProgressIndicator(update: ProgressUpdate): HTMLElement {
        const indicator = document.createElement('div');
        indicator.className = 'vaultpilot-progress-indicator';
        indicator.style.cssText = `
            background: var(--background-secondary);
            border: 1px solid var(--background-modifier-border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            pointer-events: auto;
            font-size: 12px;
            animation: slideIn 0.3s ease-out;
        `;

        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        indicator.innerHTML = `
            <div class="progress-header">
                <span class="operation-type">${this.formatOperationType(update.operation_type)}</span>
                <button class="close-btn" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="progress-message"></div>
            <div class="progress-bar-container">
                <div class="progress-bar"></div>
                <span class="progress-text"></span>
            </div>
            <div class="progress-details"></div>
        `;

        // Style the progress bar
        const progressBar = indicator.querySelector('.progress-bar') as HTMLElement;
        const progressContainer = indicator.querySelector('.progress-bar-container') as HTMLElement;
        
        progressContainer.style.cssText = `
            position: relative;
            background: var(--background-modifier-border);
            border-radius: 4px;
            height: 6px;
            margin: 8px 0;
        `;

        progressBar.style.cssText = `
            background: var(--interactive-accent);
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
            width: 0%;
        `;

        return indicator;
    }

    private updateProgressIndicator(indicator: HTMLElement, update: ProgressUpdate) {
        const messageEl = indicator.querySelector('.progress-message') as HTMLElement;
        const progressBar = indicator.querySelector('.progress-bar') as HTMLElement;
        const progressText = indicator.querySelector('.progress-text') as HTMLElement;
        const detailsEl = indicator.querySelector('.progress-details') as HTMLElement;

        // Update message
        messageEl.textContent = update.message;

        // Update progress bar
        progressBar.style.width = `${update.progress_percentage}%`;
        progressText.textContent = `${update.progress_percentage}%`;

        // Update details
        let detailsText = `Step ${update.current_step} of ${update.total_steps}`;
        if (update.eta_seconds && update.eta_seconds > 0) {
            detailsText += ` • ETA: ${this.formatETA(update.eta_seconds)}`;
        }
        detailsEl.textContent = detailsText;

        // Handle completion or error
        if (update.status === 'completed') {
            progressBar.style.background = '#22c55e'; // Green
            setTimeout(() => this.removeProgress(update.operation_id), 2000);
        } else if (update.status === 'failed') {
            progressBar.style.background = '#ef4444'; // Red
            messageEl.textContent = `Failed: ${update.message}`;
            setTimeout(() => this.removeProgress(update.operation_id), 5000);
        }
    }

    private formatOperationType(type: string): string {
        return type.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
        ).join(' ');
    }

    private formatETA(seconds: number): string {
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        } else if (seconds < 3600) {
            return `${Math.round(seconds / 60)}m`;
        } else {
            return `${Math.round(seconds / 3600)}h`;
        }
    }

    public removeProgress(operationId: string) {
        const indicator = this.activeIndicators.get(operationId);
        if (indicator) {
            indicator.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
                this.activeIndicators.delete(operationId);
            }, 300);
        }
    }

    public clearAllProgress() {
        for (const [operationId, indicator] of this.activeIndicators.entries()) {
            this.removeProgress(operationId);
        }
    }
}

// === RESPONSE TIME OPTIMIZER ===

export class ResponseTimeOptimizer {
    private cache: Map<string, any> = new Map();
    private cacheTTL: Map<string, number> = new Map();
    private requestQueue: Map<string, Promise<any>> = new Map();

    constructor() {
        // Clear expired cache entries every minute
        setInterval(() => this.cleanExpiredCache(), 60000);
    }

    public async optimizeRequest<T>(
        key: string, 
        requestFn: () => Promise<T>,
        ttlMinutes: number = 5
    ): Promise<T> {
        // Check cache first
        const cached = this.getCached(key);
        if (cached !== null) {
            return cached;
        }

        // Check if request is already in progress
        if (this.requestQueue.has(key)) {
            return this.requestQueue.get(key)!;
        }

        // Execute request
        const promise = requestFn();
        this.requestQueue.set(key, promise);

        try {
            const result = await promise;
            
            // Cache result
            this.setCached(key, result, ttlMinutes);
            
            return result;
        } finally {
            this.requestQueue.delete(key);
        }
    }

    private getCached(key: string): any {
        if (this.cache.has(key)) {
            const ttl = this.cacheTTL.get(key);
            if (ttl && Date.now() < ttl) {
                return this.cache.get(key);
            } else {
                // Expired
                this.cache.delete(key);
                this.cacheTTL.delete(key);
            }
        }
        return null;
    }

    private setCached(key: string, value: any, ttlMinutes: number) {
        this.cache.set(key, value);
        this.cacheTTL.set(key, Date.now() + (ttlMinutes * 60 * 1000));
    }

    private cleanExpiredCache() {
        const now = Date.now();
        for (const [key, ttl] of this.cacheTTL.entries()) {
            if (now >= ttl) {
                this.cache.delete(key);
                this.cacheTTL.delete(key);
            }
        }
    }

    public getCacheStats() {
        return {
            size: this.cache.size,
            activeRequests: this.requestQueue.size
        };
    }
}

// === MAIN ENHANCEMENT MANAGER ===

export class VaultPilotEnhancementManager {
    private shortcutHandler: KeyboardShortcutHandler;
    private progressUI: ProgressIndicatorUI;
    private responseOptimizer: ResponseTimeOptimizer;
    private websocket: WebSocket | null = null;
    private app: any;
    private plugin: any;

    constructor(app: any, plugin: any) {
        this.app = app;
        this.plugin = plugin;
        
        this.shortcutHandler = new KeyboardShortcutHandler(app, plugin);
        this.progressUI = new ProgressIndicatorUI(app);
        this.responseOptimizer = new ResponseTimeOptimizer();
        
        this.initializeWebSocket();
    }

    private initializeWebSocket() {
        const settings = this.plugin.settings;
        const wsUrl = settings.serverUrl.replace('http', 'ws') + '/api/obsidian/ws/enhanced';
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('VaultPilot Enhanced WebSocket connected');
        };

        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.websocket.onclose = () => {
            console.log('VaultPilot Enhanced WebSocket disconnected');
            // Attempt reconnection after 5 seconds
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }

    private handleWebSocketMessage(message: any) {
        switch (message.type) {
            case 'progress_update':
                this.progressUI.showProgress(message.data);
                break;
                
            case 'shortcuts':
                this.updateShortcuts(message.data);
                break;
                
            case 'performance_stats':
                this.updatePerformanceDisplay(message.data);
                break;
        }
    }

    private updateShortcuts(shortcutsData: ShortcutConfig) {
        // Update shortcuts in the handler
        for (const [shortcut, command] of Object.entries(shortcutsData.shortcuts)) {
            this.shortcutHandler.addCustomShortcut(shortcut, command);
        }
    }

    private updatePerformanceDisplay(stats: any) {
        // Could update a performance display in the UI
        console.log('Performance stats:', stats);
    }

    public async makeOptimizedRequest(
        endpoint: string, 
        data: any, 
        options: RequestInit = {}
    ): Promise<any> {
        const cacheKey = `${endpoint}:${JSON.stringify(data)}`;
        
        return this.responseOptimizer.optimizeRequest(
            cacheKey,
            async () => {
                const response = await fetch(
                    `${this.plugin.settings.serverUrl}${endpoint}`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...options.headers
                        },
                        body: JSON.stringify(data),
                        ...options
                    }
                );
                
                if (!response.ok) {
                    throw new Error(`Request failed: ${response.statusText}`);
                }
                
                return response.json();
            }
        );
    }

    public getShortcutReference(): Record<string, string> {
        return this.shortcutHandler.getShortcutsForContext('global');
    }

    public getCacheStats() {
        return this.responseOptimizer.getCacheStats();
    }

    public destroy() {
        if (this.websocket) {
            this.websocket.close();
        }
        this.progressUI.clearAllProgress();
    }
}
