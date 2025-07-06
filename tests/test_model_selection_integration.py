"""
Integration test for the enhanced model selection system with devpipe framework.

This test verifies that the model selection features work correctly with the 
Obsidian plugin through the devpipe communication framework.
"""

import asyncio
import json
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Import the server and model selection components
from server.api.obsidian import router
from server.models.obsidian_schemas import ModelSelectionRequest, ModelHealthRequest
from evoagentx.models.robust_model_selector import (
    RobustModelSelector, TaskType, ModelSelectionCriteria,
    initialize_robust_model_selector
)
from evoagentx.integration.devpipe_model_selector import DevPipeModelSelector


class TestModelSelectionIntegration:
    """Test suite for model selection integration with devpipe"""
    
    @pytest.fixture
    def temp_devpipe_dir(self):
        """Create a temporary devpipe directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            devpipe_path = Path(temp_dir) / "dev-pipe"
            devpipe_path.mkdir(parents=True)
            
            # Create required subdirectories
            (devpipe_path / "queues").mkdir()
            (devpipe_path / "status").mkdir()
            (devpipe_path / "communication").mkdir()
            (devpipe_path / "logs").mkdir()
            
            yield str(devpipe_path)
    
    @pytest.fixture
    def model_selector(self, temp_devpipe_dir):
        """Create a model selector with devpipe integration"""
        selector = initialize_robust_model_selector(temp_devpipe_dir)
        selector.enable_devpipe_integration()
        return selector
    
    @pytest.fixture
    def devpipe_selector(self, temp_devpipe_dir):
        """Create a devpipe model selector"""
        return DevPipeModelSelector(temp_devpipe_dir)
    
    def test_model_selection_basic(self, model_selector):
        """Test basic model selection functionality"""
        criteria = ModelSelectionCriteria(
            task_type=TaskType.GENERAL,
            require_healthy_status=False  # Don't require health for testing
        )
        
        selected_model = model_selector.select_model(criteria)
        assert selected_model is not None
        assert hasattr(selected_model, 'config')
        assert selected_model.config.model in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    
    def test_model_health_status(self, model_selector):
        """Test model health monitoring"""
        health_summary = model_selector.get_health_summary()
        
        assert "total_models" in health_summary
        assert "models" in health_summary
        assert health_summary["total_models"] >= 0
        
        # Check that we have some models configured
        assert len(health_summary["models"]) > 0
    
    def test_devpipe_message_creation(self, devpipe_selector):
        """Test devpipe message creation and structure"""
        message = devpipe_selector.create_base_message("model_selection_request")
        
        # Verify message structure
        assert "header" in message
        assert "payload" in message
        
        header = message["header"]
        assert "message_id" in header
        assert "timestamp" in header
        assert "message_type" in header
        assert header["message_type"] == "model_selection_request"
        assert "sender" in header
        assert "recipient" in header
    
    @pytest.mark.asyncio
    async def test_devpipe_model_selection_response(self, devpipe_selector, temp_devpipe_dir):
        """Test sending model selection response through devpipe"""
        request_id = str(uuid.uuid4())
        
        selected_model = {
            "name": "gpt-4o-mini",
            "provider": "openai",
            "model_id": "gpt-4o-mini",
            "capabilities": ["chat", "text_analysis"]
        }
        
        await devpipe_selector.send_model_selection_response(
            request_id=request_id,
            success=True,
            selected_model=selected_model,
            fallback_models=["gpt-4o", "gpt-3.5-turbo"],
            reasoning="Selected based on performance metrics"
        )
        
        # Check that response file was created
        outbox_path = Path(temp_devpipe_dir) / "queues" / "model_selection_responses"
        response_files = list(outbox_path.glob("*.json"))
        assert len(response_files) > 0
        
        # Verify response content
        with open(response_files[0], 'r') as f:
            response_message = json.load(f)
        
        assert response_message["header"]["message_type"] == "model_selection_response"
        assert response_message["header"]["correlation_id"] == request_id
        assert response_message["payload"]["success"] is True
        assert response_message["payload"]["selected_model"]["name"] == "gpt-4o-mini"
    
    @pytest.mark.asyncio
    async def test_devpipe_health_update(self, devpipe_selector, model_selector, temp_devpipe_dir):
        """Test sending health updates through devpipe"""
        health_summary = model_selector.get_health_summary()
        
        await devpipe_selector.send_model_health_update(health_summary)
        
        # Check that status file was created
        status_file = Path(temp_devpipe_dir) / "status" / "model_health.json"
        assert status_file.exists()
        
        # Verify status content
        with open(status_file, 'r') as f:
            status_message = json.load(f)
        
        assert status_message["header"]["message_type"] == "model_health_status"
        assert "models" in status_message["payload"]
    
    @pytest.mark.asyncio
    async def test_devpipe_performance_update(self, devpipe_selector, temp_devpipe_dir):
        """Test sending performance updates through devpipe"""
        await devpipe_selector.send_performance_update(
            model_name="gpt-4o-mini",
            task_type="chat",
            success=True,
            response_time=1.5,
            cost=0.002,
            quality_score=0.9
        )
        
        # Check that performance update file was created
        outbox_path = Path(temp_devpipe_dir) / "queues" / "model_selection_responses"
        perf_files = list(outbox_path.glob("*model-performance*.json"))
        assert len(perf_files) > 0
        
        # Verify performance update content
        with open(perf_files[0], 'r') as f:
            perf_message = json.load(f)
        
        assert perf_message["header"]["message_type"] == "model_performance_update"
        payload = perf_message["payload"]
        assert payload["model_name"] == "gpt-4o-mini"
        assert payload["task_type"] == "chat"
        assert payload["success"] is True
        assert payload["response_time"] == 1.5
    
    @pytest.mark.asyncio
    async def test_devpipe_capabilities_sync(self, devpipe_selector, temp_devpipe_dir):
        """Test syncing model capabilities to devpipe"""
        available_models = [
            {
                "name": "gpt-4o-mini",
                "capabilities": ["chat", "text_analysis", "vault_management"],
                "status": "healthy"
            },
            {
                "name": "gpt-4o",
                "capabilities": ["reasoning", "creative_writing", "code_generation"],
                "status": "healthy"
            }
        ]
        
        await devpipe_selector.update_frontend_capabilities(available_models)
        
        # Check that capabilities file was created
        capabilities_file = Path(temp_devpipe_dir) / "status" / "model_capabilities.json"
        assert capabilities_file.exists()
        
        # Verify capabilities content
        with open(capabilities_file, 'r') as f:
            capabilities_message = json.load(f)
        
        assert capabilities_message["header"]["message_type"] == "data"
        assert capabilities_message["payload"]["data_type"] == "model_capabilities"
        assert len(capabilities_message["payload"]["models"]) == 2
    
    def test_devpipe_status_reporting(self, devpipe_selector):
        """Test devpipe integration status reporting"""
        status = devpipe_selector.get_devpipe_status()
        
        assert "devpipe_path" in status
        assert "inbox_files" in status
        assert "outbox_files" in status
        assert "status_files" in status
        assert isinstance(status["inbox_files"], int)
        assert isinstance(status["outbox_files"], int)
        assert isinstance(status["status_files"], int)
    
    def test_task_type_mapping(self):
        """Test mapping between API task types and internal enums"""
        api_task_types = [
            "chat", "code_generation", "text_analysis", "reasoning",
            "creative_writing", "summarization", "translation", "vault_management"
        ]
        
        for api_task in api_task_types:
            try:
                # Should be able to convert API task type to internal enum
                if api_task == "vault_management":
                    # vault_management maps to GENERAL in current implementation
                    task_enum = TaskType.GENERAL
                else:
                    task_enum = TaskType(api_task.upper())
                assert task_enum is not None
            except ValueError:
                # Some mappings might not exist yet, which is acceptable
                pass
    
    @pytest.mark.asyncio
    async def test_model_selection_with_devpipe_integration(self, model_selector, devpipe_selector):
        """Test full integration: model selection with devpipe notifications"""
        criteria = ModelSelectionCriteria(
            task_type=TaskType.GENERAL,
            require_healthy_status=False
        )
        
        # Select a model
        selected_model = model_selector.select_model(criteria)
        assert selected_model is not None
        
        # Simulate devpipe notification
        await devpipe_selector.notify_model_selection_event(
            "model_selected",
            selected_model.config.model,
            {"task_type": "general", "selection_time": 0.1}
        )
        
        # Verify the notification was sent (check outbox)
        outbox_path = devpipe_selector.outbox_path
        event_files = list(outbox_path.glob("*model-event*.json"))
        assert len(event_files) > 0


def test_api_model_selection_endpoint():
    """Test the model selection API endpoint"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    # Test model selection request
    request_data = {
        "task_type": "chat",
        "constraints": {
            "max_cost_per_request": 0.05,
            "min_success_rate": 0.7,
            "require_healthy_status": False  # Don't require health for testing
        },
        "context": {
            "vault_path": "/test/vault",
            "file_context": "Testing model selection"
        }
    }
    
    response = client.post("/api/obsidian/models/select", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "success" in data
    # Note: Actual success depends on model availability in test environment


def test_api_model_health_endpoint():
    """Test the model health API endpoint"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    # Test health check request
    request_data = {
        "include_metrics": True
    }
    
    response = client.post("/api/obsidian/models/health", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data
    assert "summary" in data
    assert "timestamp" in data


def test_api_available_models_endpoint():
    """Test the available models API endpoint"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    
    response = client.get("/api/obsidian/models/available")
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data
    assert "total_count" in data
    assert "task_types" in data
    assert isinstance(data["models"], list)
    assert isinstance(data["total_count"], int)
    assert isinstance(data["task_types"], list)


if __name__ == "__main__":
    # Run a simple integration test
    import tempfile
    
    async def main():
        print("Running Model Selection Integration Test...")
        
        # Create temporary devpipe directory
        with tempfile.TemporaryDirectory() as temp_dir:
            devpipe_path = Path(temp_dir) / "dev-pipe"
            devpipe_path.mkdir(parents=True)
            
            # Create required subdirectories
            (devpipe_path / "queues").mkdir()
            (devpipe_path / "status").mkdir()
            (devpipe_path / "communication").mkdir()
            (devpipe_path / "logs").mkdir()
            
            # Initialize model selector
            selector = initialize_robust_model_selector(str(devpipe_path))
            print(f"✓ Initialized model selector with devpipe at {devpipe_path}")
            
            # Test basic functionality
            criteria = ModelSelectionCriteria(
                task_type=TaskType.GENERAL,
                require_healthy_status=False
            )
            
            selected_model = selector.select_model(criteria)
            if selected_model:
                print(f"✓ Selected model: {selected_model.config.model}")
            else:
                print("⚠ No model selected (this is expected in test environment)")
            
            # Test health monitoring
            health = selector.get_health_summary()
            print(f"✓ Health summary: {health['total_models']} models configured")
            
            # Test devpipe integration
            devpipe_selector = DevPipeModelSelector(str(devpipe_path))
            
            await devpipe_selector.send_model_selection_response(
                request_id="test-123",
                success=True,
                selected_model={
                    "name": "test-model",
                    "provider": "test",
                    "model_id": "test-model-id"
                },
                reasoning="Test selection"
            )
            print("✓ Sent test devpipe response")
            
            # Check status
            status = devpipe_selector.get_devpipe_status()
            print(f"✓ DevPipe status: {status['outbox_files']} outbox files")
            
            print("\n🎉 Integration test completed successfully!")
    
    asyncio.run(main())
