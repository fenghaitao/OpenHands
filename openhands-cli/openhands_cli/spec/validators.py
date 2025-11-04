"""Validation systems for specifications and constitutional alignment."""

import re
from typing import Dict, List, Any, Optional

from rich.console import Console


class SpecificationValidator:
    """Validates specification completeness and quality."""
    
    def __init__(self, console: Console):
        """Initialize specification validator.
        
        Args:
            console: Rich console for output
        """
        self.console = console
    
    def validate_specification(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specification completeness and quality.
        
        Args:
            spec_data: Specification data to validate
            
        Returns:
            Validation results with issues and suggestions
        """
        issues = []
        suggestions = []
        
        # Check required fields
        required_fields = ["title", "overview", "functional_requirements"]
        for field in required_fields:
            if not spec_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Check minimum content requirements
        if len(spec_data.get("functional_requirements", [])) < 3:
            suggestions.append("Consider adding more functional requirements for completeness")
        
        if len(spec_data.get("user_stories", [])) < 2:
            suggestions.append("User stories help clarify requirements from user perspective")
        
        # Check for common issues
        overview = spec_data.get("overview", "")
        if overview and len(overview.split()) < 20:
            suggestions.append("Project overview could be more detailed")
        
        # Check for vague language
        vague_patterns = [r'\bsomehow\b', r'\bmaybe\b', r'\bpossibly\b', r'\bkind of\b']
        for req in spec_data.get("functional_requirements", []):
            for pattern in vague_patterns:
                if re.search(pattern, req, re.IGNORECASE):
                    issues.append(f"Vague language in requirement: '{req}'")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "score": self._calculate_quality_score(spec_data, issues, suggestions)
        }
    
    def _calculate_quality_score(self, spec_data: Dict[str, Any], issues: List[str], suggestions: List[str]) -> float:
        """Calculate a quality score for the specification."""
        base_score = 100.0
        
        # Deduct for issues
        base_score -= len(issues) * 15
        
        # Deduct for missing suggestions
        base_score -= len(suggestions) * 5
        
        # Bonus for completeness
        if spec_data.get("technical_specifications"):
            base_score += 10
        if spec_data.get("success_metrics"):
            base_score += 10
        if len(spec_data.get("user_stories", [])) >= 5:
            base_score += 5
        
        return max(0.0, min(100.0, base_score))


class ConstitutionValidator:
    """Validates alignment with constitutional principles."""
    
    def __init__(self, console: Console):
        """Initialize constitution validator.
        
        Args:
            console: Rich console for output
        """
        self.console = console
    
    def validate_against_constitution(self, spec_data: Dict[str, Any], constitution: str) -> Dict[str, Any]:
        """Validate specification against constitutional principles.
        
        Args:
            spec_data: Specification data to validate
            constitution: Constitutional text to validate against
            
        Returns:
            Validation results with violations and suggestions
        """
        violations = []
        suggestions = []
        
        # Extract constitutional principles
        principles = self._extract_principles(constitution)
        
        # Check for principle violations
        for principle, description in principles.items():
            violation = self._check_principle_violation(spec_data, principle, description)
            if violation:
                violations.append(violation)
        
        # Generate suggestions based on constitution
        suggestions.extend(self._generate_constitutional_suggestions(spec_data, constitution))
        
        return {
            "is_valid": len(violations) == 0,
            "violations": violations,
            "suggestions": suggestions,
            "principles_checked": list(principles.keys())
        }
    
    def _extract_principles(self, constitution: str) -> Dict[str, str]:
        """Extract principles from constitution text.
        
        Args:
            constitution: Constitutional text
            
        Returns:
            Dictionary of principle names to descriptions
        """
        principles = {}
        
        # Look for principle patterns
        principle_patterns = [
            r'##\s*([^#\n]+)\n([^#]*?)(?=##|\Z)',  # Level 2 headers
            r'\*\*([^*]+)\*\*:?\s*([^\n*]+)',      # Bold text patterns
            r'-\s*\*\*([^*]+)\*\*:?\s*([^\n]+)',   # List with bold
        ]
        
        for pattern in principle_patterns:
            matches = re.finditer(pattern, constitution, re.MULTILINE | re.DOTALL)
            for match in matches:
                principle_name = match.group(1).strip()
                principle_desc = match.group(2).strip()
                if principle_name and principle_desc:
                    principles[principle_name] = principle_desc
        
        # Add some common principles if not found
        if not principles:
            principles = {
                "Quality First": "Prioritize code quality, testing, and maintainability",
                "User-Centered": "Focus on user needs and experience",
                "Security": "Security considerations in all design decisions"
            }
        
        return principles
    
    def _check_principle_violation(self, spec_data: Dict[str, Any], principle: str, description: str) -> Optional[str]:
        """Check if specification violates a constitutional principle.
        
        Args:
            spec_data: Specification data
            principle: Principle name
            description: Principle description
            
        Returns:
            Violation description if found, None otherwise
        """
        # Check for security principle violations
        if "security" in principle.lower():
            security_requirements = [req for req in spec_data.get("non_functional_requirements", []) 
                                   if "security" in req.lower() or "auth" in req.lower()]
            if not security_requirements:
                return f"No security requirements found, violating '{principle}' principle"
        
        # Check for quality principle violations
        if "quality" in principle.lower() or "testing" in principle.lower():
            testing_requirements = [req for req in spec_data.get("non_functional_requirements", [])
                                   if "test" in req.lower() or "quality" in req.lower()]
            if not testing_requirements:
                return f"No testing/quality requirements found, violating '{principle}' principle"
        
        # Check for user-centered principle violations
        if "user" in principle.lower():
            if len(spec_data.get("user_stories", [])) < 2:
                return f"Insufficient user stories, violating '{principle}' principle"
        
        return None
    
    def _generate_constitutional_suggestions(self, spec_data: Dict[str, Any], constitution: str) -> List[str]:
        """Generate suggestions based on constitutional principles.
        
        Args:
            spec_data: Specification data
            constitution: Constitutional text
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Suggest security requirements if constitution mentions security
        if "security" in constitution.lower():
            security_reqs = [req for req in spec_data.get("non_functional_requirements", [])
                           if "security" in req.lower()]
            if not security_reqs:
                suggestions.append("Consider adding security requirements (authentication, authorization, data protection)")
        
        # Suggest performance requirements if constitution mentions performance
        if "performance" in constitution.lower():
            perf_reqs = [req for req in spec_data.get("non_functional_requirements", [])
                        if "performance" in req.lower() or "speed" in req.lower()]
            if not perf_reqs:
                suggestions.append("Consider adding performance requirements and benchmarks")
        
        # Suggest testing requirements if constitution mentions quality
        if "quality" in constitution.lower() or "testing" in constitution.lower():
            test_reqs = [req for req in spec_data.get("non_functional_requirements", [])
                        if "test" in req.lower()]
            if not test_reqs:
                suggestions.append("Consider adding testing requirements (unit tests, integration tests, coverage)")
        
        return suggestions


class AmbiguityDetector:
    """Detects ambiguous areas in specifications."""
    
    def __init__(self, console: Console):
        """Initialize ambiguity detector.
        
        Args:
            console: Rich console for output
        """
        self.console = console
    
    def detect_ambiguities(self, spec_content: str) -> List[Dict[str, Any]]:
        """Find ambiguous phrases and concepts.
        
        Args:
            spec_content: Specification content to analyze
            
        Returns:
            List of detected ambiguities with details
        """
        ambiguities = []
        
        # Ambiguous words and phrases
        ambiguous_patterns = [
            (r'\b(should|could|might|may)\b', "Modal verbs create ambiguity"),
            (r'\b(some|several|many|few)\b', "Quantifiers are vague"),
            (r'\b(fast|slow|big|small|easy|hard)\b', "Subjective adjectives need definition"),
            (r'\b(appropriate|suitable|reasonable)\b', "Subjective judgments need criteria"),
            (r'\b(etc\.|and so on|and more)\b', "Open-ended lists are incomplete"),
            (r'\b(user-friendly|intuitive|simple)\b', "UX terms need specific criteria")
        ]
        
        for pattern, issue_type in ambiguous_patterns:
            matches = re.finditer(pattern, spec_content, re.IGNORECASE)
            for match in matches:
                ambiguities.append({
                    "text": match.group(),
                    "issue": issue_type,
                    "position": match.span(),
                    "suggestion": self._get_disambiguation_suggestion(match.group(), issue_type)
                })
        
        return ambiguities
    
    def _get_disambiguation_suggestion(self, ambiguous_text: str, issue_type: str) -> str:
        """Get suggestion for disambiguating text.
        
        Args:
            ambiguous_text: The ambiguous text found
            issue_type: Type of ambiguity issue
            
        Returns:
            Suggestion for improvement
        """
        suggestions = {
            "Modal verbs create ambiguity": f"Replace '{ambiguous_text}' with 'must', 'will', or 'shall'",
            "Quantifiers are vague": f"Replace '{ambiguous_text}' with specific numbers or ranges",
            "Subjective adjectives need definition": f"Define '{ambiguous_text}' with measurable criteria",
            "Subjective judgments need criteria": f"Specify criteria for what constitutes '{ambiguous_text}'",
            "Open-ended lists are incomplete": "Complete the list or specify what 'etc.' includes",
            "UX terms need specific criteria": f"Define '{ambiguous_text}' with measurable usability criteria"
        }
        
        return suggestions.get(issue_type, "Consider making this more specific")
    
    def generate_clarifying_questions(self, ambiguities: List[Dict[str, Any]]) -> List[str]:
        """Generate specific clarifying questions.
        
        Args:
            ambiguities: List of detected ambiguities
            
        Returns:
            List of clarifying questions
        """
        questions = []
        
        for ambiguity in ambiguities:
            text = ambiguity["text"]
            issue = ambiguity["issue"]
            
            if "Modal verbs" in issue:
                questions.append(f"Is '{text}' a requirement (must) or optional (could)?")
            elif "Quantifiers" in issue:
                questions.append(f"What specific number or range does '{text}' represent?")
            elif "Subjective" in issue:
                questions.append(f"What measurable criteria define '{text}'?")
            elif "Open-ended" in issue:
                questions.append(f"What specific items are included in '{text}'?")
        
        return questions