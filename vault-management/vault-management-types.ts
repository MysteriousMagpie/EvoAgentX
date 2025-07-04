/**
 * TypeScript type definitions for VaultPilot vault management integration
 * Add these types to your existing types.ts file or create a new vault-types.ts
 */

// === VAULT STRUCTURE TYPES ===

export interface VaultStructureRequest {
  include_content?: boolean;
  max_depth?: number;
  file_types?: string[];
}

export interface VaultFileInfo {
  path: string;
  name: string;
  size: number;
  modified: string;
  file_type: string;
  content_preview?: string;
  tags?: string[];
  links?: string[];
}

export interface VaultFolderInfo {
  name: string;
  path: string;
  children: (VaultFileInfo | VaultFolderInfo)[];
  type: 'folder';
}

export interface VaultStructureResponse {
  vault_name: string;
  total_files: number;
  total_folders: number;
  total_size: number;
  structure: VaultFolderInfo;
  recent_files: VaultFileInfo[];
  orphaned_files: VaultFileInfo[];
}

// === FILE OPERATION TYPES ===

export type FileOperationType = 'create' | 'update' | 'delete' | 'move' | 'copy';

export interface FileOperationRequest {
  operation: FileOperationType;
  file_path: string;
  content?: string;
  destination_path?: string;
  create_missing_folders?: boolean;
}

export interface FileOperationResponse {
  success: boolean;
  message: string;
  file_path: string;
  operation_performed: string;
}

export interface BatchFileOperationRequest {
  operations: FileOperationRequest[];
  continue_on_error?: boolean;
}

export interface BatchFileOperationResponse {
  success: boolean;
  completed_operations: number;
  failed_operations: number;
  results: FileOperationResponse[];
  errors: string[];
}

// === SEARCH TYPES ===

export type SearchType = 'content' | 'filename' | 'tags' | 'links';

export interface VaultSearchRequest {
  query: string;
  search_type?: SearchType;
  file_types?: string[];
  max_results?: number;
  include_context?: boolean;
}

export interface VaultSearchResult {
  file_path: string;
  file_name: string;
  match_type: string;
  snippet: string;
  line_number?: number;
  relevance_score: number;
}

export interface VaultSearchResponse {
  query: string;
  total_results: number;
  results: VaultSearchResult[];
  search_time: number;
}

// === ORGANIZATION TYPES ===

export interface VaultOrganizationRequest {
  organization_goal: string;
  preferences?: Record<string, any>;
  dry_run?: boolean;
}

export interface VaultOrganizationResponse {
  reorganization_plan: string;
  suggested_changes: Record<string, any>[];
  estimated_changes_count: number;
  dry_run: boolean;
  execution_steps?: string[];
}

// === BACKUP TYPES ===

export interface VaultBackupRequest {
  backup_name?: string;
  include_settings?: boolean;
  compress?: boolean;
}

export interface VaultBackupResponse {
  success: boolean;
  backup_path: string;
  backup_size: number;
  files_backed_up: number;
  backup_time: string;
}

// === SETTINGS EXTENSIONS ===

export interface VaultManagementSettings {
  enableVaultManagement: boolean;
  autoSyncVaultStructure: boolean;
  searchResultsLimit: number;
  enableSmartSearch: boolean;
  batchOperationTimeout: number;
  showVaultStats: boolean;
  maxSearchResults: number;
  defaultSearchType: SearchType;
  enableFileOperations: boolean;
  confirmDestructiveOperations: boolean;
  autoBackupBeforeOperations: boolean;
}

// === UI STATE TYPES ===

export interface VaultStructureState {
  isLoading: boolean;
  error?: string;
  data?: VaultStructureResponse;
  lastUpdated?: Date;
}

export interface SearchState {
  isSearching: boolean;
  query: string;
  results: VaultSearchResult[];
  totalResults: number;
  searchTime: number;
  error?: string;
}

export interface FileOperationState {
  isExecuting: boolean;
  currentOperation?: FileOperationRequest;
  progress: number;
  results: FileOperationResponse[];
  errors: string[];
}

// === MODAL PROPS TYPES ===

// Basic App interface (would normally come from Obsidian package)
interface App {
  vault: any;
  workspace: any;
}

export interface VaultModalProps {
  app: App;
  plugin: VaultPilotPlugin;
  onClose?: () => void;
}

export interface SearchModalProps extends VaultModalProps {
  initialQuery?: string;
  searchType?: SearchType;
}

export interface FileOperationModalProps extends VaultModalProps {
  initialPath?: string;
  operation?: FileOperationType;
}

export interface BatchOperationModalProps extends VaultModalProps {
  initialOperations?: FileOperationRequest[];
}

// === EVENT TYPES ===

export interface VaultManagementEvents {
  'vault-structure-updated': VaultStructureResponse;
  'search-completed': VaultSearchResponse;
  'file-operation-completed': FileOperationResponse;
  'batch-operation-completed': BatchFileOperationResponse;
  'vault-organization-planned': VaultOrganizationResponse;
  'vault-management-error': Error;
}

// === UTILITY TYPES ===

export type VaultManagementFeature = 
  | 'structure'
  | 'search'
  | 'file-operations'
  | 'batch-operations'
  | 'organization'
  | 'backup';

export interface FeatureAvailability {
  vaultStructure: boolean;
  smartSearch: boolean;
  fileOperations: boolean;
  batchOperations: boolean;
  vaultOrganization: boolean;
  realTimeSync: boolean;
  backupRestore: boolean;
  healthCheck: boolean;
}

export interface VaultStatistics {
  totalFiles: number;
  totalFolders: number;
  totalSize: number;
  averageFileSize: number;
  largestFile: VaultFileInfo;
  recentFiles: VaultFileInfo[];
  orphanedFiles: VaultFileInfo[];
  lastAnalyzed: Date;
}

// === ERROR TYPES ===

export class VaultManagementError extends Error {
  constructor(
    message: string,
    public code: string,
    public feature: VaultManagementFeature,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'VaultManagementError';
  }
}

export interface VaultManagementErrorInfo {
  code: string;
  message: string;
  feature: VaultManagementFeature;
  recoverable: boolean;
  suggestedAction?: string;
}

// === PLUGIN EXTENSION TYPES ===

export interface VaultPilotPlugin {
  // Extend your existing plugin interface with these properties
  vaultManagement?: {
    isEnabled: boolean;
    features: FeatureAvailability;
    lastSync?: Date;
    statistics?: VaultStatistics;
  };
}

// === API CLIENT EXTENSION ===

export interface VaultManagementAPI {
  getVaultStructure(request: VaultStructureRequest): Promise<VaultStructureResponse>;
  performFileOperation(request: FileOperationRequest): Promise<FileOperationResponse>;
  performBatchFileOperations(request: BatchFileOperationRequest): Promise<BatchFileOperationResponse>;
  searchVault(request: VaultSearchRequest): Promise<VaultSearchResponse>;
  organizeVault(request: VaultOrganizationRequest): Promise<VaultOrganizationResponse>;
  createVaultBackup(request: VaultBackupRequest): Promise<VaultBackupResponse>;
  
  // Convenience methods
  createFile(filePath: string, content: string, createFolders?: boolean): Promise<FileOperationResponse>;
  updateFile(filePath: string, content: string): Promise<FileOperationResponse>;
  deleteFile(filePath: string): Promise<FileOperationResponse>;
  moveFile(filePath: string, destinationPath: string, createFolders?: boolean): Promise<FileOperationResponse>;
  copyFile(filePath: string, destinationPath: string, createFolders?: boolean): Promise<FileOperationResponse>;
}

// === CONSTANTS ===

export const VAULT_MANAGEMENT_DEFAULTS = {
  SEARCH_RESULTS_LIMIT: 50,
  BATCH_OPERATION_TIMEOUT: 30000,
  MAX_FILE_SIZE_FOR_PREVIEW: 1024 * 100, // 100KB
  STRUCTURE_CACHE_DURATION: 5 * 60 * 1000, // 5 minutes
  AUTO_REFRESH_INTERVAL: 30 * 1000, // 30 seconds
} as const;

export const FILE_OPERATION_ICONS = {
  create: '📄',
  update: '✏️',
  delete: '🗑️',
  move: '🔄',
  copy: '📋',
} as const;

export const SEARCH_TYPE_ICONS = {
  content: '📝',
  filename: '📁',
  tags: '🏷️',
  links: '🔗',
} as const;
