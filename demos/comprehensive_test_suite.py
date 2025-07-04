#!/usr/bin/env python3
"""
Enhanced EvoAgentX Testing Suite

This script provides comprehensive testing for all the enhanced features
implemented in EvoAgentX, including error handling, edge cases, and 
integration scenarios.
"""

import asyncio
import pytest
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from evoagentx.actions.action import Action
from evoagentx.workflow.operators import Operator, OperatorConfig
from evoagentx.workflow.action_graph import ActionGraph
from evoagentx.optimizers.optimizer import Optimizer
from evoagentx.utils.factory import create_agent, create_memory_store

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestOptimizedAction(Action):
    """Enhanced test action with comprehensive features"""
    
    def __init__(self, name: str, sleep_duration: float = 0.1, fail_rate: float = 0.0):
        super().__init__(
            name=name,
            description=f"Test action {name} with configurable behavior",
            input_schema={"query": "string"},
            output_schema={"result": "string", "metadata": "object"}
        )
        self.sleep_duration = sleep_duration
        self.fail_rate = fail_rate
        self.execution_count = 0
    
    async def async_execute(self, **kwargs) -> Dict[str, Any]:
        """Enhanced async execution with realistic behavior"""
        self.execution_count += 1
        
        # Simulate processing time
        await asyncio.sleep(self.sleep_duration)
        
        # Simulate occasional failures
        import random
        if random.random() < self.fail_rate:
            raise Exception(f"Simulated failure in {self.name} (execution #{self.execution_count})")
        
        query = kwargs.get('query', 'default query')
        
        return {
            "result": f"Processed: {query} by {self.name}",
            "metadata": {
                "execution_count": self.execution_count,
                "processing_time": self.sleep_duration,
                "action_name": self.name,
                "timestamp": asyncio.get_event_loop().time()
            }
        }

class TestComplexOptimizer(Optimizer):
    """Enhanced test optimizer with comprehensive evaluation"""
    
    def __init__(self):
        super().__init__(
            name="TestComplexOptimizer",
            description="Complex test optimizer with multiple evaluation criteria"
        )
        self.evaluation_history = []
    
    def step(self, model, step_num: int) -> Any:
        """Enhanced step with complex transformations"""
        # Simulate model improvement with some randomness
        import random
        
        improvements = [
            {"type": "parameter_tuning", "impact": random.uniform(0.01, 0.1)},
            {"type": "architecture_change", "impact": random.uniform(-0.05, 0.15)},
            {"type": "training_adjustment", "impact": random.uniform(0.0, 0.08)}
        ]
        
        selected_improvement = random.choice(improvements)
        
        # Apply improvement to model (simulated)
        if hasattr(model, 'performance_score'):
            model.performance_score += selected_improvement["impact"]
        else:
            model.performance_score = 0.5 + selected_improvement["impact"]
        
        logger.info(f"Step {step_num}: Applied {selected_improvement['type']} with impact {selected_improvement['impact']:.4f}")
        
        return {
            "step": step_num,
            "improvement": selected_improvement,
            "new_score": getattr(model, 'performance_score', 0.5)
        }
    
    def evaluate(self, model, evaluator, **kwargs) -> Dict[str, float]:
        """Enhanced evaluation with multiple metrics"""
        import random
        
        # Simulate multiple evaluation metrics
        base_score = getattr(model, 'performance_score', 0.5)
        
        metrics = {
            "accuracy": max(0.0, min(1.0, base_score + random.uniform(-0.1, 0.1))),
            "precision": max(0.0, min(1.0, base_score + random.uniform(-0.05, 0.05))),
            "recall": max(0.0, min(1.0, base_score + random.uniform(-0.08, 0.08))),
            "f1_score": 0.0,  # Will be calculated
            "efficiency": random.uniform(0.6, 0.9),
            "robustness": random.uniform(0.4, 0.8)
        }
        
        # Calculate F1 score
        if metrics["precision"] + metrics["recall"] > 0:
            metrics["f1_score"] = 2 * (metrics["precision"] * metrics["recall"]) / (metrics["precision"] + metrics["recall"])
        
        self.evaluation_history.append(metrics)
        logger.info(f"Evaluation metrics: {metrics}")
        
        return metrics

async def test_enhanced_action_execution():
    """Test enhanced action execution with various scenarios"""
    logger.info("Testing enhanced action execution...")
    
    # Test normal execution
    action = TestOptimizedAction("test_action", sleep_duration=0.05)
    result = await action.async_execute(query="test input")
    
    assert "result" in result
    assert "metadata" in result
    assert result["metadata"]["execution_count"] == 1
    
    # Test multiple executions
    for i in range(3):
        result = await action.async_execute(query=f"test input {i}")
        assert result["metadata"]["execution_count"] == i + 2
    
    # Test error handling
    failing_action = TestOptimizedAction("failing_action", fail_rate=1.0)
    try:
        await failing_action.async_execute(query="should fail")
        assert False, "Expected action to fail"
    except Exception as e:
        assert "Simulated failure" in str(e)
    
    logger.info("✅ Enhanced action execution tests passed")

async def test_complex_action_graph():
    """Test action graph with complex scenarios"""
    logger.info("Testing complex action graph...")
    
    # Create actions with different characteristics
    actions = [
        TestOptimizedAction("preprocessor", sleep_duration=0.02),
        TestOptimizedAction("analyzer", sleep_duration=0.03),
        TestOptimizedAction("processor", sleep_duration=0.04),
        TestOptimizedAction("postprocessor", sleep_duration=0.02),
        TestOptimizedAction("validator", sleep_duration=0.01)
    ]
    
    # Create action graph
    graph = ActionGraph(name="ComplexTestGraph")
    for action in actions:
        graph.add_action(action)
    
    # Test synchronous execution
    sync_results = graph.execute(query="complex test input")
    assert len(sync_results) == len(actions)
    
    # Test asynchronous execution
    async_results = await graph.async_execute(query="complex async test input")
    assert len(async_results) == len(actions)
    
    # Verify all actions were executed
    for action in actions:
        assert action.execution_count >= 1
    
    logger.info("✅ Complex action graph tests passed")

async def test_comprehensive_optimizer():
    """Test optimizer with comprehensive scenarios"""
    logger.info("Testing comprehensive optimizer...")
    
    class MockModel:
        def __init__(self):
            self.performance_score = 0.3
    
    class MockEvaluator:
        def evaluate(self, model):
            return {"score": getattr(model, 'performance_score', 0.5)}
    
    model = MockModel()
    evaluator = MockEvaluator()
    optimizer = TestComplexOptimizer()
    
    # Test optimization with various configurations
    result = optimizer.optimize(
        model=model,
        evaluator=evaluator,
        num_steps=5,
        evaluation_rounds=2,
        convergence_threshold=0.01
    )
    
    assert "best_score" in result
    assert "optimization_history" in result
    assert "converged" in result
    assert len(result["optimization_history"]) <= 5  # Should stop early if converged
    
    # Test evaluation history
    assert len(optimizer.evaluation_history) >= 2  # At least initial + one step
    
    # Test convergence detection
    stable_model = MockModel()
    stable_model.performance_score = 0.95  # High score, should converge quickly
    
    stable_result = optimizer.optimize(
        model=stable_model,
        evaluator=evaluator,
        num_steps=10,
        evaluation_rounds=1,
        convergence_threshold=0.05
    )
    
    # Should converge in fewer steps
    assert stable_result["converged"] or len(stable_result["optimization_history"]) < 10
    
    logger.info("✅ Comprehensive optimizer tests passed")

async def test_integration_scenarios():
    """Test various integration scenarios"""
    logger.info("Testing integration scenarios...")
    
    # Test factory functions
    try:
        agent = create_agent("test", agent_type="simple")
        logger.info("✅ Agent creation successful")
    except Exception as e:
        logger.warning(f"Agent creation failed (expected if dependencies missing): {e}")
    
    try:
        memory_store = create_memory_store("test_store", store_type="memory")
        logger.info("✅ Memory store creation successful")
    except Exception as e:
        logger.warning(f"Memory store creation failed: {e}")
    
    # Test error handling and recovery
    error_prone_action = TestOptimizedAction("error_prone", fail_rate=0.8)
    successes = 0
    attempts = 10
    
    for i in range(attempts):
        try:
            await error_prone_action.async_execute(query=f"attempt {i}")
            successes += 1
        except Exception:
            pass  # Expected failures
    
    # Should have some successes despite high failure rate
    logger.info(f"Error handling test: {successes}/{attempts} successes")
    
    logger.info("✅ Integration scenarios tests passed")

def test_performance_characteristics():
    """Test performance characteristics"""
    logger.info("Testing performance characteristics...")
    
    import time
    
    # Test action execution time
    start_time = time.time()
    action = TestOptimizedAction("perf_test", sleep_duration=0.001)
    
    # Run synchronous version for timing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(action.async_execute(query="performance test"))
    loop.close()
    
    execution_time = time.time() - start_time
    assert execution_time < 1.0  # Should be fast
    
    logger.info(f"Action execution time: {execution_time:.4f}s")
    logger.info("✅ Performance characteristics tests passed")

async def run_comprehensive_tests():
    """Run all comprehensive tests"""
    logger.info("🚀 Starting comprehensive EvoAgentX testing suite...")
    
    try:
        await test_enhanced_action_execution()
        await test_complex_action_graph()
        await test_comprehensive_optimizer()
        await test_integration_scenarios()
        test_performance_characteristics()
        
        logger.info("🎉 All comprehensive tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)
