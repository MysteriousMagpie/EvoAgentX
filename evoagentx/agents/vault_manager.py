"""
Specialized agent for vault structure management with comprehensive file operations.
"""

from typing import Dict, Any, List, Optional
from evoagentx.agents import CustomizeAgent
from evoagentx.models import LLMConfig
from evoagentx.tools.vault_tools_simple import ObsidianVaultTools


class VaultManagerAgent:
    """Specialized agent for comprehensive vault structure management"""
    
    def __init__(self, llm_config: LLMConfig, vault_root: Optional[str] = None):
        self.vault_tools = ObsidianVaultTools(vault_root)
        self.llm_config = llm_config
        
        # Create specialized agents for different vault operations
        self._create_structure_agent()
        self._create_file_manager_agent()
        self._create_search_agent()
        self._create_organization_agent()
    
    def _create_structure_agent(self):
        """Create agent specialized in vault structure analysis"""
        self.structure_agent = CustomizeAgent(
            name="VaultStructureAnalyzer",
            description="Analyzes and reports on vault structure, organization, and hierarchy",
            llm_config=self.llm_config,
            system_prompt="""You are a vault structure expert. You analyze Obsidian vaults to provide detailed insights about:
- File organization and folder hierarchy
- Content distribution and patterns  
- Interconnections between notes
- Potential improvements to vault structure
- Identification of orphaned or poorly connected content

Provide clear, actionable insights about vault organization.""",
            prompt="""Analyze the vault structure data provided and give comprehensive insights:

VAULT DATA:
{vault_data}

Please provide:
1. Overall assessment of vault organization
2. Strengths of current structure
3. Areas for improvement
4. Specific recommendations
5. File distribution analysis
6. Connectivity insights

Focus on practical, actionable suggestions for better vault organization.""",
            inputs=[
                {"name": "vault_data", "type": "str", "description": "JSON data about vault structure"}
            ],
            outputs=[
                {"name": "analysis", "type": "str", "description": "Comprehensive vault structure analysis"},
                {"name": "recommendations", "type": "str", "description": "Specific improvement recommendations"},
                {"name": "organization_score", "type": "str", "description": "Overall organization rating"}
            ]
        )
    
    def _create_file_manager_agent(self):
        """Create agent specialized in file operations"""
        self.file_manager_agent = CustomizeAgent(
            name="VaultFileManager",
            description="Manages file operations like creation, modification, and organization",
            llm_config=self.llm_config,
            system_prompt="""You are a file management expert for Obsidian vaults. You help with:
- Creating well-structured markdown files
- Organizing files into logical folder structures
- Moving and renaming files for better organization
- Managing file content and metadata
- Establishing consistent naming conventions

Always prioritize vault organization and user workflow efficiency.""",
            prompt="""Based on the user's request, plan the file operations needed:

USER REQUEST: {user_request}
CURRENT VAULT STATE: {vault_context}

Provide a detailed plan for file operations including:
1. Specific files to create/modify/move
2. Folder structure changes needed
3. Content templates for new files
4. Naming conventions to follow
5. Step-by-step operation sequence

Be specific about file paths and content structure.""",
            inputs=[
                {"name": "user_request", "type": "str", "description": "What the user wants to accomplish"},
                {"name": "vault_context", "type": "str", "description": "Current vault structure and relevant context"}
            ],
            outputs=[
                {"name": "operation_plan", "type": "str", "description": "Detailed plan for file operations"},
                {"name": "file_templates", "type": "str", "description": "Content templates for new files"},
                {"name": "organization_impact", "type": "str", "description": "How changes improve organization"}
            ]
        )
    
    def _create_search_agent(self):
        """Create agent specialized in vault search and discovery"""
        self.search_agent = CustomizeAgent(
            name="VaultSearchExpert",
            description="Performs intelligent search and content discovery across the vault",
            llm_config=self.llm_config,
            system_prompt="""You are a search and discovery expert for knowledge vaults. You help users:
- Find relevant content across their vault
- Discover connections between notes
- Identify knowledge gaps and opportunities
- Suggest related content based on search results
- Interpret search results in meaningful ways

Focus on helping users discover valuable insights from their knowledge base.""",
            prompt="""Analyze the search results and provide intelligent insights:

SEARCH QUERY: {search_query}
SEARCH RESULTS: {search_results}
SEARCH CONTEXT: {search_context}

Provide:
1. Summary of what was found
2. Key insights from the results
3. Related content suggestions
4. Knowledge gaps identified
5. Recommended follow-up searches
6. Connections between found content

Help the user understand the broader context of their search.""",
            inputs=[
                {"name": "search_query", "type": "str", "description": "The original search query"},
                {"name": "search_results", "type": "str", "description": "Raw search results from vault"},
                {"name": "search_context", "type": "str", "description": "Additional context about the search"}
            ],
            outputs=[
                {"name": "search_insights", "type": "str", "description": "Intelligent analysis of search results"},
                {"name": "related_suggestions", "type": "str", "description": "Suggestions for related content"},
                {"name": "knowledge_gaps", "type": "str", "description": "Identified gaps in knowledge base"}
            ]
        )
    
    def _create_organization_agent(self):
        """Create agent specialized in vault reorganization"""
        self.organization_agent = CustomizeAgent(
            name="VaultOrganizer",
            description="Plans and executes comprehensive vault reorganization strategies",
            llm_config=self.llm_config,
            system_prompt="""You are a vault organization strategist. You help users restructure their Obsidian vaults for:
- Better information hierarchy
- Improved discoverability
- Logical content grouping
- Efficient navigation
- Scalable organization systems

Create practical, implementable reorganization plans that preserve content while improving structure.""",
            prompt="""Create a comprehensive reorganization plan:

ORGANIZATION GOAL: {organization_goal}
CURRENT STRUCTURE: {current_structure}
USER PREFERENCES: {user_preferences}

Develop a plan that includes:
1. New folder structure proposal
2. File categorization strategy
3. Migration plan with priorities
4. Naming convention standards
5. Maintenance guidelines
6. Implementation timeline

Ensure the plan is practical and maintains vault usability during transition.""",
            inputs=[
                {"name": "organization_goal", "type": "str", "description": "What the user wants to achieve"},
                {"name": "current_structure", "type": "str", "description": "Current vault structure"},
                {"name": "user_preferences", "type": "str", "description": "User preferences and constraints"}
            ],
            outputs=[
                {"name": "reorganization_plan", "type": "str", "description": "Comprehensive reorganization strategy"},
                {"name": "implementation_steps", "type": "str", "description": "Step-by-step implementation guide"},
                {"name": "maintenance_guidelines", "type": "str", "description": "Guidelines for maintaining organization"}
            ]
        )
    
    def get_vault_structure(self, include_content: bool = False, max_depth: Optional[int] = None, 
                           file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive vault structure with AI analysis"""
        # Get raw structure data
        structure_data = self.vault_tools.get_vault_structure(include_content, max_depth, file_types)
        
        # Get AI analysis of the structure
        analysis_result = self.structure_agent(
            inputs={
                "vault_data": str(structure_data)
            }
        )
        
        # Combine raw data with AI insights
        return {
            "raw_structure": structure_data,
            "ai_analysis": {
                "analysis": analysis_result.content.analysis,
                "recommendations": analysis_result.content.recommendations,
                "organization_score": analysis_result.content.organization_score
            }
        }
    
    def perform_file_operations(self, user_request: str, vault_context: Optional[str] = None) -> Dict[str, Any]:
        """Plan and execute file operations based on user request"""
        if not vault_context:
            vault_context = str(self.vault_tools.get_vault_structure())
        
        # Get AI plan for file operations
        plan_result = self.file_manager_agent(
            inputs={
                "user_request": user_request,
                "vault_context": vault_context
            }
        )
        
        # Return the plan (in a real implementation, you'd execute the operations)
        return {
            "operation_plan": plan_result.content.operation_plan,
            "file_templates": plan_result.content.file_templates,
            "organization_impact": plan_result.content.organization_impact,
            "plan_generated": True,
            "execution_note": "Plan generated. Use specific file operation methods to execute."
        }
    
    def intelligent_search(self, query: str, search_type: str = "content", 
                          file_types: Optional[List[str]] = None, max_results: int = 50) -> Dict[str, Any]:
        """Perform intelligent search with AI-powered analysis"""
        # Get raw search results
        search_results = self.vault_tools.search_vault(query, search_type, file_types, max_results)
        
        # Get AI analysis of results
        analysis_result = self.search_agent(
            inputs={
                "search_query": query,
                "search_results": str(search_results),
                "search_context": f"Search type: {search_type}, File types: {file_types}"
            }
        )
        
        return {
            "raw_results": search_results,
            "ai_insights": {
                "search_insights": analysis_result.content.search_insights,
                "related_suggestions": analysis_result.content.related_suggestions,
                "knowledge_gaps": analysis_result.content.knowledge_gaps
            }
        }
    
    def plan_vault_reorganization(self, organization_goal: str, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create comprehensive vault reorganization plan"""
        current_structure = self.vault_tools.get_vault_structure(include_content=False)
        
        reorganization_result = self.organization_agent(
            inputs={
                "organization_goal": organization_goal,
                "current_structure": str(current_structure),
                "user_preferences": str(user_preferences or {})
            }
        )
        
        return {
            "current_structure": current_structure,
            "reorganization_plan": reorganization_result.content.reorganization_plan,
            "implementation_steps": reorganization_result.content.implementation_steps,
            "maintenance_guidelines": reorganization_result.content.maintenance_guidelines
        }
    
    # Direct tool access methods for file operations
    def create_file(self, file_path: str, content: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Create a new file in the vault"""
        return self.vault_tools.create_file(file_path, content, create_missing_folders)
    
    def update_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Update an existing file in the vault"""
        return self.vault_tools.update_file(file_path, content)
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file from the vault"""
        return self.vault_tools.delete_file(file_path)
    
    def move_file(self, file_path: str, destination_path: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Move a file to a new location in the vault"""
        return self.vault_tools.move_file(file_path, destination_path, create_missing_folders)
    
    def copy_file(self, file_path: str, destination_path: str, create_missing_folders: bool = True) -> Dict[str, Any]:
        """Copy a file to a new location in the vault"""
        return self.vault_tools.copy_file(file_path, destination_path, create_missing_folders)
    
    def batch_file_operations(self, operations: List[Dict[str, Any]], continue_on_error: bool = True) -> Dict[str, Any]:
        """Perform multiple file operations in batch"""
        results = []
        errors = []
        completed = 0
        failed = 0
        
        for op in operations:
            operation_type = op.get("operation")
            file_path = op.get("file_path")
            
            try:
                # Validate required parameters
                if not operation_type:
                    raise ValueError("Operation type is required")
                if not file_path:
                    raise ValueError("File path is required")
                
                # Ensure file_path is a string
                if not isinstance(file_path, str):
                    raise ValueError("File path must be a string")
                
                if operation_type == "create":
                    result = self.create_file(file_path, op.get("content", ""), op.get("create_missing_folders", True))
                elif operation_type == "update":
                    result = self.update_file(file_path, op.get("content", ""))
                elif operation_type == "delete":
                    result = self.delete_file(file_path)
                elif operation_type == "move":
                    destination_path = op.get("destination_path")
                    if not destination_path or not isinstance(destination_path, str):
                        raise ValueError("Destination path is required and must be a string for move operation")
                    result = self.move_file(file_path, destination_path, op.get("create_missing_folders", True))
                elif operation_type == "copy":
                    destination_path = op.get("destination_path")
                    if not destination_path or not isinstance(destination_path, str):
                        raise ValueError("Destination path is required and must be a string for copy operation")
                    result = self.copy_file(file_path, destination_path, op.get("create_missing_folders", True))
                else:
                    result = {"success": False, "message": f"Unknown operation: {operation_type}"}
                
                results.append(result)
                if result.get("success"):
                    completed += 1
                else:
                    failed += 1
                    errors.append(f"Operation {operation_type} on {file_path}: {result.get('message')}")
                    
            except Exception as e:
                error_msg = f"Exception in {operation_type or 'unknown'} operation on {file_path or 'unknown'}: {str(e)}"
                errors.append(error_msg)
                failed += 1
                results.append({"success": False, "message": error_msg})
                
                if not continue_on_error:
                    break
        
        return {
            "success": failed == 0,
            "completed_operations": completed,
            "failed_operations": failed,
            "results": results,
            "errors": errors
        }
