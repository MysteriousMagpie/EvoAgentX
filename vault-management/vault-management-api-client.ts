/**
 * API Client Extensions for VaultPilot Vault Management
 * Add these methods to your existing EvoAgentXClient class
 */

import {
  VaultStructureRequest,
  VaultStructureResponse,
  VaultFileInfo,
  FileOperationRequest,
  FileOperationResponse,
  BatchFileOperationRequest,
  BatchFileOperationResponse,
  VaultSearchRequest,
  VaultSearchResponse,
  VaultSearchResult,
  VaultOrganizationRequest,
  VaultOrganizationResponse,
  VaultBackupRequest,
  VaultBackupResponse,
  VaultManagementError,
  VaultManagementAPI
} from './vault-management-types';

/**
 * Extend your existing EvoAgentXClient class with these methods
 */
export class VaultManagementExtensions implements VaultManagementAPI {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  // === CORE API METHODS ===

  /**
   * Get comprehensive vault structure with AI analysis
   */
  async getVaultStructure(request: VaultStructureRequest): Promise<VaultStructureResponse> {
    try {
      const response = await this.makeRequest('/api/obsidian/vault/structure', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `Failed to get vault structure: ${response.statusText}`,
          'STRUCTURE_FETCH_FAILED',
          'structure'
        );
      }

      return await response.json();
    } catch (error) {
      this.handleVaultManagementError(error, 'structure');
      throw error;
    }
  }

  /**
   * Perform individual file operation (create, update, delete, move, copy)
   */
  async performFileOperation(request: FileOperationRequest): Promise<FileOperationResponse> {
    try {
      this.validateFileOperationRequest(request);

      const response = await this.makeRequest('/api/obsidian/vault/file/operation', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `File operation failed: ${response.statusText}`,
          'FILE_OPERATION_FAILED',
          'file-operations'
        );
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new VaultManagementError(
          result.message || 'File operation failed',
          'FILE_OPERATION_FAILED',
          'file-operations'
        );
      }

      return result;
    } catch (error) {
      this.handleVaultManagementError(error, 'file-operations');
      throw error;
    }
  }

  /**
   * Perform multiple file operations efficiently
   */
  async performBatchFileOperations(request: BatchFileOperationRequest): Promise<BatchFileOperationResponse> {
    try {
      if (!request.operations || request.operations.length === 0) {
        throw new VaultManagementError(
          'No operations provided for batch execution',
          'INVALID_BATCH_REQUEST',
          'batch-operations'
        );
      }

      // Validate all operations before executing
      request.operations.forEach((op, index) => {
        try {
          this.validateFileOperationRequest(op);
        } catch (error) {
          throw new VaultManagementError(
            `Invalid operation at index ${index}: ${error instanceof Error ? error.message : String(error)}`,
            'INVALID_BATCH_OPERATION',
            'batch-operations'
          );
        }
      });

      const response = await this.makeRequest('/api/obsidian/vault/file/batch', {
        method: 'POST',
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `Batch operation failed: ${response.statusText}`,
          'BATCH_OPERATION_FAILED',
          'batch-operations'
        );
      }

      return await response.json();
    } catch (error) {
      this.handleVaultManagementError(error, 'batch-operations');
      throw error;
    }
  }

  /**
   * Perform intelligent search across vault with AI analysis
   */
  async searchVault(request: VaultSearchRequest): Promise<VaultSearchResponse> {
    try {
      if (!request.query || request.query.trim().length === 0) {
        throw new VaultManagementError(
          'Search query cannot be empty',
          'INVALID_SEARCH_QUERY',
          'search'
        );
      }

      const response = await this.makeRequest('/api/obsidian/vault/search', {
        method: 'POST',
        body: JSON.stringify({
          ...request,
          max_results: request.max_results || 50,
          search_type: request.search_type || 'content',
          include_context: request.include_context !== false
        })
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `Search failed: ${response.statusText}`,
          'SEARCH_FAILED',
          'search'
        );
      }

      return await response.json();
    } catch (error) {
      this.handleVaultManagementError(error, 'search');
      throw error;
    }
  }

  /**
   * Get AI-assisted vault organization plan
   */
  async organizeVault(request: VaultOrganizationRequest): Promise<VaultOrganizationResponse> {
    try {
      if (!request.organization_goal || request.organization_goal.trim().length === 0) {
        throw new VaultManagementError(
          'Organization goal cannot be empty',
          'INVALID_ORGANIZATION_GOAL',
          'organization'
        );
      }

      const response = await this.makeRequest('/api/obsidian/vault/organize', {
        method: 'POST',
        body: JSON.stringify({
          ...request,
          dry_run: request.dry_run !== false // Default to dry run
        })
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `Organization planning failed: ${response.statusText}`,
          'ORGANIZATION_FAILED',
          'organization'
        );
      }

      return await response.json();
    } catch (error) {
      this.handleVaultManagementError(error, 'organization');
      throw error;
    }
  }

  /**
   * Create vault backup
   */
  async createVaultBackup(request: VaultBackupRequest): Promise<VaultBackupResponse> {
    try {
      const response = await this.makeRequest('/api/obsidian/vault/backup', {
        method: 'POST',
        body: JSON.stringify({
          ...request,
          include_settings: request.include_settings !== false,
          compress: request.compress !== false
        })
      });

      if (!response.ok) {
        throw new VaultManagementError(
          `Backup creation failed: ${response.statusText}`,
          'BACKUP_FAILED',
          'backup'
        );
      }

      return await response.json();
    } catch (error) {
      this.handleVaultManagementError(error, 'backup');
      throw error;
    }
  }

  // === CONVENIENCE METHODS ===

  /**
   * Create a new file with content
   */
  async createFile(filePath: string, content: string, createFolders = true): Promise<FileOperationResponse> {
    return this.performFileOperation({
      operation: 'create',
      file_path: filePath,
      content,
      create_missing_folders: createFolders
    });
  }

  /**
   * Update existing file content
   */
  async updateFile(filePath: string, content: string): Promise<FileOperationResponse> {
    return this.performFileOperation({
      operation: 'update',
      file_path: filePath,
      content
    });
  }

  /**
   * Delete a file
   */
  async deleteFile(filePath: string): Promise<FileOperationResponse> {
    return this.performFileOperation({
      operation: 'delete',
      file_path: filePath
    });
  }

  /**
   * Move a file to new location
   */
  async moveFile(filePath: string, destinationPath: string, createFolders = true): Promise<FileOperationResponse> {
    return this.performFileOperation({
      operation: 'move',
      file_path: filePath,
      destination_path: destinationPath,
      create_missing_folders: createFolders
    });
  }

  /**
   * Copy a file to new location
   */
  async copyFile(filePath: string, destinationPath: string, createFolders = true): Promise<FileOperationResponse> {
    return this.performFileOperation({
      operation: 'copy',
      file_path: filePath,
      destination_path: destinationPath,
      create_missing_folders: createFolders
    });
  }

  // === UTILITY METHODS ===

  /**
   * Test vault management feature availability
   */
  async testVaultManagementConnection(): Promise<boolean> {
    try {
      const response = await this.makeRequest('/api/obsidian/vault/structure', {
        method: 'POST',
        body: JSON.stringify({ include_content: false, max_depth: 1 })
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get vault statistics quickly
   */
  async getVaultStatistics(): Promise<{ files: number; folders: number; size: number }> {
    const structure = await this.getVaultStructure({ include_content: false, max_depth: 1 });
    return {
      files: structure.total_files,
      folders: structure.total_folders,
      size: structure.total_size
    };
  }

  /**
   * Quick search for files by name
   */
  async searchFilesByName(query: string, limit = 20): Promise<VaultSearchResult[]> {
    const results = await this.searchVault({
      query,
      search_type: 'filename',
      max_results: limit
    });
    return results.results;
  }

  /**
   * Create multiple files in batch
   */
  async createMultipleFiles(files: Array<{ path: string; content: string }>): Promise<BatchFileOperationResponse> {
    const operations = files.map(file => ({
      operation: 'create' as const,
      file_path: file.path,
      content: file.content,
      create_missing_folders: true
    }));

    return this.performBatchFileOperations({
      operations,
      continue_on_error: true
    });
  }

  // === PRIVATE HELPER METHODS ===

  private async makeRequest(endpoint: string, options: RequestInit): Promise<Response> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` }),
      ...options.headers
    };

    return fetch(url, {
      ...options,
      headers
    });
  }

  private validateFileOperationRequest(request: FileOperationRequest): void {
    if (!request.operation) {
      throw new Error('Operation type is required');
    }

    if (!request.file_path || request.file_path.trim().length === 0) {
      throw new Error('File path is required');
    }

    if ((request.operation === 'move' || request.operation === 'copy') && !request.destination_path) {
      throw new Error(`Destination path is required for ${request.operation} operation`);
    }

    if (request.operation === 'create' && request.content === undefined) {
      throw new Error('Content is required for create operation');
    }

    // Validate path format
    if (request.file_path.includes('..') || request.file_path.startsWith('/')) {
      throw new Error('Invalid file path format');
    }
  }

  private handleVaultManagementError(error: any, feature: string): void {
    console.error(`Vault management error in ${feature}:`, error);
    
    // Add any global error handling logic here
    // For example, notifying the user or logging to analytics
  }
}

// === INTEGRATION HELPER ===

/**
 * Add these methods to your existing EvoAgentXClient class
 * 
 * Example integration:
 * 
 * class EvoAgentXClient extends VaultManagementExtensions {
 *   // Your existing methods...
 *   
 *   constructor(settings: EvoAgentXSettings) {
 *     super(settings.serverUrl, settings.apiKey);
 *     // Your existing initialization...
 *   }
 * }
 */

export const VAULT_MANAGEMENT_ENDPOINTS = {
  STRUCTURE: '/api/obsidian/vault/structure',
  FILE_OPERATION: '/api/obsidian/vault/file/operation',
  BATCH_OPERATION: '/api/obsidian/vault/file/batch',
  SEARCH: '/api/obsidian/vault/search',
  ORGANIZE: '/api/obsidian/vault/organize',
  BACKUP: '/api/obsidian/vault/backup'
} as const;
