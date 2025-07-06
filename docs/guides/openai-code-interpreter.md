# OpenAI Code Interpreter Developer Guide

## Overview

EvoAgentX now includes comprehensive OpenAI Code Interpreter integration with intelligent interpreter selection, providing developers with flexible, cloud-based code execution capabilities alongside existing local interpreters.

## Quick Start

### 1. Basic Usage

```python
from evoagentx.tools.openai_code_interpreter import OpenAICodeInterpreter

# Simple execution
interpreter = OpenAICodeInterpreter()
result = interpreter.execute("""
import pandas as pd
data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
print(data.describe())
""")
print(result)
```

### 2. Smart Execution (Recommended)

```python
from evoagentx.tools.intelligent_interpreter_selector import execute_smart

# Automatically selects best interpreter
result = execute_smart(
    code="import matplotlib.pyplot as plt; plt.plot([1,2,3]); plt.show()",
    security_level="medium",
    budget_limit=0.05  # 5 cents max
)

print(f"Used: {result['interpreter_used']}")
print(f"Cost: ${result['estimated_cost']:.4f}")
print(result['output'])
```

### 3. File Processing

```python
# Execute with file uploads
result = interpreter.execute_with_files(
    code="""
import pandas as pd
df = pd.read_csv('data.csv')
df.plot()
plt.savefig('analysis.png')
""",
    files=['data.csv']
)
```

## CLI Usage

### Smart Execution
```bash
# Automatic interpreter selection
evoagentx run-smart -c "print('Hello')" --security medium

# With visualization needs
evoagentx run-smart -c "import matplotlib.pyplot as plt; plt.plot([1,2,3])" --viz

# With budget limit
evoagentx run-smart -c "complex_analysis()" --budget 0.10
```

### OpenAI Code Interpreter
```bash
# Simple execution
evoagentx run-openai -c "import numpy as np; print(np.pi)"

# With file uploads
evoagentx run-openai -c "analyze_data()" --files data.csv analysis.py

# Custom model
evoagentx run-openai -c "code" --model gpt-4-1106-preview
```

## API Endpoints

### Smart Execution
```bash
POST /execute/smart
```

```json
{
  "code": "print('test')",
  "interpreter": "auto",
  "security_level": "medium",
  "budget_limit": 0.05,
  "visualization_needed": false,
  "performance_priority": false
}
```

### OpenAI Code Interpreter
```bash
POST /execute/openai
```

```json
{
  "code": "import pandas as pd; print(pd.__version__)",
  "language": "python",
  "files": ["data.csv"],
  "model": "gpt-4-1106-preview"
}
```

## Intelligent Selection Logic

The system automatically chooses interpreters based on:

### Factors Considered:
- **Security Requirements**: High security → Docker, Low security → Python/OpenAI
- **Visualization Needs**: Charts/plots → OpenAI preferred
- **File Processing**: Multiple files → OpenAI preferred  
- **Budget Constraints**: Cost limits → Local interpreters preferred
- **Performance Priority**: Speed critical → Local interpreters
- **Code Complexity**: Complex analysis → OpenAI/Docker

### Decision Matrix:

| Use Case | Recommended Interpreter | Reason |
|----------|------------------------|---------|
| Simple calculations | PythonInterpreter | Fast, no overhead |
| Data visualization | OpenAICodeInterpreter | Built-in libraries, automatic display |
| File processing | OpenAICodeInterpreter | Upload/download handling |
| Security-critical | DockerInterpreter | Isolated environment |
| High-performance | PythonInterpreter | No network latency |
| Complex analysis | OpenAICodeInterpreter | Full library ecosystem |

## Configuration

### Environment Variables
```bash
export OPENAI_API_KEY="your-api-key"
export EVOAGENTX_DEFAULT_INTERPRETER="auto"  # auto, python, docker, openai
export EVOAGENTX_OPENAI_MODEL="gpt-4-1106-preview"
export EVOAGENTX_BUDGET_LIMIT="0.10"  # Default budget limit (USD)
```

### Programmatic Configuration
```python
from evoagentx.tools.intelligent_interpreter_selector import ExecutionContext

context = ExecutionContext(
    security_level="high",
    budget_limit=0.05,
    files_required=["data.csv"],
    visualization_needed=True,
    performance_priority=False
)
```

## Advanced Usage

### Custom Interpreter Selection
```python
from evoagentx.tools.intelligent_interpreter_selector import IntelligentInterpreterSelector

selector = IntelligentInterpreterSelector()

# Analyze code before execution
analysis = selector.analyze_code(code)
print(f"Complexity: {analysis['complexity_score']}")
print(f"Security risk: {analysis['security_risk_score']}")

# Manual selection
interpreter_type = selector.select_interpreter(code, context)
interpreter = selector.create_interpreter(interpreter_type)
```

### Cost Estimation
```python
# Estimate costs before execution
estimated_cost = selector.estimate_openai_cost(code)
if estimated_cost > budget_limit:
    print("Code too expensive for OpenAI, using local interpreter")
```

### Comparative Execution
```python
# Run same code on multiple interpreters for comparison
interpreters = ['python', 'docker', 'openai']
results = {}

for interp_type in interpreters:
    try:
        interpreter = selector.create_interpreter(interp_type)
        result = interpreter.execute(code)
        results[interp_type] = {
            'output': result,
            'success': True
        }
    except Exception as e:
        results[interp_type] = {
            'output': str(e),
            'success': False
        }
```

### File Workflow Management
```python
# Complex file processing workflow
class DataPipeline:
    def __init__(self):
        self.interpreter = OpenAICodeInterpreter()
    
    def process_files(self, files, analysis_code):
        # Upload files
        result = self.interpreter.execute_with_files(analysis_code, files)
        
        # Download generated files
        for file_info in result.get('generated_files', []):
            if file_info['type'] == 'image':
                local_path = f"output_{file_info['file_id']}.png"
                self.interpreter.download_file(file_info['file_id'], local_path)
                print(f"Downloaded: {local_path}")
        
        return result
```

## Error Handling

### Graceful Fallbacks
```python
def robust_execute(code, max_attempts=3):
    interpreters = ['python', 'docker', 'openai']
    
    for i, interp_type in enumerate(interpreters):
        try:
            result = execute_smart(code, interpreter=interp_type)
            if result['success']:
                return result
        except Exception as e:
            if i == len(interpreters) - 1:  # Last attempt
                raise e
            continue
    
    raise RuntimeError("All interpreters failed")
```

### Timeout and Resource Management
```python
# Configure timeouts and limits
context = ExecutionContext(
    budget_limit=0.10,
    performance_priority=True
)

# Docker with resource limits
docker_interpreter = DockerInterpreter(
    limits=DockerLimits(
        memory="512m",
        cpus="0.5",
        timeout=30
    )
)
```

## Best Practices

### 1. Use Smart Execution by Default
```python
# Recommended approach
result = execute_smart(code, context=context)

# Instead of manually choosing
interpreter = OpenAICodeInterpreter()  # Manual choice
```

### 2. Set Appropriate Budgets
```python
# For experimentation
context = ExecutionContext(budget_limit=0.01)  # 1 cent

# For production analysis
context = ExecutionContext(budget_limit=0.50)  # 50 cents
```

### 3. Handle Files Efficiently
```python
# Good: Use OpenAI for file processing
if files_to_process:
    result = execute_smart(code, files=files_to_process)

# Good: Use Docker for security-critical file operations
if security_critical:
    context = ExecutionContext(security_level="high")
    result = execute_smart(code, context=context)
```

### 4. Monitor Costs
```python
# Track costs over time
total_cost = 0
for execution in executions:
    result = execute_smart(execution['code'])
    total_cost += result['estimated_cost']
    
if total_cost > daily_budget:
    print("Daily budget exceeded, switching to local interpreters")
```

## Integration with EvoAgentX Workflows

### Agent Integration
```python
from evoagentx.agents import Agent

class DataAnalysisAgent(Agent):
    def analyze_data(self, data_path):
        code = f"""
        import pandas as pd
        df = pd.read_csv('{data_path}')
        
        # Perform analysis
        summary = df.describe()
        print(summary)
        
        # Create visualization
        df.plot()
        plt.savefig('analysis.png')
        """
        
        # Use smart execution
        result = execute_smart(
            code=code,
            files=[data_path],
            visualization_needed=True
        )
        
        return result
```

### DevPipe Integration
```python
# DevPipe message format for interpreter selection
message = {
    "type": "code_execution_request",
    "payload": {
        "code": "analysis_code",
        "interpreter_preference": "auto",
        "context": {
            "security_level": "medium",
            "budget_limit": 0.05,
            "files": ["data.csv"]
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Budget Exceeded**
   ```python
   # Increase budget or use local interpreters
   context = ExecutionContext(budget_limit=0.20)
   ```

3. **Security Restrictions**
   ```python
   # Force Docker for security
   context = ExecutionContext(security_level="high")
   ```

4. **File Upload Errors**
   ```python
   # Check file exists and is readable
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"File not found: {file_path}")
   ```

### Debug Mode
```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Analyze selection decisions
selector = IntelligentInterpreterSelector()
analysis = selector.analyze_code(code)
print(f"Analysis: {analysis}")
```

## Performance Optimization

### Caching Results
```python
import functools

@functools.lru_cache(maxsize=100)
def cached_execute(code_hash, interpreter_type):
    # Cache expensive executions
    pass
```

### Batch Processing
```python
# Process multiple files efficiently
batch_code = """
files = ['file1.csv', 'file2.csv', 'file3.csv']
results = []
for file in files:
    df = pd.read_csv(file)
    result = analyze(df)
    results.append(result)
"""

result = interpreter.execute_with_files(batch_code, files)
```

This integration provides EvoAgentX with powerful, flexible code execution capabilities that automatically balance performance, cost, security, and functionality based on the specific requirements of each task.
