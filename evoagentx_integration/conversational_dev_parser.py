"""
Conversational Development Intelligence Parser

This module extends the existing intelligence parser to specifically handle
development-related requests in natural language, extracting intent, target files,
and implementation approaches.
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class DevIntent(Enum):
    CREATE = "create"
    MODIFY = "modify" 
    DELETE = "delete"
    REFACTOR = "refactor"
    ADD_FEATURE = "add_feature"
    FIX_BUG = "fix_bug"
    OPTIMIZE = "optimize"
    TEST = "test"
    DOCUMENT = "document"

class ComplexityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ParsedDevRequest:
    intent: DevIntent
    description: str
    confidence: float
    target_file: Optional[str] = None
    required_files: Optional[List[str]] = None
    suggested_approach: Optional[str] = None
    estimated_complexity: Optional[ComplexityLevel] = None
    dependencies: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None

class ConversationalDevParser:
    """
    Advanced parser for development requests in natural language.
    Identifies intent, files, and generates implementation strategies.
    """
    
    def __init__(self):
        self.intent_patterns = {
            DevIntent.CREATE: [
                r'\b(create|add|make|build|generate|new)\b.*\b(component|function|class|file|module|page)\b',
                r'\b(implement|setup|initialize)\b',
                r'\bnew\s+\w+',
                r'\bcreate\s+(a\s+)?(\w+\s+)*(component|service|utility|helper)'
            ],
            DevIntent.MODIFY: [
                r'\b(change|modify|update|edit|alter)\b',
                r'\b(adjust|tweak|revise)\b',
                r'\bmake\s+.+\s+(different|better)',
                r'\bupdate\s+the\b'
            ],
            DevIntent.DELETE: [
                r'\b(remove|delete|drop|eliminate)\b',
                r'\bget\s+rid\s+of\b',
                r'\btake\s+(out|away)\b'
            ],
            DevIntent.REFACTOR: [
                r'\b(refactor|restructure|reorganize|clean\s+up)\b',
                r'\bimprove\s+the\s+(structure|organization|code\s+quality)\b',
                r'\bsplit\s+(up|into)',
                r'\bmove\s+.+\s+to\b'
            ],
            DevIntent.ADD_FEATURE: [
                r'\badd\s+(feature|functionality|capability|support\s+for)\b',
                r'\bimplement\s+.+\s+(feature|function)\b',
                r'\benable\s+.+\s+to\b',
                r'\bmake\s+it\s+(possible|able)\s+to\b'
            ],
            DevIntent.FIX_BUG: [
                r'\b(fix|repair|resolve|solve)\b.*\b(bug|issue|problem|error)\b',
                r'\b(debug|troubleshoot)\b',
                r'\b(broken|not\s+working|failing)\b',
                r'\berror\s+.+\s+(fix|handle|catch)'
            ],
            DevIntent.OPTIMIZE: [
                r'\b(optimize|improve\s+performance|speed\s+up|make\s+faster)\b',
                r'\b(reduce|minimize|decrease)\s+.+\s+(time|memory|size)\b',
                r'\bmore\s+efficient\b',
                r'\bbetter\s+performance\b'
            ],
            DevIntent.TEST: [
                r'\b(test|testing|unit\s+test|integration\s+test)\b',
                r'\bwrite\s+tests?\s+for\b',
                r'\badd\s+test\s+coverage\b',
                r'\bvalidate\s+that\b'
            ],
            DevIntent.DOCUMENT: [
                r'\b(document|documentation|comments?|readme)\b',
                r'\bwrite\s+docs?\s+for\b',
                r'\badd\s+(comments|documentation)\b',
                r'\bexplain\s+how\s+.+\s+works\b'
            ]
        }
        
        # File extension patterns
        self.file_patterns = {
            r'\.tsx?$': 'typescript',
            r'\.jsx?$': 'javascript', 
            r'\.py$': 'python',
            r'\.vue$': 'vue',
            r'\.css$': 'css',
            r'\.scss$': 'scss',
            r'\.html$': 'html',
            r'\.json$': 'json',
            r'\.md$': 'markdown'
        }
        
        # Component/feature indicators
        self.component_patterns = [
            r'\b(component|widget|element)\b',
            r'\b(modal|dialog|popup|overlay)\b',
            r'\b(button|input|form|field)\b',
            r'\b(header|footer|sidebar|navbar)\b',
            r'\b(page|view|screen|route)\b',
            r'\b(service|utility|helper|hook)\b',
            r'\b(api|endpoint|request|response)\b'
        ]
        
        # Complexity indicators
        self.complexity_indicators = {
            ComplexityLevel.LOW: [
                r'\bsimple\b', r'\bbasic\b', r'\bquick\b', r'\bsmall\b',
                r'\beasy\b', r'\bminor\b', r'\btoggle\b', r'\bshow/hide\b'
            ],
            ComplexityLevel.HIGH: [
                r'\bcomplex\b', r'\badvanced\b', r'\bfull\b', r'\bcomplete\b',
                r'\bentire\b', r'\bmultiple\b', r'\bintegration\b', r'\bsystem\b',
                r'\barchitecture\b', r'\bframework\b', r'\bdatabase\b'
            ]
        }

    def parse_dev_request(self, message: str, context: Optional[Dict] = None) -> ParsedDevRequest:
        """
        Parse a natural language development request and extract structured information.
        """
        message_lower = message.lower()
        
        # 1. Determine intent
        intent, intent_confidence = self._extract_intent(message_lower)
        
        # 2. Extract target files
        target_file, file_confidence = self._extract_target_file(message, context)
        
        # 3. Determine complexity
        complexity = self._estimate_complexity(message_lower)
        
        # 4. Extract dependencies and requirements
        dependencies = self._extract_dependencies(message_lower)
        
        # 5. Identify risk factors
        risk_factors = self._identify_risk_factors(message_lower, intent)
        
        # 6. Generate suggested approach
        suggested_approach = self._generate_approach(intent, message_lower, complexity)
        
        # 7. Calculate overall confidence
        overall_confidence = self._calculate_confidence(
            intent_confidence, file_confidence, message_lower
        )
        
        return ParsedDevRequest(
            intent=intent,
            description=message.strip(),
            confidence=overall_confidence,
            target_file=target_file,
            suggested_approach=suggested_approach,
            estimated_complexity=complexity,
            dependencies=dependencies,
            risk_factors=risk_factors
        )

    def _extract_intent(self, message_lower: str) -> Tuple[DevIntent, float]:
        """Extract the development intent from the message."""
        best_intent = DevIntent.MODIFY
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            confidence = 0.0
            for pattern in patterns:
                matches = re.findall(pattern, message_lower, re.IGNORECASE)
                if matches:
                    confidence += len(matches) * 0.3
            
            # Normalize confidence
            confidence = min(confidence, 1.0)
            
            if confidence > best_confidence:
                best_intent = intent
                best_confidence = confidence
        
        # Default confidence if no strong matches
        if best_confidence == 0.0:
            best_confidence = 0.5
        
        return best_intent, best_confidence

    def _extract_target_file(self, message: str, context: Optional[Dict] = None) -> Tuple[Optional[str], float]:
        """Extract target file from the message."""
        # Look for file paths and file extensions
        file_pattern = r'[a-zA-Z0-9_/-]+\.[a-zA-Z0-9]+(?:\s|$|[,.])'
        matches = re.findall(file_pattern, message)
        
        if matches:
            # Clean up the match
            target_file = matches[0].strip(' ,.')
            return target_file, 0.8
        
        # Look for component names that might correspond to files
        component_matches = []
        for pattern in self.component_patterns:
            component_matches.extend(re.findall(pattern, message.lower()))
        
        if component_matches and context and 'project_path' in context:
            # Try to guess file based on component name
            return None, 0.3
        
        return None, 0.0

    def _estimate_complexity(self, message_lower: str) -> ComplexityLevel:
        """Estimate the complexity of the request."""
        complexity_scores = {level: 0 for level in ComplexityLevel}
        
        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if re.search(indicator, message_lower):
                    complexity_scores[level] += 1
        
        # Default to medium if no clear indicators
        if all(score == 0 for score in complexity_scores.values()):
            return ComplexityLevel.MEDIUM
        
        return max(complexity_scores.keys(), key=lambda k: complexity_scores[k])

    def _extract_dependencies(self, message_lower: str) -> List[str]:
        """Extract potential dependencies from the message."""
        dependencies = []
        
        # Common framework/library patterns
        dependency_patterns = [
            r'\breact\b', r'\bvue\b', r'\bangular\b',
            r'\btypescript\b', r'\bjavascript\b',
            r'\bapi\b', r'\brest\b', r'\bgraphql\b',
            r'\bdatabase\b', r'\bsql\b', r'\bmongo\b',
            r'\bauth\b', r'\blogin\b', r'\bsession\b',
            r'\brouting\b', r'\brouter\b', r'\bnavigation\b'
        ]
        
        for pattern in dependency_patterns:
            if re.search(pattern, message_lower):
                dependencies.append(pattern.strip(r'\b'))
        
        return dependencies

    def _identify_risk_factors(self, message_lower: str, intent: DevIntent) -> List[str]:
        """Identify potential risk factors for the request."""
        risks = []
        
        # High-risk operations
        if intent == DevIntent.DELETE:
            risks.append("Data loss potential")
        
        if intent == DevIntent.REFACTOR:
            risks.append("Breaking changes possible")
        
        # Look for complexity indicators
        if re.search(r'\b(database|schema|migration)\b', message_lower):
            risks.append("Database changes required")
        
        if re.search(r'\b(api|endpoint|backend)\b', message_lower):
            risks.append("API compatibility concerns")
        
        if re.search(r'\b(authentication|auth|security)\b', message_lower):
            risks.append("Security implications")
        
        return risks

    def _generate_approach(self, intent: DevIntent, message_lower: str, complexity: ComplexityLevel) -> str:
        """Generate a suggested implementation approach."""
        approaches = {
            DevIntent.CREATE: "1. Design component interface\n2. Implement basic structure\n3. Add functionality\n4. Test and refine",
            DevIntent.MODIFY: "1. Analyze current implementation\n2. Plan modifications\n3. Apply changes incrementally\n4. Test thoroughly",
            DevIntent.DELETE: "1. Identify dependencies\n2. Plan removal strategy\n3. Remove safely\n4. Clean up references",
            DevIntent.REFACTOR: "1. Document current behavior\n2. Plan new structure\n3. Refactor incrementally\n4. Maintain test coverage",
            DevIntent.ADD_FEATURE: "1. Design feature requirements\n2. Plan integration points\n3. Implement core functionality\n4. Add tests and documentation",
            DevIntent.FIX_BUG: "1. Reproduce the issue\n2. Identify root cause\n3. Implement fix\n4. Add regression tests",
            DevIntent.OPTIMIZE: "1. Profile current performance\n2. Identify bottlenecks\n3. Implement optimizations\n4. Measure improvements",
            DevIntent.TEST: "1. Identify test cases\n2. Set up test environment\n3. Write comprehensive tests\n4. Ensure coverage",
            DevIntent.DOCUMENT: "1. Audit current documentation\n2. Identify gaps\n3. Write clear documentation\n4. Review and update"
        }
        
        base_approach = approaches.get(intent, "1. Analyze requirements\n2. Plan implementation\n3. Execute changes\n4. Test and validate")
        
        # Add complexity-specific notes
        if complexity == ComplexityLevel.HIGH:
            base_approach += "\n\nNote: High complexity - consider breaking into smaller tasks"
        elif complexity == ComplexityLevel.LOW:
            base_approach += "\n\nNote: Low complexity - quick implementation possible"
        
        return base_approach

    def _calculate_confidence(self, intent_confidence: float, file_confidence: float, message_lower: str) -> float:
        """Calculate overall parsing confidence."""
        # Base confidence from intent and file extraction
        base_confidence = (intent_confidence * 0.6) + (file_confidence * 0.4)
        
        # Boost for clear, specific language
        specificity_boost = 0.0
        if len(message_lower.split()) > 5:  # Longer messages often more specific
            specificity_boost += 0.1
        
        if re.search(r'\b(need|want|should|must|require)\b', message_lower):
            specificity_boost += 0.1
        
        return min(base_confidence + specificity_boost, 1.0)

    def parse_request(self, message: str, context: Optional[Dict[str, Any]] = None) -> ParsedDevRequest:
        """
        Main parsing method that analyzes a development request.
        """
        return self.parse_dev_request(message, context)

# === Utility Functions ===

def parse_conversational_dev_request(message: str, context: Optional[dict] = None) -> dict:
    """
    Parse a natural language development request into structured data.
    
    Args:
        message: User's natural language request
        context: Additional context (project path, current file, etc.)
    
    Returns:
        Dictionary with parsed request data
    """
    if context is None:
        context = {}
    
    parser = ConversationalDevParser()
    parsed_request = parser.parse_dev_request(message, context)
    
    return {
        "intent": parsed_request.intent.value,
        "description": parsed_request.description,
        "confidence": parsed_request.confidence,
        "targetFile": parsed_request.target_file,
        "requiredFiles": parsed_request.required_files,
        "suggestedApproach": parsed_request.suggested_approach,
        "estimatedComplexity": parsed_request.estimated_complexity.value if parsed_request.estimated_complexity else None,
        "dependencies": parsed_request.dependencies,
        "riskFactors": parsed_request.risk_factors
    }

# === Example Usage ===
if __name__ == "__main__":
    # Test the parser with sample requests
    test_requests = [
        "Add a dark mode toggle to the settings component",
        "Fix the API error handling in src/services/auth.js",
        "Create a new user profile page with edit functionality",
        "Refactor the dashboard component to use hooks instead of class components",
        "Optimize the image loading performance in the gallery"
    ]
    
    parser = ConversationalDevParser()
    
    for request in test_requests:
        print(f"\nRequest: {request}")
        result = parse_conversational_dev_request(request)
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Approach: {result['suggestedApproach']}")
        print("-" * 50)
