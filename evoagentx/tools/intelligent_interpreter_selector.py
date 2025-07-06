"""
Intelligent Interpreter Selector for EvoAgentX
Automatically chooses the best code interpreter based on code analysis and context
"""

import re
import ast
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass

from .interpreter_python import PythonInterpreter
from .interpreter_docker import DockerInterpreter
from .openai_code_interpreter import OpenAICodeInterpreter


class InterpreterType(Enum):
    PYTHON = "python"
    DOCKER = "docker" 
    OPENAI = "openai"


@dataclass
class ExecutionContext:
    """Context information for interpreter selection"""
    security_level: str = "medium"  # low, medium, high
    budget_limit: Optional[float] = None  # USD limit for cloud execution
    files_required: List[str] = None
    visualization_needed: bool = False
    internet_required: bool = False
    performance_priority: bool = False
    
    def __post_init__(self):
        if self.files_required is None:
            self.files_required = []


class IntelligentInterpreterSelector:
    """
    Intelligently selects the best interpreter for code execution
    based on code analysis and execution context.
    """
    
    def __init__(self):
        self.openai_cost_per_token = 0.00003  # Rough estimate
        self.visualization_libraries = {
            'matplotlib', 'pyplot', 'seaborn', 'plotly', 'bokeh',
            'altair', 'holoviews', 'pygal', 'ggplot'
        }
        self.data_libraries = {
            'pandas', 'numpy', 'scipy', 'sklearn', 'tensorflow',
            'torch', 'transformers', 'PIL', 'cv2', 'openpyxl'
        }
        self.security_risk_patterns = [
            r'subprocess\.',
            r'os\.system',
            r'eval\(',
            r'exec\(',
            r'__import__',
            r'open\(',
            r'file\(',
            r'input\(',
        ]
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze code to determine characteristics"""
        analysis = {
            'imports': [],
            'has_visualization': False,
            'has_data_processing': False,
            'security_risk_score': 0,
            'estimated_tokens': 0,
            'uses_files': False,
            'complexity_score': 0
        }
        
        # Basic token estimation
        analysis['estimated_tokens'] = len(code.split()) * 1.3
        
        # Check for file operations
        if any(pattern in code for pattern in ['open(', 'read_csv', 'load_', 'with open']):
            analysis['uses_files'] = True
        
        # Security risk analysis
        for pattern in self.security_risk_patterns:
            if re.search(pattern, code):
                analysis['security_risk_score'] += 1
        
        # Parse imports and analyze libraries
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis['imports'].append(node.module)
        except:
            # If parsing fails, use regex fallback
            import_matches = re.findall(r'import\s+(\w+)', code)
            from_matches = re.findall(r'from\s+(\w+)', code)
            analysis['imports'].extend(import_matches + from_matches)
        
        # Check for visualization
        if any(lib in analysis['imports'] for lib in self.visualization_libraries):
            analysis['has_visualization'] = True
        
        # Check for data processing
        if any(lib in analysis['imports'] for lib in self.data_libraries):
            analysis['has_data_processing'] = True
        
        # Complexity score (simple heuristic)
        analysis['complexity_score'] = (
            len(analysis['imports']) * 2 +
            code.count('def ') * 3 +
            code.count('class ') * 5 +
            code.count('for ') +
            code.count('while ') +
            code.count('if ')
        )
        
        return analysis
    
    def estimate_openai_cost(self, code: str) -> float:
        """Estimate cost for OpenAI Code Interpreter execution"""
        analysis = self.analyze_code(code)
        estimated_tokens = analysis['estimated_tokens']
        
        # Add overhead for assistant setup and response
        total_tokens = estimated_tokens + 500
        
        return total_tokens * self.openai_cost_per_token
    
    def select_interpreter(
        self, 
        code: str, 
        context: ExecutionContext = None,
        **kwargs
    ) -> InterpreterType:
        """
        Select the best interpreter for the given code and context.
        
        Args:
            code: The code to analyze
            context: Execution context with preferences and constraints
            **kwargs: Additional parameters for interpreter initialization
            
        Returns:
            InterpreterType: The recommended interpreter type
        """
        if context is None:
            context = ExecutionContext()
        
        analysis = self.analyze_code(code)
        
        # Decision logic based on multiple factors
        score_python = 0
        score_docker = 0
        score_openai = 0
        
        # Security considerations
        if context.security_level == "high" or analysis['security_risk_score'] > 2:
            score_docker += 30
            score_python -= 20
        elif context.security_level == "low":
            score_python += 10
            score_openai += 5
        
        # Budget considerations
        if context.budget_limit is not None:
            estimated_cost = self.estimate_openai_cost(code)
            if estimated_cost > context.budget_limit:
                score_openai -= 50
            else:
                score_openai += 10
        
        # File handling
        if context.files_required or analysis['uses_files']:
            score_openai += 20
            score_docker += 10
            score_python -= 10
        
        # Visualization needs
        if context.visualization_needed or analysis['has_visualization']:
            score_openai += 30
            score_docker += 10
            score_python -= 20
        
        # Data processing
        if analysis['has_data_processing']:
            score_openai += 15
            score_docker += 10
            score_python += 5
        
        # Performance priority
        if context.performance_priority:
            score_python += 20
            score_docker += 10
            score_openai -= 10
        
        # Complexity considerations
        if analysis['complexity_score'] > 20:
            score_openai += 10
            score_docker += 15
        elif analysis['complexity_score'] < 5:
            score_python += 15
        
        # Internet/external dependencies
        if context.internet_required:
            score_openai += 20
            score_docker += 10
            score_python -= 10
        
        # Make decision based on highest score
        scores = {
            InterpreterType.PYTHON: score_python,
            InterpreterType.DOCKER: score_docker,
            InterpreterType.OPENAI: score_openai
        }
        
        return max(scores, key=scores.get)
    
    def create_interpreter(
        self,
        interpreter_type: InterpreterType,
        **kwargs
    ):
        """Create an interpreter instance of the specified type"""
        if interpreter_type == InterpreterType.PYTHON:
            return PythonInterpreter(**kwargs)
        elif interpreter_type == InterpreterType.DOCKER:
            return DockerInterpreter(**kwargs)
        elif interpreter_type == InterpreterType.OPENAI:
            return OpenAICodeInterpreter(**kwargs)
        else:
            raise ValueError(f"Unknown interpreter type: {interpreter_type}")
    
    def execute_with_best_interpreter(
        self,
        code: str,
        language: str = "python",
        context: ExecutionContext = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute code using the best interpreter for the task.
        
        Returns:
            Dict containing execution result and metadata
        """
        selected_type = self.select_interpreter(code, context, **kwargs)
        interpreter = self.create_interpreter(selected_type, **kwargs)
        
        try:
            if selected_type == InterpreterType.OPENAI and context and context.files_required:
                # Use file-aware execution for OpenAI
                result = interpreter.execute_with_files(code, context.files_required, language)
                output = result.get('output', str(result))
            else:
                # Standard execution
                output = interpreter.execute(code, language)
            
            return {
                'output': output,
                'interpreter_used': selected_type.value,
                'analysis': self.analyze_code(code),
                'estimated_cost': self.estimate_openai_cost(code) if selected_type == InterpreterType.OPENAI else 0,
                'success': True
            }
            
        except Exception as e:
            return {
                'output': f"Error: {str(e)}",
                'interpreter_used': selected_type.value,
                'analysis': self.analyze_code(code),
                'estimated_cost': 0,
                'success': False,
                'error': str(e)
            }
        finally:
            # Cleanup if needed
            if hasattr(interpreter, 'cleanup'):
                interpreter.cleanup()


# Convenience function for simple usage
def execute_smart(
    code: str,
    language: str = "python",
    security_level: str = "medium",
    budget_limit: Optional[float] = None,
    files: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute code using intelligent interpreter selection.
    
    Args:
        code: Code to execute
        language: Programming language
        security_level: Security requirement level
        budget_limit: Maximum cost for cloud execution
        files: Files to include in execution
        **kwargs: Additional interpreter parameters
        
    Returns:
        Execution result with metadata
    """
    context = ExecutionContext(
        security_level=security_level,
        budget_limit=budget_limit,
        files_required=files or [],
        visualization_needed='plt.' in code or 'plot(' in code or 'show()' in code,
        internet_required='requests.' in code or 'urllib' in code
    )
    
    selector = IntelligentInterpreterSelector()
    return selector.execute_with_best_interpreter(code, language, context, **kwargs)
