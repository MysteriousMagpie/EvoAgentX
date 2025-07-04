/**
 * EvoAgentX Obsidian Plugin Example
 * 
 * This is a basic example of how to integrate EvoAgentX with Obsidian.
 * It demonstrates chat functionality, copilot completion, and workflow execution.
 */

import { App, Plugin, PluginSettingTab, Setting, Notice, TFile, Editor, MarkdownView, Modal } from 'obsidian';

interface EvoAgentXSettings {
	serverUrl: string;
	enableCopilot: boolean;
	enableRealtime: boolean;
	defaultMode: 'ask' | 'agent';
}

const DEFAULT_SETTINGS: EvoAgentXSettings = {
	serverUrl: 'http://localhost:8000',
	enableCopilot: true,
	enableRealtime: false,
	defaultMode: 'ask'
}

export default class EvoAgentXPlugin extends Plugin {
	settings: EvoAgentXSettings;
	public ws: WebSocket | null = null;
	private currentConversationId: string | null = null;

	async onload() {
		await this.loadSettings();

		// Add ribbon icon
		this.addRibbonIcon('message-square', 'EvoAgentX Chat', () => {
			new ChatModal(this.app, this).open();
		});

		// Add commands
		this.addCommand({
			id: 'evoagentx-chat',
			name: 'Open EvoAgentX Chat',
			callback: () => {
				new ChatModal(this.app, this).open();
			}
		});

		this.addCommand({
			id: 'evoagentx-complete',
			name: 'Get AI Completion',
			editorCallback: (editor: Editor) => {
				this.getCompletion(editor);
			}
		});

		this.addCommand({
			id: 'evoagentx-workflow',
			name: 'Execute Workflow',
			callback: () => {
				new WorkflowModal(this.app, this).open();
			}
		});

		this.addCommand({
			id: 'evoagentx-analyze-vault',
			name: 'Analyze Vault Context',
			callback: () => {
				this.analyzeVaultContext();
			}
		});

		// Add settings tab
		this.addSettingTab(new EvoAgentXSettingTab(this.app, this));

		// Connect WebSocket if enabled
		if (this.settings.enableRealtime) {
			this.connectWebSocket();
		}

		console.log('EvoAgentX plugin loaded');
	}

	onunload() {
		if (this.ws) {
			this.ws.close();
		}
		console.log('EvoAgentX plugin unloaded');
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	// WebSocket connection
	connectWebSocket() {
		try {
			const wsUrl = this.settings.serverUrl.replace('http', 'ws') + '/ws/obsidian';
			this.ws = new WebSocket(wsUrl);

			this.ws.onopen = () => {
				console.log('Connected to EvoAgentX WebSocket');
				new Notice('Connected to EvoAgentX');
			};

			this.ws.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					this.handleWebSocketMessage(data);
				} catch (e) {
					console.error('Error parsing WebSocket message:', e);
				}
			};

			this.ws.onclose = () => {
				console.log('Disconnected from EvoAgentX WebSocket');
				// Attempt to reconnect after 5 seconds
				setTimeout(() => {
					if (this.settings.enableRealtime) {
						this.connectWebSocket();
					}
				}, 5000);
			};

			this.ws.onerror = (error) => {
				console.error('WebSocket error:', error);
				new Notice('WebSocket connection error');
			};
		} catch (error) {
			console.error('Failed to connect WebSocket:', error);
		}
	}

	handleWebSocketMessage(data: any) {
		switch (data.type) {
			case 'connection_established':
				console.log('WebSocket connection established:', data.connection_id);
				break;
			case 'agent_response':
				new Notice(`Agent: ${data.response.response.substring(0, 100)}...`);
				break;
			case 'workflow_progress':
				new Notice(`Workflow progress: ${data.progress.message || 'Processing...'}`);
				break;
			case 'copilot_suggestion':
				// Handle copilot suggestions
				break;
		}
	}

	// API Methods
	async chatWithAgent(message: string, mode: 'ask' | 'agent' = 'ask'): Promise<string> {
		try {
			const response = await fetch(`${this.settings.serverUrl}/api/obsidian/chat`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ 
					message,
					conversation_id: this.currentConversationId,
					mode: mode
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const result = await response.json();
			this.currentConversationId = result.conversation_id;
			return result.response;
		} catch (error) {
			console.error('Chat error:', error);
			new Notice('Error communicating with EvoAgentX');
			return 'Error: Could not get response from agent';
		}
	}

	async getCompletion(editor: Editor) {
		if (!this.settings.enableCopilot) {
			new Notice('Copilot feature is disabled');
			return;
		}

		try {
			const cursor = editor.getCursor();
			const text = editor.getValue();
			const cursorPosition = editor.posToOffset(cursor);

			const response = await fetch(`${this.settings.serverUrl}/api/obsidian/copilot/complete`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					text,
					cursor_position: cursorPosition,
					file_type: 'markdown',
					context: 'obsidian note'
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const result = await response.json();
			
			// Insert completion at cursor
			editor.replaceRange(result.completion, cursor);
			new Notice('AI completion inserted');

		} catch (error) {
			console.error('Completion error:', error);
			new Notice('Error getting AI completion');
		}
	}

	async executeWorkflow(goal: string): Promise<string> {
		try {
			const response = await fetch(`${this.settings.serverUrl}/api/obsidian/workflow`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ 
					goal,
					context: { source: 'obsidian' }
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const result = await response.json();
			return result.output;
		} catch (error) {
			console.error('Workflow error:', error);
			new Notice('Error executing workflow');
			return 'Error: Could not execute workflow';
		}
	}

	async analyzeVaultContext() {
		try {
			// Get current file and some related files
			const activeFile = this.app.workspace.getActiveFile();
			const files = this.app.vault.getMarkdownFiles().slice(0, 5); // Limit to 5 files for demo
			
			const filePaths = files.map(f => f.path);
			const contentSnippets: Record<string, string> = {};
			
			// Get content snippets
			for (const file of files.slice(0, 3)) {
				const content = await this.app.vault.read(file);
				contentSnippets[file.path] = content.substring(0, 200);
			}

			const response = await fetch(`${this.settings.serverUrl}/api/obsidian/vault/context`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					file_paths: filePaths,
					content_snippets: contentSnippets
				})
			});

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const result = await response.json();
			
			// Create a new note with the analysis
			const analysisNote = `# Vault Analysis\n\nGenerated on: ${new Date().toLocaleString()}\n\n## Summary\n\n${result.context_summary}\n\n## Analyzed Files\n\n${filePaths.map(path => `- [[${path}]]`).join('\n')}`;
			
			const fileName = `Vault Analysis ${new Date().toISOString().split('T')[0]}.md`;
			await this.app.vault.create(fileName, analysisNote);
			
			// Open the new file
			const newFile = this.app.vault.getAbstractFileByPath(fileName);
			if (newFile instanceof TFile) {
				await this.app.workspace.getLeaf().openFile(newFile);
			}
			
			new Notice('Vault analysis complete!');

		} catch (error) {
			console.error('Vault analysis error:', error);
			new Notice('Error analyzing vault');
		}
	}
}

// Chat Modal
class ChatModal extends Modal {
	plugin: EvoAgentXPlugin;
	private messageContainer: HTMLElement;
	private inputEl: HTMLInputElement;
	private currentMode: 'ask' | 'agent' = 'ask';
	private modeToggle: HTMLElement;

	constructor(app: App, plugin: EvoAgentXPlugin) {
		super(app);
		this.plugin = plugin;
	}

	onOpen() {
		const { contentEl } = this;
		contentEl.createEl('h2', { text: 'EvoAgentX Chat' });

		// Create mode selector
		const modeContainer = contentEl.createDiv({ cls: 'evoagentx-mode-selector' });
		modeContainer.style.marginBottom = '10px';
		modeContainer.style.display = 'flex';
		modeContainer.style.gap = '5px';

		const askButton = modeContainer.createEl('button', { 
			text: 'Ask Mode',
			cls: this.currentMode === 'ask' ? 'mode-active' : 'mode-inactive'
		});
		askButton.onclick = () => this.setMode('ask');

		const agentButton = modeContainer.createEl('button', { 
			text: 'Agent Mode',
			cls: this.currentMode === 'agent' ? 'mode-active' : 'mode-inactive'
		});
		agentButton.onclick = () => this.setMode('agent');

		// Store reference for updates
		this.modeToggle = modeContainer;

		// Add mode description
		const modeDescription = contentEl.createDiv({ cls: 'evoagentx-mode-description' });
		modeDescription.style.fontSize = '0.9em';
		modeDescription.style.marginBottom = '10px';
		modeDescription.style.fontStyle = 'italic';
		this.updateModeDescription(modeDescription);

		// Create message container
		this.messageContainer = contentEl.createDiv({ cls: 'evoagentx-messages' });
		this.messageContainer.style.height = '300px';
		this.messageContainer.style.overflowY = 'auto';
		this.messageContainer.style.border = '1px solid var(--background-modifier-border)';
		this.messageContainer.style.padding = '10px';
		this.messageContainer.style.marginBottom = '10px';

		// Create input area
		const inputContainer = contentEl.createDiv({ cls: 'evoagentx-input' });
		
		this.inputEl = inputContainer.createEl('input', {
			type: 'text',
			placeholder: this.getPlaceholderText()
		});
		this.inputEl.style.width = '80%';
		this.inputEl.style.marginRight = '10px';

		const sendButton = inputContainer.createEl('button', { text: 'Send' });
		sendButton.onclick = () => this.sendMessage();

		// Handle Enter key
		this.inputEl.addEventListener('keypress', (e) => {
			if (e.key === 'Enter') {
				this.sendMessage();
			}
		});

		// Focus input
		this.inputEl.focus();

		// Set initial mode from settings
		this.setMode(this.plugin.settings.defaultMode);

		// Add CSS for mode buttons
		const style = contentEl.createEl('style');
		style.textContent = `
			.mode-active {
				background-color: var(--interactive-accent);
				color: var(--text-on-accent);
				border: 1px solid var(--interactive-accent);
				padding: 5px 10px;
				border-radius: 3px;
				cursor: pointer;
			}
			.mode-inactive {
				background-color: var(--background-modifier-border);
				color: var(--text-muted);
				border: 1px solid var(--background-modifier-border);
				padding: 5px 10px;
				border-radius: 3px;
				cursor: pointer;
			}
			.mode-inactive:hover {
				background-color: var(--background-modifier-hover);
			}
		`;
	}

	setMode(mode: 'ask' | 'agent') {
		this.currentMode = mode;
		
		// Update mode buttons
		if (this.modeToggle) {
			const buttons = this.modeToggle.querySelectorAll('button');
			buttons.forEach(btn => {
				btn.className = btn.textContent?.includes('Ask') ? 
					(mode === 'ask' ? 'mode-active' : 'mode-inactive') :
					(mode === 'agent' ? 'mode-active' : 'mode-inactive');
			});
		}
		
		// Update placeholder text
		if (this.inputEl) {
			this.inputEl.placeholder = this.getPlaceholderText();
		}
	}

	getPlaceholderText(): string {
		return this.currentMode === 'ask' ? 
			'Ask a question...' : 
			'Describe what you want to accomplish...';
	}

	updateModeDescription(element: HTMLElement) {
		element.textContent = this.currentMode === 'ask' ? 
			'Ask Mode: Quick questions and chat responses' :
			'Agent Mode: Complex workflows and task automation';
	}

	async sendMessage() {
		const message = this.inputEl.value.trim();
		if (!message) return;

		// Add user message to chat
		this.addMessage('You', message, 'user');
		this.inputEl.value = '';

		// Show typing indicator
		const typingEl = this.addMessage(
			this.currentMode === 'ask' ? 'Agent' : 'Workflow', 
			'Processing...', 
			'agent'
		);
		
		try {
			let response: string;
			
			if (this.currentMode === 'ask') {
				// Use simple chat endpoint
				response = await this.plugin.chatWithAgent(message, 'ask');
			} else {
				// Use unified chat endpoint with agent mode
				response = await this.plugin.chatWithAgent(message, 'agent');
			}
			
			// Remove typing indicator and add response
			typingEl.remove();
			this.addMessage(
				this.currentMode === 'ask' ? 'Agent' : 'Workflow',
				response, 
				'agent'
			);
		} catch (error) {
			typingEl.remove();
			this.addMessage('System', 'Error getting response', 'error');
		}
	}

	addMessage(sender: string, content: string, type: 'user' | 'agent' | 'error') {
		const messageEl = this.messageContainer.createDiv({ cls: `message message-${type}` });
		messageEl.createEl('strong', { text: `${sender}: ` });
		messageEl.createSpan({ text: content });
		
		// Scroll to bottom
		this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
		
		return messageEl;
	}

	onClose() {
		const { contentEl } = this;
		contentEl.empty();
	}
}

// Workflow Modal
class WorkflowModal extends Modal {
	plugin: EvoAgentXPlugin;

	constructor(app: App, plugin: EvoAgentXPlugin) {
		super(app);
		this.plugin = plugin;
	}

	onOpen() {
		const { contentEl } = this;
		contentEl.createEl('h2', { text: 'Execute EvoAgentX Workflow' });

		const form = contentEl.createEl('form');
		
		form.createEl('label', { text: 'Goal:' });
		const goalInput = form.createEl('textarea', {
			placeholder: 'Describe what you want to accomplish...'
		});
		goalInput.style.width = '100%';
		goalInput.style.height = '100px';
		goalInput.style.marginBottom = '10px';

		const buttonContainer = form.createDiv();
		
		const executeButton = buttonContainer.createEl('button', { text: 'Execute Workflow' });
		executeButton.type = 'submit';
		
		const cancelButton = buttonContainer.createEl('button', { text: 'Cancel' });
		cancelButton.type = 'button';
		cancelButton.style.marginLeft = '10px';
		cancelButton.onclick = () => this.close();

		form.onsubmit = async (e) => {
			e.preventDefault();
			
			const goal = goalInput.value.trim();
			if (!goal) {
				new Notice('Please enter a goal');
				return;
			}

			executeButton.disabled = true;
			executeButton.textContent = 'Executing...';

			try {
				const result = await this.plugin.executeWorkflow(goal);
				
				// Create a new note with the workflow result
				const fileName = `Workflow Result ${new Date().toISOString().split('T')[0]}.md`;
				const content = `# Workflow Result\n\n**Goal:** ${goal}\n\n**Generated on:** ${new Date().toLocaleString()}\n\n## Result\n\n${result}`;
				
				await this.app.vault.create(fileName, content);
				
				// Open the new file
				const newFile = this.app.vault.getAbstractFileByPath(fileName);
				if (newFile instanceof TFile) {
					await this.app.workspace.getLeaf().openFile(newFile);
				}
				
				new Notice('Workflow completed!');
				this.close();
			} catch (error) {
				new Notice('Error executing workflow');
				executeButton.disabled = false;
				executeButton.textContent = 'Execute Workflow';
			}
		};

		goalInput.focus();
	}

	onClose() {
		const { contentEl } = this;
		contentEl.empty();
	}
}

// Settings Tab
class EvoAgentXSettingTab extends PluginSettingTab {
	plugin: EvoAgentXPlugin;

	constructor(app: App, plugin: EvoAgentXPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();

		containerEl.createEl('h2', { text: 'EvoAgentX Settings' });

		new Setting(containerEl)
			.setName('Server URL')
			.setDesc('The URL of the EvoAgentX server')
			.addText(text => text
				.setPlaceholder('http://localhost:8000')
				.setValue(this.plugin.settings.serverUrl)
				.onChange(async (value) => {
					this.plugin.settings.serverUrl = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Enable Copilot')
			.setDesc('Enable AI-powered text completion')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.enableCopilot)
				.onChange(async (value) => {
					this.plugin.settings.enableCopilot = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Enable Realtime')
			.setDesc('Enable WebSocket connection for real-time features')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.enableRealtime)
				.onChange(async (value) => {
					this.plugin.settings.enableRealtime = value;
					await this.plugin.saveSettings();
					
					// Reconnect WebSocket if enabled
					if (value) {
						this.plugin.connectWebSocket();
					} else if (this.plugin.ws) {
						this.plugin.ws.close();
					}
				}));

		new Setting(containerEl)
			.setName('Default Chat Mode')
			.setDesc('Choose the default mode for chat interactions')
			.addDropdown(dropdown => dropdown
				.addOption('ask', 'Ask Mode (Simple Q&A)')
				.addOption('agent', 'Agent Mode (Complex Workflows)')
				.setValue(this.plugin.settings.defaultMode)
				.onChange(async (value: string) => {
					this.plugin.settings.defaultMode = value as 'ask' | 'agent';
					await this.plugin.saveSettings();
				}));

		// Add test connection button
		new Setting(containerEl)
			.setName('Test Connection')
			.setDesc('Test connection to the EvoAgentX server')
			.addButton(button => button
				.setButtonText('Test')
				.onClick(async () => {
					try {
						const response = await fetch(`${this.plugin.settings.serverUrl}/api/obsidian/health`);
						if (response.ok) {
							const data = await response.json();
							new Notice(`✅ Connected! Status: ${data.status}`);
						} else {
							new Notice('❌ Connection failed');
						}
					} catch (error) {
						new Notice('❌ Connection error');
					}
				}));
	}
}
