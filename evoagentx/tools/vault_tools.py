"""
Vault management tools for Obsidian integration.
These tools enable agents to perform comprehensive vault operations.
"""

import os
import shutil
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import zipfile
import tempfile
from dataclasses import dataclass


@dataclass
class VaultFile:
    """Represents a file in the vault"""
    path: str
    name: str
    size: int
    modified: datetime
    file_type: str
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    links: Optional[List[str]] = None


@dataclass
class VaultFolder:
    """Represents a folder in the vault"""
    path: str
    name: str
    files: List[VaultFile]
    subfolders: List['VaultFolder']


class ObsidianVaultTools:
    """Tools for managing Obsidian vault structure and content"""
    
    def __init__(self, vault_root: Optional[str] = None):
        """
        Initialize vault tools with a root directory.
        If vault_root is None, tools will work in a sandboxed mode.
        """
        if vault_root:
            self.vault_root = Path(vault_root)
            self.sandbox_mode = False
        else:
            self.vault_root = Path(tempfile.gettempdir()) / "evoagentx_vault_sandbox"
            self.vault_root.mkdir(exist_ok=True)
            self.sandbox_mode = True
        
    def _get_safe_path(self, relative_path: str) -> Path:
        """Get a safe absolute path within the vault or sandbox"""
        base_path = self.vault_root
            
        full_path = (base_path / relative_path).resolve()
        
        # Ensure path is within the vault/sandbox
        if base_path not in full_path.parents and full_path != base_path:
            raise ValueError(f"Access outside vault forbidden: {relative_path}")
            
        return full_path
    
    def get_vault_structure(self, include_content: bool = False, max_depth: Optional[int] = None, 
                           file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive vault structure information"""
        try:
            if self.sandbox_mode:
                # Return mock structure for sandbox mode
                return self._get_mock_vault_structure()
            
            vault_path = self.vault_root
            if not vault_path.exists():
                raise FileNotFoundError(f"Vault directory not found: {vault_path}")
            
            total_files = 0
            total_folders = 0
            total_size = 0
            recent_files = []
            orphaned_files = []
            
            def scan_directory(dir_path: Path, current_depth: int = 0) -> VaultFolder:
                nonlocal total_files, total_folders, total_size
                
                if max_depth is not None and current_depth >= max_depth:
                    return VaultFolder(str(dir_path.relative_to(vault_path)), dir_path.name, [], [])
                
                files = []
                subfolders = []
                
                try:
                    for item in dir_path.iterdir():
                        if item.is_file():
                            if file_types and item.suffix.lstrip('.').lower() not in [ft.lower() for ft in file_types]:
                                continue
                                
                            file_info = self._get_file_info(item, include_content)
                            files.append(file_info)
                            total_files += 1
                            total_size += file_info.size
                            
                            # Track recent files (modified in last 7 days)
                            if (datetime.now() - file_info.modified).days <= 7:
                                recent_files.append(file_info)
                                
                        elif item.is_dir() and not item.name.startswith('.'):
                            subfolder = scan_directory(item, current_depth + 1)
                            subfolders.append(subfolder)
                            total_folders += 1
                            
                except PermissionError:
                    pass  # Skip directories we can't access
                    
                return VaultFolder(
                    str(dir_path.relative_to(vault_path)),
                    dir_path.name,
                    files,
                    subfolders
                )
            
            root_folder = scan_directory(vault_path)
            
            # Find orphaned files (files with no incoming links)
            if include_content:
                orphaned_files = self._find_orphaned_files(vault_path)
            
            # Sort recent files by modification date
            recent_files.sort(key=lambda f: f.modified, reverse=True)
            recent_files = recent_files[:20]  # Limit to 20 most recent
            
            return {
                "vault_name": vault_path.name,
                "total_files": total_files,
                "total_folders": total_folders,
                "total_size": total_size,
                "structure": self._folder_to_dict(root_folder),
                "recent_files": [self._file_to_dict(f) for f in recent_files],
                "orphaned_files": [self._file_to_dict(f) for f in orphaned_files]
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get vault structure: {str(e)}",
                "vault_name": "Unknown",
                "total_files": 0,
                "total_folders": 0,
                "total_size": 0,
                "structure": {},
                "recent_files": [],
                "orphaned_files": []
            }
    
    def _get_mock_vault_structure(self) -> Dict[str, Any]:
        """Return mock vault structure for sandbox mode"""
        return {
            "vault_name": "Demo Vault",
            "total_files": 25,
            "total_folders": 8,
            "total_size": 524288,
            "structure": {
                "path": "",
                "name": "Demo Vault",
                "files": [
                    {"path": "README.md", "name": "README.md", "size": 1024, "file_type": "md"},
                    {"path": "Daily Notes.md", "name": "Daily Notes.md", "size": 2048, "file_type": "md"}
                ],
                "subfolders": [
                    {
                        "path": "Projects",
                        "name": "Projects", 
                        "files": [
                            {"path": "Projects/Project A.md", "name": "Project A.md", "size": 4096, "file_type": "md"},
                            {"path": "Projects/Project B.md", "name": "Project B.md", "size": 3072, "file_type": "md"}
                        ],
                        "subfolders": []
                    },
                    {
                        "path": "Resources",
                        "name": "Resources",
                        "files": [
                            {"path": "Resources/Articles.md", "name": "Articles.md", "size": 8192, "file_type": "md"}
                        ],
                        "subfolders": []
                    }
                ]
            },
            "recent_files": [
                {"path": "Daily Notes.md", "name": "Daily Notes.md", "size": 2048, "file_type": "md"}
            ],
            "orphaned_files": []
        }
    
    def _get_file_info(self, file_path: Path, include_content: bool = False) -> VaultFile:
        """Get detailed information about a file"""
        stat = file_path.stat()
        content = None
        tags = []
        links = []
        
        if include_content and file_path.suffix.lower() in ['.md', '.txt']:
            try:
                content = file_path.read_text(encoding='utf-8')
                if file_path.suffix.lower() == '.md':
                    tags = self._extract_tags(content)
                    links = self._extract_links(content)
            except (UnicodeDecodeError, PermissionError):
                content = None
        
        return VaultFile(
            path=str(file_path.relative_to(self.vault_root)),
            name=file_path.name,
            size=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            file_type=file_path.suffix.lstrip('.').lower() or 'unknown',
            content=content[:500] if content else None,  # Preview only
            tags=tags,
            links=links
        )
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from markdown content"""
        tags = []
        # Extract #tags
        tag_pattern = r'#([a-zA-Z0-9_/-]+)'
        tags.extend(re.findall(tag_pattern, content))
        
        # Extract tags from frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            # Simple tags extraction from YAML frontmatter
            tag_line_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
            if tag_line_match:
                yaml_tags = [tag.strip().strip('"\'') for tag in tag_line_match.group(1).split(',')]
                tags.extend(yaml_tags)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_links(self, content: str) -> List[str]:
        """Extract internal links from markdown content"""
        # Extract [[internal links]]
        internal_links = re.findall(r'\[\[([^\]]+)\]\]', content)
        # Extract [text](link) style links to .md files
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
        
        links = internal_links + [link[1] for link in md_links]
        return list(set(links))
    
    def _find_orphaned_files(self, vault_path: Path) -> List[VaultFile]:
        """Find files that have no incoming links"""
        # This is a simplified implementation
        # In a real scenario, you'd want to build a comprehensive link graph
        all_files = {}
        all_links = set()
        
        for md_file in vault_path.rglob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                file_info = self._get_file_info(md_file, False)
                all_files[md_file.stem] = file_info
                
                links = self._extract_links(content)
                for link in links:
                    # Clean link name
                    clean_link = Path(link).stem
                    all_links.add(clean_link)
                    
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # Find files with no incoming links
        orphaned = []
        for filename, file_info in all_files.items():
            if filename not in all_links:
                orphaned.append(file_info)
        
        return orphaned[:10]  # Limit to 10 orphaned files
    
    def _folder_to_dict(self, folder: VaultFolder) -> Dict[str, Any]:
        """Convert VaultFolder to dictionary"""
        return {
            "path": folder.path,
            "name": folder.name,
            "files": [self._file_to_dict(f) for f in folder.files],
            "subfolders": [self._folder_to_dict(sf) for sf in folder.subfolders]
        }
    
    def _file_to_dict(self, file: VaultFile) -> Dict[str, Any]:
        """Convert VaultFile to dictionary"""
        return {
            "path": file.path,
            "name": file.name,
            "size": file.size,
            "modified": file.modified.isoformat(),
            "file_type": file.file_type,
            "content_preview": file.content,
            "tags": file.tags,
            "links": file.links
        }
    
    def create_file(self, file_path: str, content: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Create a new file in the vault"""
        try:
            full_path = self._get_safe_path(file_path)
            
            if create_missing_folders:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if full_path.exists():
                return {
                    "success": False,
                    "message": f"File already exists: {file_path}",
                    "file_path": file_path,
                    "operation_performed": "create"
                }
            
            full_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"File created successfully: {file_path}",
                "file_path": file_path,
                "operation_performed": "create"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create file: {str(e)}",
                "file_path": file_path,
                "operation_performed": "create"
            }
    
    def update_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Update an existing file in the vault"""
        try:
            full_path = self._get_safe_path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File does not exist: {file_path}",
                    "file_path": file_path,
                    "operation_performed": "update"
                }
            
            # Create backup
            backup_content = full_path.read_text(encoding='utf-8')
            
            full_path.write_text(content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"File updated successfully: {file_path}",
                "file_path": file_path,
                "operation_performed": "update"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update file: {str(e)}",
                "file_path": file_path,
                "operation_performed": "update"
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from the vault"""
        try:
            full_path = self._get_safe_path(file_path)
            
            if not full_path.exists():
                return {
                    "success": False,
                    "message": f"File does not exist: {file_path}",
                    "file_path": file_path,
                    "operation_performed": "delete"
                }
            
            full_path.unlink()
            
            return {
                "success": True,
                "message": f"File deleted successfully: {file_path}",
                "file_path": file_path,
                "operation_performed": "delete"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete file: {str(e)}",
                "file_path": file_path,
                "operation_performed": "delete"
            }
    
    def move_file(self, file_path: str, destination_path: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Move a file to a new location in the vault"""
        try:
            source_path = self._get_safe_path(file_path)
            dest_path = self._get_safe_path(destination_path)
            
            if not source_path.exists():
                return {
                    "success": False,
                    "message": f"Source file does not exist: {file_path}",
                    "file_path": file_path,
                    "operation_performed": "move"
                }
            
            if dest_path.exists():
                return {
                    "success": False,
                    "message": f"Destination file already exists: {destination_path}",
                    "file_path": file_path,
                    "operation_performed": "move"
                }
            
            if create_missing_folders:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            return {
                "success": True,
                "message": f"File moved successfully from {file_path} to {destination_path}",
                "file_path": destination_path,
                "operation_performed": "move"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to move file: {str(e)}",
                "file_path": file_path,
                "operation_performed": "move"
            }
    
    def copy_file(self, file_path: str, destination_path: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Copy a file to a new location in the vault"""
        try:
            source_path = self._get_safe_path(file_path)
            dest_path = self._get_safe_path(destination_path)
            
            if not source_path.exists():
                return {
                    "success": False,
                    "message": f"Source file does not exist: {file_path}",
                    "file_path": file_path,
                    "operation_performed": "copy"
                }
            
            if dest_path.exists():
                return {
                    "success": False,
                    "message": f"Destination file already exists: {destination_path}",
                    "file_path": file_path,
                    "operation_performed": "copy"
                }
            
            if create_missing_folders:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(str(source_path), str(dest_path))
            
            return {
                "success": True,
                "message": f"File copied successfully from {file_path} to {destination_path}",
                "file_path": destination_path,
                "operation_performed": "copy"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to copy file: {str(e)}",
                "file_path": file_path,
                "operation_performed": "copy"
            }
    
    def search_vault(self, query: str, search_type: str = "content", file_types: Optional[List[str]] = None, 
                    max_results: int = 50, include_context: bool = True) -> Dict[str, Any]:
        """Search vault content"""
        try:
            if self.sandbox_mode:
                return self._get_mock_search_results(query)
            
            results = []
            search_start = datetime.now()
            
            file_extensions = [f".{ft}" for ft in file_types] if file_types else ['.md', '.txt']
            
            for file_path in self.vault_root.rglob('*'):
                if not file_path.is_file() or file_path.suffix.lower() not in file_extensions:
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    relative_path = str(file_path.relative_to(self.vault_root))
                    
                    if search_type == "filename":
                        if query.lower() in file_path.name.lower():
                            results.append({
                                "file_path": relative_path,
                                "file_name": file_path.name,
                                "match_type": "filename",
                                "snippet": file_path.name,
                                "line_number": None,
                                "relevance_score": 1.0
                            })
                    
                    elif search_type == "content":
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if query.lower() in line.lower():
                                context_start = max(0, i - 2) if include_context else i
                                context_end = min(len(lines), i + 3) if include_context else i + 1
                                snippet = '\n'.join(lines[context_start:context_end])
                                
                                results.append({
                                    "file_path": relative_path,
                                    "file_name": file_path.name,
                                    "match_type": "content",
                                    "snippet": snippet,
                                    "line_number": i + 1,
                                    "relevance_score": 0.8
                                })
                                
                                if len(results) >= max_results:
                                    break
                    
                    elif search_type == "tags":
                        tags = self._extract_tags(content)
                        if any(query.lower() in tag.lower() for tag in tags):
                            matching_tags = [tag for tag in tags if query.lower() in tag.lower()]
                            results.append({
                                "file_path": relative_path,
                                "file_name": file_path.name,
                                "match_type": "tags",
                                "snippet": f"Tags: {', '.join(matching_tags)}",
                                "line_number": None,
                                "relevance_score": 0.9
                            })
                    
                    elif search_type == "links":
                        links = self._extract_links(content)
                        if any(query.lower() in link.lower() for link in links):
                            matching_links = [link for link in links if query.lower() in link.lower()]
                            results.append({
                                "file_path": relative_path,
                                "file_name": file_path.name,
                                "match_type": "links",
                                "snippet": f"Links: {', '.join(matching_links)}",
                                "line_number": None,
                                "relevance_score": 0.7
                            })
                    
                    if len(results) >= max_results:
                        break
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            search_time = (datetime.now() - search_start).total_seconds()
            
            # Sort by relevance score
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return {
                "query": query,
                "total_results": len(results),
                "results": results[:max_results],
                "search_time": search_time
            }
            
        except Exception as e:
            return {
                "query": query,
                "total_results": 0,
                "results": [],
                "search_time": 0.0,
                "error": f"Search failed: {str(e)}"
            }
    
    def _get_mock_search_results(self, query: str) -> Dict[str, Any]:
        """Return mock search results for sandbox mode"""
        return {
            "query": query,
            "total_results": 3,
            "results": [
                {
                    "file_path": "Projects/Project A.md",
                    "file_name": "Project A.md",
                    "match_type": "content",
                    "snippet": f"This is a sample match for '{query}' in the content.",
                    "line_number": 5,
                    "relevance_score": 0.9
                },
                {
                    "file_path": "Resources/Articles.md",
                    "file_name": "Articles.md", 
                    "match_type": "content",
                    "snippet": f"Another example where '{query}' appears in the text.",
                    "line_number": 12,
                    "relevance_score": 0.8
                },
                {
                    "file_path": f"{query.title()} Notes.md",
                    "file_name": f"{query.title()} Notes.md",
                    "match_type": "filename",
                    "snippet": f"{query.title()} Notes.md",
                    "line_number": None,
                    "relevance_score": 1.0
                }
            ],
            "search_time": 0.1
        }
    
    def create_backup(self, backup_name: Optional[str] = None, include_settings: bool = True, 
                     compress: bool = True) -> Dict[str, Any]:
        """Create a backup of the vault"""
        try:
            if self.sandbox_mode:
                return {
                    "success": True,
                    "backup_path": f"/tmp/vault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    "backup_size": 1048576,
                    "files_backed_up": 25,
                    "backup_time": datetime.now().isoformat()
                }
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = backup_name or f"vault_backup_{timestamp}"
            
            backup_dir = self.vault_root.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            if compress:
                backup_path = backup_dir / f"{backup_name}.zip"
                files_backed_up = 0
                
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in self.vault_root.rglob('*'):
                        if file_path.is_file():
                            if not include_settings and '.obsidian' in file_path.parts:
                                continue
                            
                            arcname = file_path.relative_to(self.vault_root)
                            zipf.write(file_path, arcname)
                            files_backed_up += 1
                
                backup_size = backup_path.stat().st_size
            else:
                backup_path = backup_dir / backup_name
                shutil.copytree(self.vault_root, backup_path)
                
                files_backed_up = sum(1 for _ in backup_path.rglob('*') if _.is_file())
                backup_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "backup_size": backup_size,
                "files_backed_up": files_backed_up,
                "backup_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "backup_path": "",
                "backup_size": 0,
                "files_backed_up": 0,
                "backup_time": datetime.now().isoformat(),
                "error": f"Backup failed: {str(e)}"
            }
