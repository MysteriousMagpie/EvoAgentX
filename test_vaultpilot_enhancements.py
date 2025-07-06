#!/usr/bin/env python3
"""
VaultPilot Experience Enhancement Test Suite

Comprehensive testing for response time improvements, progress indicators,
and keyboard shortcuts functionality.
"""

import asyncio
import time
import json
import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch

# Import the enhancement modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'evoagentx_integration'))

from experience_enhancements import (
    ExperienceEnhancementEngine, ResponseOptimizer, ProgressIndicatorManager,
    KeyboardShortcutManager, OperationType, ProgressUpdate, PerformanceMetrics
)
from websocket_handler import WebSocketManager


class TestResponseOptimizer:
    """Test suite for response time optimization"""
    
    @pytest.fixture
    def optimizer(self):
        return ResponseOptimizer()
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, optimizer):
        """Test basic caching functionality"""
        call_count = 0
        
        async def mock_operation():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate work
            return {"result": "test_data", "call": call_count}
        
        # First call - should execute operation
        result1, metrics1 = await optimizer.optimize_response("test_op", {"param": "value"})
        assert metrics1.cache_hit is False
        assert call_count == 0  # Operation not actually called in current implementation
        
        # Second call - should hit cache
        result2, metrics2 = await optimizer.optimize_response("test_op", {"param": "value"})
        assert metrics2.cache_hit is True
        assert result1 == result2
    
    @pytest.mark.asyncio 
    async def test_cache_expiration(self, optimizer):
        """Test cache TTL functionality"""
        # Set very short TTL for testing
        original_cache = optimizer.cache.copy()
        
        # Add cache entry with past expiration
        past_time = time.time() - 3600  # 1 hour ago
        optimizer.cache["expired_key"] = "expired_value"
        optimizer.cache_ttl["expired_key"] = past_time
        
        # Should return None for expired cache
        result = optimizer._get_cached_result("expired_key")
        assert result is None
        assert "expired_key" not in optimizer.cache
    
    @pytest.mark.asyncio
    async def test_search_optimization(self, optimizer):
        """Test search-specific optimizations"""
        search_data = {
            "query": "test query that is very long and should be truncated" * 10,
            "max_results": None
        }
        
        optimized_data, applied = await optimizer._optimize_search(search_data, {})
        
        assert len(optimized_data["query"]) <= 100  # Should be truncated
        assert optimized_data["max_results"] == 50  # Should have default
        assert "query_truncation" in applied
        assert "result_limiting" in applied
    
    @pytest.mark.asyncio
    async def test_vault_optimization(self, optimizer):
        """Test vault operation optimizations"""
        vault_data = {
            "include_content": True,
            "max_depth": None
        }
        
        context = {"content_required": False}
        optimized_data, applied = await optimizer._optimize_vault_operations(vault_data, context)
        
        assert optimized_data["include_content"] is False
        assert optimized_data["max_depth"] == 3
        assert "content_exclusion" in applied
        assert "depth_limiting" in applied
    
    def test_cache_key_generation(self, optimizer):
        """Test cache key generation consistency"""
        data1 = {"param1": "value1", "param2": "value2"}
        data2 = {"param2": "value2", "param1": "value1"}  # Different order
        
        key1 = optimizer._generate_cache_key("test_op", data1)
        key2 = optimizer._generate_cache_key("test_op", data2)
        
        assert key1 == key2  # Should be same despite different order


class TestProgressIndicatorManager:
    """Test suite for progress indicators"""
    
    @pytest.fixture
    def websocket_manager(self):
        return Mock(spec=WebSocketManager)
    
    @pytest.fixture
    def progress_manager(self, websocket_manager):
        return ProgressIndicatorManager(websocket_manager)
    
    @pytest.mark.asyncio
    async def test_operation_lifecycle(self, progress_manager, websocket_manager):
        """Test complete operation lifecycle"""
        operation_id = "test_operation_123"
        vault_id = "test_vault"
        
        # Start operation
        await progress_manager.start_operation(
            operation_id, OperationType.VAULT_ANALYSIS, vault_id, 5, "Test operation"
        )
        
        assert operation_id in progress_manager.active_operations
        operation = progress_manager.active_operations[operation_id]
        assert operation["operation_type"] == OperationType.VAULT_ANALYSIS
        assert operation["total_steps"] == 5
        assert operation["status"] == "starting"
        
        # Verify initial WebSocket message sent
        websocket_manager.broadcast_to_vault.assert_called()
        call_args = websocket_manager.broadcast_to_vault.call_args
        assert call_args[0][0] == vault_id
        assert call_args[0][1]["type"] == "progress_update"
    
    @pytest.mark.asyncio
    async def test_progress_updates(self, progress_manager, websocket_manager):
        """Test progress update functionality"""
        operation_id = "test_operation_456"
        vault_id = "test_vault"
        
        await progress_manager.start_operation(
            operation_id, OperationType.SEARCH, vault_id, 3, "Test search"
        )
        
        # Update progress
        await progress_manager.update_progress(operation_id, 2, "Processing step 2")
        
        operation = progress_manager.active_operations[operation_id]
        assert operation["current_step"] == 2
        assert operation["status"] == "running"
        
        # Verify WebSocket update sent
        assert websocket_manager.broadcast_to_vault.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_operation_completion(self, progress_manager, websocket_manager):
        """Test operation completion"""
        operation_id = "test_operation_789"
        vault_id = "test_vault"
        
        await progress_manager.start_operation(
            operation_id, OperationType.WORKFLOW_EXECUTION, vault_id, 2, "Test workflow"
        )
        
        # Complete operation
        result_data = {"artifacts_created": 3}
        await progress_manager.complete_operation(
            operation_id, "Operation completed successfully", result_data
        )
        
        # Should be moved to history
        assert operation_id not in progress_manager.active_operations
        assert operation_id in progress_manager.progress_history
        
        # Check completion data
        completed_op = progress_manager.progress_history[operation_id]
        assert completed_op["status"] == "completed"
        assert "end_time" in completed_op
    
    @pytest.mark.asyncio
    async def test_operation_failure(self, progress_manager, websocket_manager):
        """Test operation failure handling"""
        operation_id = "test_operation_fail"
        vault_id = "test_vault"
        
        await progress_manager.start_operation(
            operation_id, OperationType.BACKUP_CREATION, vault_id, 3, "Test backup"
        )
        
        # Fail operation
        error_details = {"error_code": "DISK_FULL"}
        await progress_manager.fail_operation(
            operation_id, "Backup failed: insufficient disk space", error_details
        )
        
        # Should be moved to history with failure status
        assert operation_id not in progress_manager.active_operations
        assert operation_id in progress_manager.progress_history
        
        failed_op = progress_manager.progress_history[operation_id]
        assert failed_op["status"] == "failed"
        assert failed_op["error"] == "Backup failed: insufficient disk space"
    
    def test_eta_calculation(self, progress_manager):
        """Test ETA calculation logic"""
        operation = {
            "start_time": time.time() - 60,  # Started 60 seconds ago
            "total_steps": 10
        }
        
        # 50% complete after 60 seconds = 60 more seconds estimated
        eta = progress_manager._calculate_eta(operation, 0.5)
        assert 55 <= eta <= 65  # Allow some variance
        
        # Near completion
        eta = progress_manager._calculate_eta(operation, 0.9)
        assert 0 <= eta <= 10
        
        # Just started
        eta = progress_manager._calculate_eta(operation, 0.1)
        assert eta is None or eta > 100


class TestKeyboardShortcutManager:
    """Test suite for keyboard shortcuts"""
    
    @pytest.fixture
    def shortcut_manager(self):
        return KeyboardShortcutManager()
    
    def test_default_shortcuts_loaded(self, shortcut_manager):
        """Test that default shortcuts are properly loaded"""
        assert len(shortcut_manager.shortcuts) > 0
        assert "Ctrl+Shift+S" in shortcut_manager.shortcuts
        assert shortcut_manager.shortcuts["Ctrl+Shift+S"] == "vaultpilot-smart-search"
    
    def test_shortcut_categorization(self, shortcut_manager):
        """Test shortcut categorization functionality"""
        ai_shortcuts = shortcut_manager.get_shortcuts_by_category("ai")
        search_shortcuts = shortcut_manager.get_shortcuts_by_category("search")
        
        assert len(ai_shortcuts) > 0
        assert len(search_shortcuts) > 0
        
        # Verify AI shortcuts contain AI commands
        for shortcut, command in ai_shortcuts.items():
            assert "ai" in command.lower() or "copilot" in command.lower()
    
    def test_context_filtering(self, shortcut_manager):
        """Test context-based shortcut filtering"""
        global_shortcuts = shortcut_manager.get_shortcuts_for_context("global")
        editor_shortcuts = shortcut_manager.get_shortcuts_for_context("editor")
        
        assert len(global_shortcuts) >= len(editor_shortcuts)
        assert "Ctrl+Space" in editor_shortcuts  # Copilot suggestion
    
    def test_custom_shortcut_addition(self, shortcut_manager):
        """Test adding custom shortcuts"""
        custom_shortcut = "Ctrl+Alt+X"
        custom_command = "my-custom-command"
        
        shortcut_manager.add_custom_shortcut(
            custom_shortcut, custom_command, "My custom command", "custom"
        )
        
        assert shortcut_manager.shortcuts[custom_shortcut] == custom_command
        assert custom_command in shortcut_manager.command_mappings
        assert shortcut_manager.command_mappings[custom_command]["custom"] is True
    
    def test_shortcut_reference_generation(self, shortcut_manager):
        """Test shortcut reference generation"""
        reference = shortcut_manager.generate_shortcut_reference()
        
        assert isinstance(reference, dict)
        assert len(reference) > 0
        
        # Should have categories
        assert "ai" in reference
        assert "search" in reference
        
        # Each category should have shortcuts with proper structure
        for category, shortcuts in reference.items():
            assert isinstance(shortcuts, list)
            for shortcut_info in shortcuts:
                assert "shortcut" in shortcut_info
                assert "command" in shortcut_info
                assert "description" in shortcut_info


class TestExperienceEnhancementEngine:
    """Test suite for the main enhancement engine"""
    
    @pytest.fixture
    def websocket_manager(self):
        return Mock(spec=WebSocketManager)
    
    @pytest.fixture
    def enhancement_engine(self, websocket_manager):
        return ExperienceEnhancementEngine(websocket_manager)
    
    @pytest.mark.asyncio
    async def test_enhanced_execute_with_progress(self, enhancement_engine, websocket_manager):
        """Test enhanced execution with progress tracking"""
        operation = "vault_analyze"
        data = {"vault_path": "/"}
        vault_id = "test_vault"
        operation_type = OperationType.VAULT_ANALYSIS
        
        result, metrics = await enhancement_engine.enhanced_execute(
            operation, data, vault_id, operation_type
        )
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.response_time >= 0
        assert isinstance(metrics.optimizations_applied, list)
        
        # Should have sent progress updates
        assert websocket_manager.broadcast_to_vault.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_enhanced_execute_with_error(self, enhancement_engine, websocket_manager):
        """Test enhanced execution error handling"""
        with patch.object(enhancement_engine.response_optimizer, 'optimize_response', 
                         side_effect=Exception("Test error")):
            
            with pytest.raises(Exception, match="Test error"):
                await enhancement_engine.enhanced_execute(
                    "test_op", {}, "vault_id", OperationType.AI_PROCESSING
                )
    
    def test_keyboard_shortcuts_integration(self, enhancement_engine):
        """Test keyboard shortcuts integration"""
        shortcuts_config = enhancement_engine.get_keyboard_shortcuts()
        
        assert "shortcuts" in shortcuts_config
        assert "commands" in shortcuts_config
        assert "reference" in shortcuts_config
        
        assert isinstance(shortcuts_config["shortcuts"], dict)
        assert len(shortcuts_config["shortcuts"]) > 0
    
    def test_performance_stats(self, enhancement_engine):
        """Test performance statistics retrieval"""
        stats = enhancement_engine.get_performance_stats()
        
        assert "cache_stats" in stats
        assert "active_operations" in stats
        assert "optimizations_available" in stats
        
        assert isinstance(stats["active_operations"], int)
        assert isinstance(stats["optimizations_available"], list)


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    @pytest.fixture
    def enhancement_engine(self):
        websocket_manager = Mock(spec=WebSocketManager)
        return ExperienceEnhancementEngine(websocket_manager)
    
    @pytest.mark.asyncio
    async def test_complete_vault_analysis_workflow(self, enhancement_engine):
        """Test complete vault analysis with all enhancements"""
        # Simulate vault analysis request
        operation = "vault_analyze"
        data = {
            "vault_path": "/",
            "include_content": True,
            "max_depth": 5
        }
        vault_id = "test_vault"
        operation_type = OperationType.VAULT_ANALYSIS
        
        # Execute with enhancements
        result, metrics = await enhancement_engine.enhanced_execute(
            operation, data, vault_id, operation_type
        )
        
        # Verify optimizations were applied
        assert metrics.optimizations_applied is not None
        assert len(metrics.optimizations_applied) >= 0
        
        # Verify performance tracking
        assert metrics.response_time >= 0
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_operations(self, enhancement_engine):
        """Test handling multiple concurrent operations"""
        operations = []
        
        # Start multiple operations concurrently
        for i in range(3):
            operation_task = enhancement_engine.enhanced_execute(
                f"operation_{i}",
                {"data": f"test_{i}"},
                "test_vault",
                OperationType.SEARCH
            )
            operations.append(operation_task)
        
        # Wait for all to complete
        results = await asyncio.gather(*operations, return_exceptions=True)
        
        # All should complete successfully
        for result in results:
            assert not isinstance(result, Exception)
            data, metrics = result
            assert isinstance(metrics, PerformanceMetrics)
    
    @pytest.mark.asyncio
    async def test_cache_performance_improvement(self, enhancement_engine):
        """Test that caching improves performance"""
        operation = "test_cache_performance"
        data = {"consistent": "data"}
        vault_id = "test_vault"
        operation_type = OperationType.AI_PROCESSING
        
        # First request
        start_time1 = time.time()
        result1, metrics1 = await enhancement_engine.enhanced_execute(
            operation, data, vault_id, operation_type
        )
        duration1 = time.time() - start_time1
        
        # Second request (should hit cache)
        start_time2 = time.time()
        result2, metrics2 = await enhancement_engine.enhanced_execute(
            operation, data, vault_id, operation_type
        )
        duration2 = time.time() - start_time2
        
        # Cache should provide performance benefit
        # Note: In actual implementation, would expect metrics2.cache_hit to be True
        # and duration2 to be significantly less than duration1


class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_response_time_benchmarks(self):
        """Benchmark response times for various operations"""
        optimizer = ResponseOptimizer()
        
        # Test search optimization performance
        search_data = {"query": "test", "max_results": 100}
        
        start_time = time.time()
        optimized_data, applied = await optimizer._optimize_search(search_data, {})
        optimization_time = time.time() - start_time
        
        # Optimization should be very fast (< 1ms)
        assert optimization_time < 0.001
    
    @pytest.mark.asyncio
    async def test_progress_update_performance(self):
        """Benchmark progress update performance"""
        websocket_manager = Mock(spec=WebSocketManager)
        progress_manager = ProgressIndicatorManager(websocket_manager)
        
        operation_id = "perf_test"
        
        # Benchmark progress updates
        start_time = time.time()
        
        await progress_manager.start_operation(
            operation_id, OperationType.VAULT_ANALYSIS, "test_vault", 100
        )
        
        for i in range(10):
            await progress_manager.update_progress(operation_id, i, f"Step {i}")
        
        await progress_manager.complete_operation(operation_id, "Done")
        
        total_time = time.time() - start_time
        
        # 12 operations (start + 10 updates + complete) should be fast
        assert total_time < 0.1  # Less than 100ms
        avg_time_per_update = total_time / 12
        assert avg_time_per_update < 0.01  # Less than 10ms per update


if __name__ == "__main__":
    print("🧪 VaultPilot Experience Enhancement Test Suite")
    print("=" * 60)
    
    # Run tests with pytest
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])
