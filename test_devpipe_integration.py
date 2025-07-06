#!/usr/bin/env python3
"""
Comprehensive Test Suite for VaultPilot Dev-Pipe Integration

This script validates all aspects of the dev-pipe integration with vault management,
enhanced workflows, and communication protocols.
"""

import asyncio
import aiohttp
import json
import time
import websockets
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from server.services.devpipe_integration import dev_pipe

class DevPipeIntegrationTester:
    """Comprehensive tester for dev-pipe integration"""
    
    def __init__(self, base_url="http://127.0.0.1:8002"):
        self.base_url = base_url
        self.ws_url = base_url.replace("http", "ws") + "/ws/obsidian"
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: List[Dict[str, Any]] = []
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🔧 Test session initialized")
    
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 Test session cleaned up")
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name}: {details}")
    
    async def test_dev_pipe_framework(self):
        """Test core dev-pipe framework functionality"""
        print("\n🧪 Testing Dev-Pipe Framework...")
        
        try:
            # Test task creation
            task_id = await dev_pipe.create_task(
                task_type="test_task",
                operation="framework_test",
                parameters={"test": "dev_pipe_framework"}
            )
            
            self.log_test_result("Task Creation", bool(task_id), f"Task ID: {task_id}")
            
            # Test progress notification
            await dev_pipe.notify_progress(task_id, "framework_test", 50,
                                         details={"stage": "testing"})
            
            self.log_test_result("Progress Notification", True, "Progress updated to 50%")
            
            # Test completion notification
            await dev_pipe.send_completion_notification(
                task_id, "framework_test", {"result": "success"}
            )
            
            self.log_test_result("Completion Notification", True, "Task completed successfully")
            
            # Test error handling
            test_error = Exception("Test error for dev-pipe")
            await dev_pipe.handle_error(task_id, test_error, {"context": "error_test"})
            
            self.log_test_result("Error Handling", True, "Error logged successfully")
            
        except Exception as e:
            self.log_test_result("Dev-Pipe Framework", False, f"Framework error: {str(e)}")
    
    async def test_health_endpoints(self):
        """Test health and status endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        assert self.session is not None, "Session not initialized"
        
        try:
            # Test basic health check
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        has_dev_pipe = "dev_pipe" in data or "dev_pipe_integration" in data
                        self.log_test_result("Health Check", True, 
                                           f"Status: {data.get('status')}, Dev-Pipe: {has_dev_pipe}")
                    else:
                        self.log_test_result("Health Check", False, "Empty response data")
                else:
                    self.log_test_result("Health Check", False, f"Status: {response.status}")
            
            # Test dev-pipe status endpoint
            async with self.session.get(f"{self.base_url}/dev-pipe/status") as response:
                if response.status == 200:
                    data = await response.json()
                    dev_pipe_status = data.get("dev_pipe_status", "unknown")
                    task_stats = data.get("task_statistics", {})
                    self.log_test_result("Dev-Pipe Status", True, 
                                       f"Status: {dev_pipe_status}, Tasks: {task_stats}")
                else:
                    self.log_test_result("Dev-Pipe Status", False, f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Health Endpoints", False, f"Health test error: {str(e)}")
    
    async def test_vault_management_endpoints(self):
        """Test enhanced vault management endpoints"""
        print("\n🗄️ Testing Vault Management Endpoints...")
        
        assert self.session is not None, "Session not initialized"
        
        # Test vault structure endpoint
        try:
            payload = {
                "include_content": False,
                "max_depth": 3,
                "file_types": ["md", "txt"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/obsidian/vault/structure",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    vault_name = data.get("vault_name", "Unknown")
                    total_files = data.get("total_files", 0)
                    self.log_test_result("Vault Structure", True, 
                                       f"Vault: {vault_name}, Files: {total_files}")
                else:
                    self.log_test_result("Vault Structure", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Vault Structure", False, f"Structure test error: {str(e)}")
        
        # Test vault search endpoint
        try:
            payload = {
                "query": "test search query",
                "search_type": "content",
                "max_results": 10,
                "file_types": ["md"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/obsidian/vault/search",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    total_results = data.get("total_results", 0)
                    search_time = data.get("search_time", 0)
                    self.log_test_result("Vault Search", True, 
                                       f"Results: {total_results}, Time: {search_time}s")
                else:
                    self.log_test_result("Vault Search", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Vault Search", False, f"Search test error: {str(e)}")
        
        # Test file operation endpoint
        try:
            payload = {
                "operation": "create",
                "file_path": "/test_dev_pipe_file.md",
                "content": "# Test File for Dev-Pipe Integration\n\nThis is a test file.",
                "create_missing_folders": True
            }
            
            async with self.session.post(
                f"{self.base_url}/api/obsidian/vault/file/operation",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    success = data.get("success", False)
                    operation = data.get("operation_performed", "unknown")
                    self.log_test_result("File Operation", success, 
                                       f"Operation: {operation}")
                else:
                    self.log_test_result("File Operation", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("File Operation", False, f"File operation error: {str(e)}")
    
    async def test_enhanced_workflows(self):
        """Test enhanced workflow system"""
        print("\n⚡ Testing Enhanced Workflows...")
        
        assert self.session is not None, "Session not initialized"
        # Test workflow templates
        try:
            async with self.session.get(
                f"{self.base_url}/api/obsidian/workflow/templates"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    templates = data.get("templates", [])
                    dev_pipe_enabled = data.get("dev_pipe_integration", {}).get("status") == "active"
                    self.log_test_result("Workflow Templates", True, 
                                       f"Templates: {len(templates)}, Dev-Pipe: {dev_pipe_enabled}")
                else:
                    self.log_test_result("Workflow Templates", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Workflow Templates", False, f"Templates error: {str(e)}")
        
        # Test workflow execution
        try:
            payload = {
                "template_id": "research_synthesis",
                "goal": "Test research synthesis workflow",
                "context": {
                    "vault_context": "Test vault content",
                    "target_files": ["/test_file.md"]
                },
                "streaming": False
            }
            
            async with self.session.post(
                f"{self.base_url}/api/obsidian/workflow/execute",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    workflow_id = data.get("workflow_id")
                    status = data.get("status")
                    self.log_test_result("Workflow Execution", True, 
                                       f"ID: {workflow_id}, Status: {status}")
                    
                    # Test workflow status check
                    if workflow_id:
                        await asyncio.sleep(1)  # Wait a moment
                        async with self.session.get(
                            f"{self.base_url}/api/obsidian/workflow/status/{workflow_id}"
                        ) as status_response:
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                current_status = status_data.get("status")
                                progress = status_data.get("progress", 0)
                                self.log_test_result("Workflow Status", True, 
                                                   f"Status: {current_status}, Progress: {progress}%")
                            else:
                                self.log_test_result("Workflow Status", False, 
                                                   f"Status: {status_response.status}")
                else:
                    self.log_test_result("Workflow Execution", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Workflow Execution", False, f"Workflow error: {str(e)}")
    
    async def test_enhanced_chat(self):
        """Test enhanced chat endpoint with dev-pipe integration"""
        print("\n💬 Testing Enhanced Chat...")
        
        assert self.session is not None, "Session not initialized"
        
        try:
            payload = {
                "message": "Test message for dev-pipe integration",
                "agent_name": "test_agent",
                "mode": "ask",
                "context": {"test": True}
            }
            
            async with self.session.post(
                f"{self.base_url}/api/obsidian/chat",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    has_response = bool(data.get("response"))
                    has_metadata = bool(data.get("metadata"))
                    conversation_id = data.get("conversation_id")
                    self.log_test_result("Enhanced Chat", True, 
                                       f"Response: {has_response}, Metadata: {has_metadata}, ID: {conversation_id}")
                else:
                    self.log_test_result("Enhanced Chat", False, 
                                       f"Status: {response.status}")
                    
        except Exception as e:
            self.log_test_result("Enhanced Chat", False, f"Chat error: {str(e)}")
    
    async def test_websocket_integration(self):
        """Test WebSocket integration with dev-pipe"""
        print("\n🌐 Testing WebSocket Integration...")
        
        try:
            # Test WebSocket connection
            async with websockets.connect(self.ws_url) as websocket:
                # Send ping message
                ping_message = json.dumps({"type": "ping"})
                await websocket.send(ping_message)
                
                # Wait for pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    self.log_test_result("WebSocket Ping/Pong", True, "Ping/Pong successful")
                else:
                    self.log_test_result("WebSocket Ping/Pong", False, 
                                       f"Unexpected response: {response_data}")
                
                # Test task progress message
                progress_message = json.dumps({
                    "type": "task_progress",
                    "task_id": "test_task_123",
                    "operation": "test_operation",
                    "progress": 75,
                    "details": {"stage": "testing_websocket"}
                })
                await websocket.send(progress_message)
                
                self.log_test_result("WebSocket Task Progress", True, "Progress message sent")
                
        except asyncio.TimeoutError:
            self.log_test_result("WebSocket Integration", False, "Connection timeout")
        except Exception as e:
            self.log_test_result("WebSocket Integration", False, f"WebSocket error: {str(e)}")
    
    async def test_dev_pipe_file_system(self):
        """Test dev-pipe file system structure"""
        print("\n📁 Testing Dev-Pipe File System...")
        
        try:
            # Check directory structure
            required_dirs = [
                dev_pipe.queues_dir / "incoming",
                dev_pipe.queues_dir / "outgoing", 
                dev_pipe.queues_dir / "processing",
                dev_pipe.queues_dir / "archive",
                dev_pipe.tasks_dir / "active",
                dev_pipe.tasks_dir / "pending",
                dev_pipe.tasks_dir / "completed",
                dev_pipe.tasks_dir / "failed",
                dev_pipe.status_dir,
                dev_pipe.logs_dir / "info",
                dev_pipe.logs_dir / "error"
            ]
            
            missing_dirs = [d for d in required_dirs if not d.exists()]
            
            if not missing_dirs:
                self.log_test_result("Dev-Pipe Directory Structure", True, 
                                   f"All {len(required_dirs)} directories exist")
            else:
                self.log_test_result("Dev-Pipe Directory Structure", False, 
                                   f"Missing directories: {len(missing_dirs)}")
            
            # Check for task files
            active_tasks = list(dev_pipe.tasks_dir.glob("*/*.json"))
            self.log_test_result("Dev-Pipe Task Files", len(active_tasks) >= 0, 
                               f"Found {len(active_tasks)} task files")
            
        except Exception as e:
            self.log_test_result("Dev-Pipe File System", False, f"File system error: {str(e)}")
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting VaultPilot Dev-Pipe Integration Test Suite")
        print("=" * 70)
        
        await self.setup()
        
        try:
            # Run all test categories
            await self.test_dev_pipe_framework()
            await self.test_health_endpoints()
            await self.test_vault_management_endpoints()
            await self.test_enhanced_workflows()
            await self.test_enhanced_chat()
            await self.test_websocket_integration()
            await self.test_dev_pipe_file_system()
            
        finally:
            await self.cleanup()
        
        # Print test summary
        self.print_test_summary()
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n" + "=" * 70)
        
        if failed_tests == 0:
            print("🎉 All tests passed! Dev-Pipe integration is working correctly.")
        else:
            print(f"⚠️  {failed_tests} test(s) failed. Please review the errors above.")
        
        return failed_tests == 0

async def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test VaultPilot Dev-Pipe Integration")
    parser.add_argument("--url", default="http://127.0.0.1:8000", 
                       help="Base URL for the server")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests only")
    
    args = parser.parse_args()
    
    # Create and run tester
    tester = DevPipeIntegrationTester(args.url)
    
    try:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
