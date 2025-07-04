#!/usr/bin/env python3
"""
Demonstration of the agent's vault structure access capabilities
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig

def demonstrate_vault_access():
    """Demonstrate that agents now have full vault structure access"""
    print("🏛️  VAULT STRUCTURE ACCESS DEMONSTRATION")
    print("=" * 50)
    
    # Setup LLM config (will work with dummy key for structure access)
    llm_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=os.getenv("OPENAI_API_KEY", "dummy-key-for-demo"),
        stream=False,
        output_response=True
    )
    
    # Create a demo vault
    demo_vault = project_root / "demo_vault"
    demo_vault.mkdir(exist_ok=True)
    
    # Create sample files and folders
    (demo_vault / "README.md").write_text("# Demo Vault\\n\\nThis is a demonstration vault.")
    
    notes_dir = demo_vault / "Notes"
    notes_dir.mkdir(exist_ok=True)
    (notes_dir / "meeting-notes.md").write_text("# Meeting Notes\\n\\n- Important points")
    (notes_dir / "project-ideas.md").write_text("# Project Ideas\\n\\n- AI integration")
    
    research_dir = demo_vault / "Research"
    research_dir.mkdir(exist_ok=True)
    (research_dir / "ai-trends.md").write_text("# AI Trends\\n\\n- Large Language Models")
    
    archive_dir = demo_vault / "Archive"
    archive_dir.mkdir(exist_ok=True)
    (archive_dir / "old-notes.md").write_text("# Old Notes\\n\\n- Archived content")
    
    try:
        # Initialize the vault manager agent
        print("🤖 Initializing VaultManagerAgent...")
        vault_agent = VaultManagerAgent(llm_config=llm_config, vault_root=str(demo_vault))
        print(f"   ✓ Agent initialized with vault: {vault_agent.vault_tools.vault_root}")
        
        # Demonstrate vault structure access
        print("\\n📊 VAULT STRUCTURE ACCESS:")
        print("-" * 30)
        
        structure = vault_agent.vault_tools.get_vault_structure(include_content=True)
        
        print(f"📁 Total Folders: {structure.get('total_folders', 0)}")
        print(f"📄 Total Files: {structure.get('total_files', 0)}")
        print(f"💾 Total Size: {structure.get('total_size', 0)} bytes")
        
        # Show folder structure
        if 'structure' in structure:
            print("\\n🗂️  FOLDER HIERARCHY:")
            def print_structure(item, level=0):
                indent = "  " * level
                if item.get('type') == 'folder':
                    print(f"{indent}📁 {item.get('name', 'Unknown')}/")
                    for child in item.get('children', []):
                        print_structure(child, level + 1)
                else:
                    size = item.get('size', 0)
                    print(f"{indent}📄 {item.get('name', 'Unknown')} ({size} bytes)")
            
            print_structure(structure['structure'])
        
        # Demonstrate file operations
        print("\\n🔧 FILE OPERATIONS:")
        print("-" * 20)
        
        # Create a new file
        new_file_path = str(demo_vault / "agent-created.md")
        result = vault_agent.create_file(new_file_path, "# Agent Created\\n\\nThis file was created by the agent!")
        print(f"✓ Created file: {result.get('success', False)}")
        
        # Search for content
        print("\\n🔍 SEARCH CAPABILITIES:")
        print("-" * 20)
        
        search_results = vault_agent.vault_tools.search_vault("AI", "content")
        print(f"📋 Found {len(search_results.get('results', []))} matches for 'AI'")
        
        for i, result in enumerate(search_results.get('results', [])[:3]):  # Show first 3
            print(f"   {i+1}. {result.get('file_name', 'Unknown')} - {result.get('snippet', 'No snippet')[:50]}...")
        
        # Demonstrate batch operations
        print("\\n⚡ BATCH OPERATIONS:")
        print("-" * 18)
        
        batch_ops = [
            {
                "operation": "create",
                "file_path": str(demo_vault / "batch1.md"),
                "content": "# Batch File 1\\n\\nCreated in batch operation."
            },
            {
                "operation": "create", 
                "file_path": str(demo_vault / "batch2.md"),
                "content": "# Batch File 2\\n\\nAlso created in batch."
            }
        ]
        
        batch_result = vault_agent.batch_file_operations(batch_ops)
        print(f"✓ Batch completed: {batch_result['completed_operations']} success, {batch_result['failed_operations']} failed")
        
        print("\\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 50)
        print("✅ The agent now has FULL ACCESS to vault structure!")
        print("✅ Can read, create, modify, and organize files")
        print("✅ Supports intelligent search and batch operations")
        print("✅ No more 'no access to vault structure' errors!")
        
        # Show the final state
        final_structure = vault_agent.vault_tools.get_vault_structure()
        print(f"\\n📈 Final vault stats:")
        print(f"   📁 Folders: {final_structure.get('total_folders', 0)}")
        print(f"   📄 Files: {final_structure.get('total_files', 0)}")
        print(f"   💾 Size: {final_structure.get('total_size', 0)} bytes")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\\n🧹 Cleaning up demo files...")
        import shutil
        if demo_vault.exists():
            shutil.rmtree(demo_vault)
        print("✓ Cleanup completed")

if __name__ == "__main__":
    demonstrate_vault_access()
