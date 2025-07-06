"""
Fixed Enhanced Vault Management API with Dev-Pipe Integration

This module fixes the schema mismatches and implements all the missing vault management 
endpoints with proper dev-pipe protocol integration for communication, monitoring, and error handling.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
import asyncio
import json
import time
from datetime import datetime, timedelta
import uuid
import zipfile
import shutil
import tempfile
from pathlib import Path

from ..services.devpipe_integration import dev_pipe
from ..models.obsidian_schemas import (
    VaultStructureRequest, VaultStructureResponse,
    FileOperationRequest, FileOperationResponse,
    BatchFileOperationRequest, BatchFileOperationResponse,
    VaultSearchRequest, VaultSearchResponse,
    VaultOrganizationRequest, VaultOrganizationResponse,
    VaultBackupRequest, VaultBackupResponse,
    VaultContextRequest, VaultContextResponse
)
from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig
import os

router = APIRouter(prefix="/api/obsidian/vault", tags=["vault-management"])

def get_llm_config():
    """Get LLM configuration for vault manager"""
    return OpenAILLMConfig(
        model="gpt-4",
        openai_key=os.getenv("OPENAI_API_KEY"),
        stream=False,
        output_response=True,
        max_tokens=4000,
    )

def get_vault_manager(vault_root: Optional[str] = None) -> VaultManagerAgent:
    """Get or create the global vault manager instance"""
    return VaultManagerAgent(llm_config=get_llm_config(), vault_root=vault_root)

@router.post("/structure", response_model=VaultStructureResponse)
async def get_vault_structure_enhanced(request: VaultStructureRequest, background_tasks: BackgroundTasks):
    """Get comprehensive vault structure with AI analysis and dev-pipe integration"""
    
    task_id = await dev_pipe.create_task(
        task_type="vault_analysis",
        operation="get_structure",
        parameters={
            "include_content": request.include_content,
            "max_depth": request.max_depth,
            "file_types": request.file_types or []
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "get_structure", 20,
                                     details={"stage": "initializing"})
        
        manager = get_vault_manager()
        
        await dev_pipe.notify_progress(task_id, "get_structure", 50,
                                     details={"stage": "analyzing_structure"})
        
        vault_structure = manager.get_vault_structure(
            include_content=request.include_content,
            max_depth=request.max_depth,
            file_types=request.file_types
        )
        
        await dev_pipe.notify_progress(task_id, "get_structure", 80,
                                     details={"stage": "ai_analysis"})
        
        # Use the structure agent for AI analysis
        analysis_prompt = f"Analyze this vault structure and provide insights:\n{json.dumps(vault_structure, default=str, indent=2)}"
        ai_analysis_result = manager.structure_agent(inputs={"vault_data": analysis_prompt})
        ai_analysis = ai_analysis_result.content if hasattr(ai_analysis_result, 'content') else str(ai_analysis_result)
        
        # Parse AI analysis to extract components
        analysis_parts = ai_analysis.split("RECOMMENDATIONS:")
        analysis_text = analysis_parts[0].replace("ANALYSIS:", "").strip()
        recommendations_text = analysis_parts[1].split("ORGANIZATION_SCORE:")[0].strip() if len(analysis_parts) > 1 else ""
        
        # Extract organization score
        score_part = ai_analysis.split("ORGANIZATION_SCORE:")
        organization_score = score_part[1].strip().split()[0] if len(score_part) > 1 else "N/A"
        
        await dev_pipe.notify_progress(task_id, "get_structure", 95,
                                     details={"stage": "finalizing"})
        
        response = VaultStructureResponse(
            vault_name=vault_structure.get("vault_name", "Unknown"),
            total_files=vault_structure.get("total_files", 0),
            total_folders=vault_structure.get("total_folders", 0),
            total_size=vault_structure.get("total_size", 0),
            structure=vault_structure.get("structure", {}),
            recent_files=vault_structure.get("recent_files", []),
            orphaned_files=vault_structure.get("orphaned_files", []),
            analysis=analysis_text,
            recommendations=recommendations_text,
            organization_score=organization_score
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "get_structure", 
            {
                "vault_name": response.vault_name,
                "total_files": response.total_files,
                "organization_score": response.organization_score
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "get_structure",
            "request_params": request.dict()
        })
        raise HTTPException(status_code=500, detail=f"Structure analysis error: {str(e)}")

@router.post("/file/operation", response_model=FileOperationResponse)
async def perform_file_operation_enhanced(request: FileOperationRequest, background_tasks: BackgroundTasks):
    """Perform single file operation with dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="file_operation",
        operation=request.operation,
        parameters={
            "file_path": request.file_path,
            "operation": request.operation,
            "has_content": bool(request.content),
            "has_destination": bool(request.destination_path)
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, request.operation, 20,
                                     details={"stage": "validating_input"})
        
        manager = get_vault_manager()
        
        await dev_pipe.notify_progress(task_id, request.operation, 50,
                                     details={"stage": "executing_operation"})
        
        if request.operation == "create":
            result = manager.create_file(
                request.file_path, 
                request.content or "", 
                request.create_missing_folders
            )
        elif request.operation == "update":
            result = manager.update_file(request.file_path, request.content or "")
        elif request.operation == "delete":
            result = manager.delete_file(request.file_path)
        elif request.operation == "move":
            if not request.destination_path:
                raise ValueError("Destination path required for move operation")
            result = manager.move_file(
                request.file_path, 
                request.destination_path, 
                request.create_missing_folders
            )
        elif request.operation == "copy":
            if not request.destination_path:
                raise ValueError("Destination path required for copy operation")
            result = manager.copy_file(
                request.file_path, 
                request.destination_path, 
                request.create_missing_folders
            )
        else:
            raise ValueError(f"Unknown operation: {request.operation}")
        
        await dev_pipe.notify_progress(task_id, request.operation, 90,
                                     details={"stage": "completing"})
        
        response = FileOperationResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            file_path=request.file_path,
            operation_performed=request.operation
        )
        
        await dev_pipe.send_completion_notification(
            task_id, request.operation,
            {
                "success": response.success,
                "file_path": response.file_path,
                "operation": response.operation_performed
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": request.operation,
            "file_path": request.file_path
        })
        raise HTTPException(status_code=500, detail=f"File operation error: {str(e)}")

@router.post("/file/batch", response_model=BatchFileOperationResponse)
async def perform_batch_file_operations_enhanced(request: BatchFileOperationRequest, background_tasks: BackgroundTasks):
    """Perform batch file operations with dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="batch_file_operations",
        operation="batch_operations",
        parameters={
            "operation_count": len(request.operations),
            "continue_on_error": request.continue_on_error
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "batch_operations", 10,
                                     details={"stage": "preparing_batch"})
        
        manager = get_vault_manager()
        
        # Convert operations to the format expected by VaultManagerAgent
        operations_data = []
        for op in request.operations:
            op_data = {
                "operation": op.operation,
                "file_path": op.file_path,
                "content": op.content,
                "destination_path": op.destination_path,
                "create_missing_folders": op.create_missing_folders
            }
            operations_data.append(op_data)
        
        await dev_pipe.notify_progress(task_id, "batch_operations", 30,
                                     details={"stage": "executing_operations"})
        
        result = manager.batch_file_operations(operations_data, request.continue_on_error)
        
        await dev_pipe.notify_progress(task_id, "batch_operations", 80,
                                     details={"stage": "processing_results"})
        
        # Process results
        results = []
        errors = []
        completed_operations = 0
        failed_operations = 0
        
        for i, operation in enumerate(request.operations):
            if i < len(result.get("results", [])):
                op_result = result["results"][i]
                if op_result.get("success", False):
                    completed_operations += 1
                else:
                    failed_operations += 1
                    errors.append(op_result.get("message", "Unknown error"))
                
                results.append(FileOperationResponse(
                    success=op_result.get("success", False),
                    message=op_result.get("message", ""),
                    file_path=operation.file_path,
                    operation_performed=operation.operation
                ))
        
        response = BatchFileOperationResponse(
            success=result.get("success", False),
            completed_operations=completed_operations,
            failed_operations=failed_operations,
            results=results,
            errors=errors
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "batch_operations",
            {
                "success": response.success,
                "completed": response.completed_operations,
                "failed": response.failed_operations
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "batch_operations",
            "operation_count": len(request.operations)
        })
        raise HTTPException(status_code=500, detail=f"Batch operation error: {str(e)}")

@router.post("/search", response_model=VaultSearchResponse)
async def search_vault_enhanced(request: VaultSearchRequest, background_tasks: BackgroundTasks):
    """Search vault content with AI insights and dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="vault_search",
        operation="intelligent_search",
        parameters={
            "query": request.query,
            "search_type": request.search_type,
            "max_results": request.max_results
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "intelligent_search", 20,
                                     details={"stage": "preparing_search"})
        
        manager = get_vault_manager()
        
        await dev_pipe.notify_progress(task_id, "intelligent_search", 50,
                                     details={"stage": "executing_search"})
        
        search_results = manager.intelligent_search(
            query=request.query,
            search_type=request.search_type,
            file_types=request.file_types,
            max_results=request.max_results
        )
        
        await dev_pipe.notify_progress(task_id, "intelligent_search", 90,
                                     details={"stage": "formatting_results"})
        
        response = VaultSearchResponse(
            query=request.query,
            total_results=search_results.get("total_results", 0),
            results=search_results.get("results", []),
            search_time=search_results.get("search_time", 0.0)
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "intelligent_search",
            {
                "query": response.query,
                "total_results": response.total_results,
                "search_time": response.search_time
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "intelligent_search",
            "query": request.query
        })
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.post("/organize", response_model=VaultOrganizationResponse)
async def organize_vault_enhanced(request: VaultOrganizationRequest, background_tasks: BackgroundTasks):
    """Plan vault reorganization with AI assistance and dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="vault_organization",
        operation="plan_reorganization",
        parameters={
            "goal": request.organization_goal,
            "dry_run": request.dry_run
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "plan_reorganization", 20,
                                     details={"stage": "analyzing_current_structure"})
        
        manager = get_vault_manager()
        
        await dev_pipe.notify_progress(task_id, "plan_reorganization", 60,
                                     details={"stage": "generating_plan"})
        
        reorganization_result = manager.plan_vault_reorganization(
            organization_goal=request.organization_goal,
            user_preferences=request.preferences
        )
        
        await dev_pipe.notify_progress(task_id, "plan_reorganization", 90,
                                     details={"stage": "finalizing_plan"})
        
        response = VaultOrganizationResponse(
            reorganization_plan=reorganization_result.get("reorganization_plan", ""),
            suggested_changes=reorganization_result.get("suggested_changes", []),
            estimated_changes_count=reorganization_result.get("estimated_changes_count", 0),
            dry_run=request.dry_run,
            execution_steps=reorganization_result.get("execution_steps", [])
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "plan_reorganization",
            {
                "success": True,
                "estimated_changes": response.estimated_changes_count,
                "dry_run": response.dry_run
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "plan_reorganization",
            "goal": request.organization_goal
        })
        raise HTTPException(status_code=500, detail=f"Organization error: {str(e)}")

@router.post("/backup", response_model=VaultBackupResponse)
async def create_vault_backup_enhanced(request: VaultBackupRequest, background_tasks: BackgroundTasks):
    """Create a backup of the vault with dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="vault_backup",
        operation="create_backup",
        parameters={
            "backup_name": request.backup_name,
            "include_settings": request.include_settings,
            "compress": request.compress
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "create_backup", 10,
                                     details={"stage": "initializing_backup"})
        
        # Get the vault path from environment or default
        vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "./vault")
        if not os.path.exists(vault_path):
            raise HTTPException(status_code=404, detail="Vault directory not found")
        
        vault_path = Path(vault_path)
        
        # Generate backup name if not provided
        backup_name = request.backup_name or f"vault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        backup_dir = Path("./backups")
        backup_dir.mkdir(exist_ok=True)
        
        await dev_pipe.notify_progress(task_id, "create_backup", 20,
                                     details={"stage": "scanning_files"})
        
        # Count files to backup
        files_to_backup = []
        total_size = 0
        
        for file_path in vault_path.rglob("*"):
            if file_path.is_file():
                # Skip certain files/directories
                if any(skip in str(file_path) for skip in ['.git', '.DS_Store', '__pycache__']):
                    continue
                files_to_backup.append(file_path)
                total_size += file_path.stat().st_size
        
        await dev_pipe.notify_progress(task_id, "create_backup", 40,
                                     details={
                                         "stage": "preparing_archive",
                                         "files_found": len(files_to_backup),
                                         "total_size": total_size
                                     })
        
        # Create backup archive
        if request.compress:
            backup_path = backup_dir / f"{backup_name}.zip"
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for i, file_path in enumerate(files_to_backup):
                    # Calculate relative path
                    rel_path = file_path.relative_to(vault_path)
                    zipf.write(file_path, rel_path)
                    
                    # Update progress
                    if i % 10 == 0:  # Update every 10 files
                        progress = 40 + int((i / len(files_to_backup)) * 40)
                        await dev_pipe.notify_progress(task_id, "create_backup", progress,
                                                     details={
                                                         "stage": "archiving_files",
                                                         "files_processed": i,
                                                         "total_files": len(files_to_backup)
                                                     })
                
                # Include settings if requested
                if request.include_settings:
                    settings_path = vault_path / ".obsidian"
                    if settings_path.exists():
                        for settings_file in settings_path.rglob("*"):
                            if settings_file.is_file():
                                rel_path = settings_file.relative_to(vault_path)
                                zipf.write(settings_file, rel_path)
        else:
            # Create uncompressed backup directory
            backup_path = backup_dir / backup_name
            shutil.copytree(vault_path, backup_path, 
                          ignore=shutil.ignore_patterns('.git', '.DS_Store', '__pycache__'))
        
        await dev_pipe.notify_progress(task_id, "create_backup", 90,
                                     details={"stage": "finalizing_backup"})
        
        # Get backup statistics
        backup_size = backup_path.stat().st_size if backup_path.is_file() else sum(
            f.stat().st_size for f in backup_path.rglob('*') if f.is_file()
        )
        
        response = VaultBackupResponse(
            success=True,
            backup_path=str(backup_path),
            backup_size=backup_size,
            files_backed_up=len(files_to_backup),
            backup_time=datetime.now()
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "create_backup",
            {
                "success": response.success,
                "backup_path": response.backup_path,
                "backup_size": response.backup_size,
                "files_backed_up": response.files_backed_up
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "create_backup",
            "backup_name": request.backup_name
        })
        raise HTTPException(status_code=500, detail=f"Backup error: {str(e)}")

@router.post("/context", response_model=VaultContextResponse)
async def analyze_vault_context_enhanced(request: VaultContextRequest, background_tasks: BackgroundTasks):
    """Analyze vault context with dev-pipe tracking"""
    
    task_id = await dev_pipe.create_task(
        task_type="vault_context",
        operation="analyze_context",
        parameters={
            "file_paths": request.file_paths,
            "content_snippets": request.content_snippets or {}
        }
    )
    
    try:
        await dev_pipe.notify_progress(task_id, "analyze_context", 20,
                                     details={"stage": "initializing_analysis"})
        
        await dev_pipe.notify_progress(task_id, "analyze_context", 50,
                                     details={"stage": "analyzing_relationships"})
        
        # Analyze the provided files and content
        relevant_notes = []
        context_parts = []
        
        for file_path in request.file_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        relevant_notes.append({
                            "path": file_path,
                            "title": os.path.basename(file_path),
                            "content_preview": content[:500] + "..." if len(content) > 500 else content,
                            "size": len(content),
                            "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
                        context_parts.append(content)
                except Exception as e:
                    # Skip files that can't be read
                    continue
        
        await dev_pipe.notify_progress(task_id, "analyze_context", 80,
                                     details={"stage": "generating_summary"})
        
        # Generate context summary
        context_summary = f"Analyzed {len(relevant_notes)} files. "
        if relevant_notes:
            total_size = sum(note["size"] for note in relevant_notes)
            context_summary += f"Total content size: {total_size} characters. "
            context_summary += f"Files include: {', '.join(note['title'] for note in relevant_notes[:5])}"
            if len(relevant_notes) > 5:
                context_summary += f" and {len(relevant_notes) - 5} more files."
        else:
            context_summary += "No accessible files found."
        
        response = VaultContextResponse(
            context_summary=context_summary,
            relevant_notes=relevant_notes
        )
        
        await dev_pipe.send_completion_notification(
            task_id, "analyze_context",
            {
                "files_analyzed": len(relevant_notes),
                "total_content_size": sum(note["size"] for note in relevant_notes)
            }
        )
        
        return response
        
    except Exception as e:
        await dev_pipe.handle_error(task_id, e, {
            "operation": "analyze_context",
            "file_paths": request.file_paths
        })
        raise HTTPException(status_code=500, detail=f"Context analysis error: {str(e)}")
