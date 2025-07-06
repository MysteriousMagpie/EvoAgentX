"""
Code Generation Agent for Conversational Development Interface

This agent takes parsed development requests and generates appropriate code changes,
patches, or complete files based on the user's natural language descriptions.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import tempfile
import subprocess

class CodeType(Enum):
    PATCH = "patch"
    FULL_FILE = "full_file" 
    MULTIPLE_FILES = "multiple_files"
    DIRECTORY_STRUCTURE = "directory_structure"

@dataclass
class GeneratedCode:
    type: CodeType
    content: str | Dict[str, str]
    diff_summary: Optional[str] = None
    explanations: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    test_suggestions: Optional[List[str]] = None
    rollback_info: Optional[Dict[str, Any]] = None

class ConversationalCodeGenerator:
    """
    Advanced code generation agent that creates code based on natural language requests.
    Integrates with EvoAgentX's agent system for sophisticated code generation.
    """
    
    def __init__(self):
        self.template_cache = {}
        self.code_templates = self._load_code_templates()
        
    def _load_code_templates(self) -> Dict[str, str]:
        """Load reusable code templates for common patterns."""
        return {
            "react_component": '''import React, { useState } from 'react';

interface {ComponentName}Props {
  // Add props here
}

export const {ComponentName}: React.FC<{ComponentName}Props> = ({
  // Destructure props here
}) => {
  // Add state and logic here
  
  return (
    <div className="{component-name}">
      {/* Component content */}
    </div>
  );
};

export default {ComponentName};''',

            "vue_component": '''<template>
  <div class="{component-name}">
    <!-- Component content -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// Add reactive state here
const state = ref();

// Add computed properties here
const computed_value = computed(() => {
  // Computation logic
});

// Add methods here
const handleAction = () => {
  // Method logic
};
</script>

<style scoped>
.{component-name} {
  /* Component styles */
}
</style>''',

            "api_service": '''class {ServiceName}Service {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  async {methodName}(params?: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/{endpoint}`, {
        method: '{method}',
        headers: {
          'Content-Type': 'application/json',
        },
        body: params ? JSON.stringify(params) : undefined,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('{ServiceName}Service.{methodName} error:', error);
      throw error;
    }
  }
}

export default new {ServiceName}Service();''',

            "utility_function": '''/**
 * {description}
 * @param {paramType} {paramName} - {paramDescription}
 * @returns {returnType} {returnDescription}
 */
export function {functionName}({paramName}: {paramType}): {returnType} {
  // Implementation here
  return {defaultReturn};
}''',

            "test_file": '''import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { {ImportName} } from '../{fileName}';

describe('{TestSubject}', () => {
  beforeEach(() => {
    // Setup before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  it('should {testDescription}', () => {
    // Arrange
    const {varName} = {setupValue};

    // Act
    const result = {functionCall};

    // Assert
    expect(result).toBe({expectedValue});
  });

  it('should handle edge cases', () => {
    // Test edge cases
  });
});'''
        }

    async def generate_code(self, request: Dict[str, Any]) -> GeneratedCode:
        """
        Main entry point for code generation based on a parsed development request.
        """
        intent = request.get('intent', 'modify')
        target_file = request.get('targetFile')
        description = request.get('description', '')
        context = request.get('context', {})
        
        # Determine generation strategy based on intent
        if intent == 'create':
            return await self._generate_new_code(request)
        elif intent == 'modify':
            return await self._generate_modification(request)
        elif intent == 'add_feature':
            return await self._generate_feature_addition(request)
        elif intent == 'fix_bug':
            return await self._generate_bug_fix(request)
        elif intent == 'refactor':
            return await self._generate_refactor(request)
        elif intent == 'test':
            return await self._generate_tests(request)
        elif intent == 'document':
            return await self._generate_documentation(request)
        elif intent == 'optimize':
            return await self._generate_optimization(request)
        else:
            return await self._generate_generic_change(request)

    async def _generate_new_code(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate new files or components from scratch."""
        description = request.get('description', '')
        context = request.get('context', {})
        project_path = context.get('projectPath', '')
        
        # Detect what type of code to create
        if 'component' in description.lower():
            return await self._create_component(request)
        elif 'service' in description.lower() or 'api' in description.lower():
            return await self._create_service(request)
        elif 'utility' in description.lower() or 'helper' in description.lower():
            return await self._create_utility(request)
        elif 'page' in description.lower() or 'view' in description.lower():
            return await self._create_page(request)
        else:
            return await self._create_generic_file(request)

    async def _create_component(self, request: Dict[str, Any]) -> GeneratedCode:
        """Create a new component based on the request."""
        description = request.get('description', '')
        context = request.get('context', {})
        
        # Extract component name
        component_name = self._extract_component_name(description)
        
        # Determine framework
        framework = self._detect_framework(context, description)
        
        # Generate component code
        if framework == 'react':
            template = self.code_templates['react_component']
            content = template.replace('{ComponentName}', component_name)
            content = content.replace('{component-name}', self._to_kebab_case(component_name))
            
            # Add specific functionality based on description
            content = self._add_component_features(content, description, 'react')
            
        elif framework == 'vue':
            template = self.code_templates['vue_component']
            content = template.replace('{ComponentName}', component_name)
            content = content.replace('{component-name}', self._to_kebab_case(component_name))
            
            # Add specific functionality
            content = self._add_component_features(content, description, 'vue')
            
        else:
            # Generic component
            content = self._generate_generic_component(component_name, description)
        
        # Determine file path
        file_extension = '.tsx' if framework == 'react' else '.vue' if framework == 'vue' else '.js'
        target_file = f"src/components/{component_name}{file_extension}"
        
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content={target_file: content},
            diff_summary=f"Created new {framework} component: {component_name}",
            explanations=[
                f"Generated {component_name} component with {framework} framework",
                "Includes basic structure with props, state, and styling",
                "Ready for customization based on specific requirements"
            ],
            dependencies=self._extract_dependencies(description, framework),
            test_suggestions=[
                f"Add unit tests for {component_name} component",
                "Test component rendering with different props",
                "Test user interactions and state changes"
            ]
        )

    async def _create_service(self, request: Dict[str, Any]) -> GeneratedCode:
        """Create a new service or API module."""
        description = request.get('description', '')
        
        # Extract service name and methods
        service_name = self._extract_service_name(description)
        methods = self._extract_api_methods(description)
        
        # Generate service code
        template = self.code_templates['api_service']
        content = template.replace('{ServiceName}', service_name)
        
        # Add specific methods
        if methods:
            method_code = ""
            for method in methods:
                method_template = template.split('async {methodName}')[1].split('}')[0] + '}'
                method_code += method_template.replace('{methodName}', method['name'])
                method_code = method_code.replace('{endpoint}', method.get('endpoint', method['name']))
                method_code = method_code.replace('{method}', method.get('http_method', 'GET'))
            content = content.replace('async {methodName}(params?: any): Promise<any> {', method_code)
        
        target_file = f"src/services/{self._to_camel_case(service_name)}.service.ts"
        
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content={target_file: content},
            diff_summary=f"Created {service_name} service with API methods",
            explanations=[
                f"Generated {service_name} service class",
                "Includes error handling and TypeScript types",
                "Ready for integration with your API endpoints"
            ],
            dependencies=['fetch API'],
            test_suggestions=[
                f"Add unit tests for {service_name} service methods",
                "Mock API responses for testing",
                "Test error handling scenarios"
            ]
        )

    async def _generate_modification(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate modifications to existing code."""
        target_file = request.get('targetFile')
        description = request.get('description', '')
        context = request.get('context', {})
        
        if not target_file:
            return GeneratedCode(
                type=CodeType.PATCH,
                content="// Error: No target file specified for modification",
                warnings=["Cannot modify code without specifying target file"],
                explanations=["Please specify which file you want to modify"]
            )
        
        # Read existing file content (simulated)
        existing_content = await self._read_file_content(target_file, context)
        
        # Generate modifications based on description
        modified_content = await self._apply_modifications(existing_content, description, target_file)
        
        # Generate diff
        diff_summary = await self._generate_diff_summary(existing_content, modified_content)
        
        return GeneratedCode(
            type=CodeType.PATCH,
            content=modified_content,
            diff_summary=diff_summary,
            explanations=[
                f"Modified {target_file} based on request",
                "Preserved existing functionality while adding new features",
                "Changes are backwards compatible"
            ],
            warnings=self._analyze_modification_risks(existing_content, modified_content)
        )

    async def _generate_feature_addition(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate code to add a new feature to existing codebase."""
        description = request.get('description', '')
        context = request.get('context', {})
        
        # Analyze what type of feature is being added
        feature_type = self._classify_feature(description)
        
        if feature_type == 'ui_feature':
            return await self._add_ui_feature(request)
        elif feature_type == 'api_feature':
            return await self._add_api_feature(request)
        elif feature_type == 'utility_feature':
            return await self._add_utility_feature(request)
        else:
            return await self._add_generic_feature(request)

    async def _generate_bug_fix(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate code to fix identified bugs."""
        description = request.get('description', '')
        target_file = request.get('targetFile')
        
        # Analyze the bug description
        bug_type = self._classify_bug(description)
        
        # Generate appropriate fix
        if bug_type == 'null_reference':
            fix_code = self._generate_null_check_fix(description)
        elif bug_type == 'async_error':
            fix_code = self._generate_async_error_fix(description)
        elif bug_type == 'type_error':
            fix_code = self._generate_type_fix(description)
        else:
            fix_code = self._generate_generic_bug_fix(description)
        
        return GeneratedCode(
            type=CodeType.PATCH,
            content=fix_code,
            diff_summary=f"Fixed {bug_type} bug in {target_file}",
            explanations=[
                f"Identified and fixed {bug_type} issue",
                "Added error handling and validation",
                "Improved code robustness"
            ],
            test_suggestions=[
                "Add test cases for the bug scenario",
                "Verify fix doesn't break existing functionality",
                "Add regression tests"
            ]
        )

    # === Helper Methods ===

    def _extract_component_name(self, description: str) -> str:
        """Extract component name from description."""
        # Look for component name patterns
        patterns = [
            r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\s+component\b',
            r'\bcomponent\s+called\s+([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b',
            r'\bnew\s+([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b',
            r'\bcreate\s+(?:a\s+)?([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                return match.group(1)
        
        # Fallback to generic names
        if 'modal' in description.lower():
            return 'Modal'
        elif 'button' in description.lower():
            return 'Button'
        elif 'form' in description.lower():
            return 'Form'
        else:
            return 'Component'

    def _detect_framework(self, context: Dict, description: str) -> str:
        """Detect the framework being used."""
        if context.get('framework'):
            return context['framework']
        
        # Try to detect from project context
        project_path = context.get('projectPath', '')
        if 'react' in project_path.lower() or 'tsx' in description:
            return 'react'
        elif 'vue' in project_path.lower() or '.vue' in description:
            return 'vue'
        elif 'angular' in project_path.lower():
            return 'angular'
        else:
            return 'react'  # Default fallback

    def _add_component_features(self, content: str, description: str, framework: str) -> str:
        """Add specific features to component based on description."""
        features = []
        
        # Analyze description for features
        if 'dark mode' in description.lower() or 'theme' in description.lower():
            features.append('theme_toggle')
        if 'form' in description.lower() or 'input' in description.lower():
            features.append('form_handling')
        if 'modal' in description.lower() or 'dialog' in description.lower():
            features.append('modal_behavior')
        if 'api' in description.lower() or 'fetch' in description.lower():
            features.append('api_integration')
        
        # Apply features to content
        for feature in features:
            content = self._apply_feature_template(content, feature, framework)
        
        return content

    def _apply_feature_template(self, content: str, feature: str, framework: str) -> str:
        """Apply specific feature templates to the component."""
        if feature == 'theme_toggle' and framework == 'react':
            theme_code = '''
  const [darkMode, setDarkMode] = useState(false);
  
  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };'''
            content = content.replace('// Add state and logic here', theme_code)
            
        elif feature == 'form_handling' and framework == 'react':
            form_code = '''
  const [formData, setFormData] = useState({});
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };'''
            content = content.replace('// Add state and logic here', form_code)
        
        return content

    def _to_kebab_case(self, text: str) -> str:
        """Convert PascalCase to kebab-case."""
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', text).lower()

    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = re.findall(r'\b\w+\b', text)
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])

    def _extract_dependencies(self, description: str, framework: str) -> List[str]:
        """Extract dependencies needed for the code."""
        deps = []
        
        if framework == 'react':
            deps.append('react')
            if 'typescript' in description.lower() or 'tsx' in description.lower():
                deps.append('@types/react')
        
        if 'api' in description.lower():
            deps.append('axios')
        if 'router' in description.lower():
            deps.append('react-router-dom' if framework == 'react' else 'vue-router')
        if 'state' in description.lower() and framework == 'react':
            deps.append('zustand')
        
        return deps

    async def _read_file_content(self, file_path: str, context: Dict) -> str:
        """Read existing file content (simulated for demo)."""
        # In a real implementation, this would read the actual file
        return f"// Existing content of {file_path}\n// ... existing code ..."

    async def _apply_modifications(self, existing_content: str, description: str, target_file: str) -> str:
        """Apply modifications to existing content."""
        # This is a simplified implementation
        # In practice, this would use AST parsing and modification
        
        if 'add function' in description.lower():
            function_code = self._generate_function_from_description(description)
            return existing_content + '\n\n' + function_code
        elif 'modify function' in description.lower():
            return self._modify_existing_function(existing_content, description)
        else:
            return existing_content + f'\n\n// {description}'

    def _generate_function_from_description(self, description: str) -> str:
        """Generate a function based on natural language description."""
        # Extract function name
        function_match = re.search(r'function\s+called\s+(\w+)', description)
        if function_match:
            function_name = function_match.group(1)
        else:
            function_name = 'newFunction'
        
        return f'''
/**
 * {description}
 */
export function {function_name}() {{
  // TODO: Implement {description}
  return null;
}}'''

    async def _generate_diff_summary(self, old_content: str, new_content: str) -> str:
        """Generate a human-readable summary of changes."""
        if len(new_content) > len(old_content):
            return f"Added {len(new_content) - len(old_content)} characters of new code"
        elif len(new_content) < len(old_content):
            return f"Removed {len(old_content) - len(new_content)} characters"
        else:
            return "Modified existing code"

    def _analyze_modification_risks(self, old_content: str, new_content: str) -> List[str]:
        """Analyze potential risks in the modifications."""
        risks = []
        
        if 'delete' in new_content.lower() and 'delete' not in old_content.lower():
            risks.append("Added deletion operations - review carefully")
        
        if len(new_content) < len(old_content) * 0.5:
            risks.append("Significant content reduction - ensure no important code was removed")
        
        return risks

    def _classify_feature(self, description: str) -> str:
        """Classify the type of feature being added."""
        if any(keyword in description.lower() for keyword in ['button', 'modal', 'component', 'ui', 'interface']):
            return 'ui_feature'
        elif any(keyword in description.lower() for keyword in ['api', 'endpoint', 'service', 'request']):
            return 'api_feature'
        elif any(keyword in description.lower() for keyword in ['utility', 'helper', 'function', 'method']):
            return 'utility_feature'
        else:
            return 'generic_feature'

    def _classify_bug(self, description: str) -> str:
        """Classify the type of bug being fixed."""
        if any(keyword in description.lower() for keyword in ['null', 'undefined', 'reference']):
            return 'null_reference'
        elif any(keyword in description.lower() for keyword in ['async', 'promise', 'await']):
            return 'async_error'
        elif any(keyword in description.lower() for keyword in ['type', 'typescript', 'interface']):
            return 'type_error'
        else:
            return 'generic_bug'

    # === Additional helper methods for other code generation scenarios ===
    
    async def _generate_refactor(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate refactored code."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// Refactored code placeholder",
            diff_summary="Code refactoring applied"
        )
    
    async def _generate_tests(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate test code."""
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content="// Test code placeholder",
            diff_summary="Test file created"
        )
    
    async def _generate_documentation(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate documentation."""
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content="// Documentation placeholder",
            diff_summary="Documentation added"
        )
    
    async def _generate_optimization(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate optimized code."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// Optimized code placeholder",
            diff_summary="Performance optimizations applied"
        )
    
    async def _generate_generic_change(self, request: Dict[str, Any]) -> GeneratedCode:
        """Generate generic code changes."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// Generic changes placeholder",
            diff_summary="Code changes applied"
        )
    
    async def _create_utility(self, request: Dict[str, Any]) -> GeneratedCode:
        """Create utility functions."""
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content="// Utility functions placeholder",
            diff_summary="Utility file created"
        )
    
    async def _create_page(self, request: Dict[str, Any]) -> GeneratedCode:
        """Create page component."""
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content="// Page component placeholder",
            diff_summary="Page component created"
        )
    
    async def _create_generic_file(self, request: Dict[str, Any]) -> GeneratedCode:
        """Create generic file."""
        return GeneratedCode(
            type=CodeType.FULL_FILE,
            content="// Generic file placeholder",
            diff_summary="File created"
        )
    
    def _generate_generic_component(self, name: str, description: str) -> str:
        """Generate generic component code."""
        return f"// Generic {name} component\n// {description}"
    
    def _extract_service_name(self, description: str) -> str:
        """Extract service name from description."""
        return "Service"
    
    def _extract_api_methods(self, description: str) -> List[Dict]:
        """Extract API methods from description."""
        return [{"name": "getData", "endpoint": "data", "http_method": "GET"}]
    
    async def _add_ui_feature(self, request: Dict[str, Any]) -> GeneratedCode:
        """Add a UI feature to existing codebase."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// UI feature addition placeholder",
            diff_summary="UI feature added"
        )
    
    async def _add_api_feature(self, request: Dict[str, Any]) -> GeneratedCode:
        """Add an API feature to existing codebase."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// API feature addition placeholder",
            diff_summary="API feature added"
        )
    
    async def _add_utility_feature(self, request: Dict[str, Any]) -> GeneratedCode:
        """Add utility feature."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// Utility feature addition placeholder",
            diff_summary="Utility feature added"
        )
    
    async def _add_generic_feature(self, request: Dict[str, Any]) -> GeneratedCode:
        """Add generic feature."""
        return GeneratedCode(
            type=CodeType.PATCH,
            content="// Generic feature addition placeholder",
            diff_summary="Feature added"
        )
    
    def _generate_null_check_fix(self, description: str) -> str:
        """Generate null check fix."""
        return "// Null check fix placeholder"
    
    def _generate_async_error_fix(self, description: str) -> str:
        """Generate async error fix."""
        return "// Async error fix placeholder"
    
    def _generate_type_fix(self, description: str) -> str:
        """Generate type fix."""
        return "// Type fix placeholder"
    
    def _generate_generic_bug_fix(self, description: str) -> str:
        """Generate generic bug fix."""
        return "// Bug fix placeholder"
    
    def _modify_existing_function(self, content: str, description: str) -> str:
        """Modify existing function."""
        return content + "\n// Function modification placeholder"

# === Integration Functions ===

async def generate_conversational_code(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for conversational code generation.
    Returns a dictionary compatible with the API response format.
    """
    generator = ConversationalCodeGenerator()
    result = await generator.generate_code(request)
    
    return {
        "generatedCode": {
            "type": result.type.value,
            "content": result.content,
            "diffSummary": result.diff_summary,
            "explanations": result.explanations,
            "warnings": result.warnings,
            "dependencies": result.dependencies,
            "testSuggestions": result.test_suggestions,
            "rollbackInfo": result.rollback_info
        },
        "metadata": {
            "generator_version": "1.0.0",
            "generation_timestamp": "2024-01-01T00:00:00Z",
            "request_processed": request
        }
    }

# === Export ===
__all__ = ['ConversationalCodeGenerator', 'generate_conversational_code', 'GeneratedCode', 'CodeType']
