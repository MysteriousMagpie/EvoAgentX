from typing import Union, Optional
from pydantic import Field 

from ..core.module import BaseModule
from ..models.base_model import BaseLLM
from ..benchmark.benchmark import Benchmark
from ..evaluators.evaluator import Evaluator
from ..workflow.action_graph import ActionGraph 
from ..workflow.workflow_graph import WorkFlowGraph


class Optimizer(BaseModule):
    
    graph: Union[WorkFlowGraph, ActionGraph] = Field(description="The workflow to optimize.")
    evaluator: Evaluator = Field(description="The evaluator to use for optimization.")

    llm: Optional[BaseLLM] = Field(default=None, description="The LLM to use for optimization and evaluation.")
    max_steps: int = Field(default=5, description="The maximum number of optimization steps to take.")
    eval_every_n_steps: int = Field(default=1, description="Evaluate the workflow every `eval_every_n_steps` steps.")
    eval_rounds: int = Field(default=1, description="Run evaluation for `eval_rounds` times and compute the average score.")
    convergence_threshold: int = Field(default=5, description="If the optimization has not improved the score for `convergence_threshold` steps, the optimization will be stopped.")

    def optimize(self, dataset: Benchmark, **kwargs):
        """
        Optimize the workflow using iterative improvement.
        
        Args:
            dataset: The benchmark dataset to use for optimization
            **kwargs: Additional optimization parameters
            
        Returns:
            dict: Optimization results including final score and history
        """
        from ..core.logging import logger
        
        logger.info(f"Starting optimization with {type(self).__name__}")
        
        best_score = 0.0
        best_graph = None
        optimization_history = []
        steps_without_improvement = 0
        
        # Initial evaluation
        initial_score = self.evaluate(dataset, eval_mode="test")
        current_score = initial_score.get("score", 0.0) if isinstance(initial_score, dict) else initial_score
        best_score = current_score
        best_graph = self.graph
        
        logger.info(f"Initial score: {current_score}")
        optimization_history.append({"step": 0, "score": current_score, "type": "initial"})
        
        total_steps = 0
        for step in range(1, self.max_steps + 1):
            total_steps = step
            logger.info(f"Optimization step {step}/{self.max_steps}")
            
            # Take optimization step
            try:
                step_result = self.step(dataset=dataset, step=step, **kwargs)
                
                # Evaluate if needed
                if step % self.eval_every_n_steps == 0:
                    evaluation_results = []
                    for round_idx in range(self.eval_rounds):
                        eval_result = self.evaluate(dataset, eval_mode="test")
                        eval_score = eval_result.get("score", 0.0) if isinstance(eval_result, dict) else eval_result
                        evaluation_results.append(eval_score)
                    
                    # Average score across evaluation rounds
                    avg_score = sum(evaluation_results) / len(evaluation_results)
                    
                    logger.info(f"Step {step} average score: {avg_score} (over {self.eval_rounds} rounds)")
                    optimization_history.append({"step": step, "score": avg_score, "type": "evaluation"})
                    
                    # Check for improvement
                    if avg_score > best_score:
                        best_score = avg_score
                        best_graph = self.graph
                        steps_without_improvement = 0
                        logger.info(f"New best score: {best_score}")
                    else:
                        steps_without_improvement += 1
                        
                    # Check convergence
                    if self.convergence_check(steps_without_improvement, **kwargs):
                        logger.info(f"Convergence reached after {step} steps")
                        break
                        
            except Exception as e:
                logger.error(f"Error in optimization step {step}: {e}")
                optimization_history.append({"step": step, "error": str(e), "type": "error"})
                continue
        
        # Restore best graph
        if best_graph is not None:
            self.graph = best_graph
            
        return {
            "best_score": best_score,
            "final_score": current_score,
            "optimization_history": optimization_history,
            "total_steps": total_steps,
            "converged": steps_without_improvement >= self.convergence_threshold
        }

    def step(self, **kwargs):
        """
        Take a single optimization step.
        
        This is a basic implementation that subclasses should override.
        
        Args:
            **kwargs: Step-specific parameters
            
        Returns:
            dict: Step results
        """
        from ..core.logging import logger
        
        step_num = kwargs.get("step", 0)
        logger.info(f"Taking optimization step {step_num}")
        
        # Basic implementation - subclasses should override this
        # This just logs the step and returns
        return {"step": step_num, "message": "Basic step implementation"}
    
    def evaluate(self, dataset: Benchmark, eval_mode: str = "test", graph: Optional[Union[WorkFlowGraph, ActionGraph]] = None, **kwargs) -> dict:
        """
        Evaluate the workflow on the given dataset.
        
        Args:
            dataset: The benchmark dataset to evaluate on
            eval_mode: Evaluation mode ("test", "val", etc.)
            graph: Optional graph to evaluate (uses self.graph if None)
            **kwargs: Additional evaluation parameters
            
        Returns:
            dict: Evaluation results including score and metrics
        """
        from ..core.logging import logger
        
        evaluation_graph = graph or self.graph
        if evaluation_graph is None:
            raise ValueError("No graph available for evaluation")
            
        logger.info(f"Evaluating graph with {type(self.evaluator).__name__}")
        
        try:
            # Use the evaluator to run evaluation
            results = self.evaluator.evaluate(
                graph=evaluation_graph,
                dataset=dataset,
                eval_mode=eval_mode,
                **kwargs
            )
            
            if isinstance(results, dict):
                return results
            else:
                # Convert single score to dict format
                return {"score": results, "eval_mode": eval_mode}
                
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            return {"score": 0.0, "error": str(e), "eval_mode": eval_mode}
    
    def convergence_check(self, steps_without_improvement: int, **kwargs) -> bool:
        """
        Check if the optimization has converged.
        
        Args:
            steps_without_improvement: Number of steps without score improvement
            **kwargs: Additional convergence parameters
            
        Returns:
            bool: True if optimization should stop
        """
        return steps_without_improvement >= self.convergence_threshold