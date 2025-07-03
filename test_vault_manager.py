#!/usr/bin/env python3
"""
Test script for vault management functionality
"""
import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from evoagentx.agents.vault_manager import VaultManagerAgent
from evoagentx.models import OpenAILLMConfig

def test_vault_manager():
    """Test the vault manager functionality"""
    print("Testing Vault Manager...")
    
    # Setup LLM config
    llm_config = OpenAILLMConfig(
        model="gpt-4o-mini",
        openai_key=os.getenv("OPENAI_API_KEY", "test-key"),
        stream=False,
        output_response=True
    )
    
    # Create a test vault directory
    test_vault_dir = project_root / "test_vault"
    test_vault_dir.mkdir(exist_ok=True)
    
    # Create some test files
    (test_vault_dir / "note1.md").write_text("# Test Note 1\n\nThis is a test note.")
    (test_vault_dir / "note2.md").write_text("# Test Note 2\n\nThis is another test note.")
    
    # Create subfolder
    subfolder = test_vault_dir / "subfolder"
    subfolder.mkdir(exist_ok=True)
    (subfolder / "note3.md").write_text("# Test Note 3\n\nThis is a note in a subfolder.")
    
    try:
        # Initialize vault manager
        vault_manager = VaultManagerAgent(llm_config=llm_config, vault_root=str(test_vault_dir))
        
        print(f"✓ Vault Manager initialized with vault root: {vault_manager.vault_tools.vault_root}")
        
        # Test vault structure retrieval
        print("\n1. Testing vault structure retrieval...")
        structure = vault_manager.vault_tools.get_vault_structure(include_content=True)
        print(f"   Found {structure.get('total_files', 0)} files and {structure.get('total_folders', 0)} folders")
        
        # Test file operations
        print("\n2. Testing file operations...")
        
        # Create a new file
        test_file = test_vault_dir / "test_created.md"
        result = vault_manager.create_file(str(test_file), "# Created by Test\n\nThis file was created by the test script.")
        print(f"   Create file result: {result}")
        
        # Read the file
        if test_file.exists():
            content = test_file.read_text()
            print(f"   File content: {content[:50]}...")
        
        # Test search functionality
        print("\n3. Testing search functionality...")
        search_results = vault_manager.vault_tools.search_vault("test", "content")
        print(f"   Search results: {len(search_results.get('results', []))} matches found")
        
        # Test batch operations
        print("\n4. Testing batch operations...")
        batch_ops = [
            {
                "operation": "create",
                "file_path": str(test_vault_dir / "batch_test1.md"),
                "content": "# Batch Test 1\n\nCreated via batch operation."
            },
            {
                "operation": "create", 
                "file_path": str(test_vault_dir / "batch_test2.md"),
                "content": "# Batch Test 2\n\nAlso created via batch operation."
            }
        ]
        
        batch_result = vault_manager.batch_file_operations(batch_ops)
        print(f"   Batch operation result: {batch_result['completed_operations']} completed, {batch_result['failed_operations']} failed")
        
        print("\n✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        print("\nCleaning up test files...")
        import shutil
        if test_vault_dir.exists():
            shutil.rmtree(test_vault_dir)
        print("✓ Cleanup completed")

if __name__ == "__main__":
    test_vault_manager()
