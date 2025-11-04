"""OpenHands agent integration for SDD workflow."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .context import SpecContext


class OpenHandsContextProvider:
    """Provides specification context to OpenHands agents."""
    
    def __init__(self, project_dir: Optional[Path] = None, console: Optional[Console] = None):
        """Initialize context provider.
        
        Args:
            project_dir: Project directory, defaults to current working directory
            console: Rich console for output
        """
        self.project_dir = project_dir or Path.cwd()
        self.console = console or Console()
        self.spec_context = SpecContext(self.project_dir, self.console)
    
    def should_inject_context(self) -> bool:
        """Check if context should be injected for this session.
        
        Returns:
            True if this is an SDD project and context should be injected
        """
        return self.spec_context.is_sdd_project()
    
    def get_context_banner(self) -> str:
        """Get a banner message for SDD context injection.
        
        Returns:
            Banner message string
        """
        if not self.should_inject_context():
            return ""
        
        summary = self.spec_context.get_context_summary()
        
        banner_lines = [
            "🔍 SPECIFICATION-DRIVEN DEVELOPMENT PROJECT DETECTED",
            "═" * 60,
        ]
        
        # Add context availability info
        context_items = []
        if summary["has_constitution"]:
            context_items.append("📜 Constitutional principles")
        if summary["has_specification"]:
            context_items.append("📋 Project specification")
        if summary["has_plan"]:
            context_items.append("🏗️ Implementation plan")
        if summary["has_tasks"]:
            pending = summary["pending_task_count"]
            total = summary["total_task_count"]
            context_items.append(f"✅ Development tasks ({total - pending}/{total} complete)")
        
        if context_items:
            banner_lines.append("Loaded SDD context:")
            for item in context_items:
                banner_lines.append(f"  • {item}")
        
        banner_lines.extend([
            "",
            "🤖 Your responses will be guided by constitutional principles",
            "   and current project specifications.",
            "═" * 60
        ])
        
        return "\n".join(banner_lines)
    
    def get_initial_context_message(self) -> str:
        """Get initial context message for agent conversation.
        
        Returns:
            Context message for agent
        """
        if not self.should_inject_context():
            return ""
        
        context = self.spec_context.get_agent_context(include_tasks=True)
        
        # Wrap with clear markers
        message = f"""
{self.get_context_banner()}

{context}

---
**This context will guide our conversation. Please reference these specifications and constitutional principles in your responses.**
"""
        return message
    
    def get_compact_context(self) -> str:
        """Get compact context for ongoing conversations.
        
        Returns:
            Compact context string
        """
        if not self.should_inject_context():
            return ""
        
        summary = self.spec_context.get_context_summary()
        
        # Load key information
        constitution = self.spec_context.load_constitution()
        spec = self.spec_context.load_latest_specification()
        tasks = self.spec_context.load_pending_tasks()
        
        context_parts = []
        
        # Constitutional principles (compact)
        if constitution:
            principles = self.spec_context._extract_key_principles(constitution)
            if principles:
                context_parts.append("📜 **Constitutional Principles**: " + " | ".join(principles[:3]))
        
        # Current specification
        if spec:
            context_parts.append(f"📋 **Specification**: {spec['metadata'].get('title', 'Unknown')}")
        
        # Task progress
        if tasks:
            pending = len(tasks['pending_tasks'])
            total = tasks['total_tasks']
            progress_pct = ((total - pending) / total * 100) if total > 0 else 0
            context_parts.append(f"✅ **Progress**: {total - pending}/{total} tasks ({progress_pct:.0f}%)")
            
            # Next immediate task
            if tasks['pending_tasks']:
                next_task = tasks['pending_tasks'][0]
                context_parts.append(f"🎯 **Next Task**: {next_task['description']}")
        
        if context_parts:
            return "\n".join([
                "🔍 **SDD Context**: " + " • ".join(context_parts),
                ""
            ])
        
        return ""
    
    def format_context_for_system_prompt(self) -> str:
        """Format context for system prompt injection.
        
        Returns:
            System prompt context string
        """
        if not self.should_inject_context():
            return ""
        
        context = self.spec_context.get_agent_context(include_tasks=False)
        
        # Format for system prompt
        system_context = f"""
You are working on a Specification-Driven Development (SDD) project. Here is the current project context:

{context}

IMPORTANT INSTRUCTIONS:
1. Always consider constitutional principles when making suggestions
2. Ensure all implementations align with project specifications  
3. Reference specific requirements when discussing features
4. Maintain consistency with the established implementation plan
5. Help track progress by noting completed tasks

Your responses should demonstrate awareness of this SDD context and help advance the project according to its constitutional principles and specifications.
"""
        return system_context
    
    def update_context_on_change(self, file_path: Path) -> Optional[str]:
        """Update agent context when specs change.
        
        Args:
            file_path: Path to changed file
            
        Returns:
            Update message if relevant change detected
        """
        if not self.should_inject_context():
            return None
        
        # Check if the change affects SDD context
        file_str = str(file_path)
        
        if ".specify/" in file_str:
            return "🔄 **SDD Context Updated**: Project specifications have been modified. Please refresh context if needed."
        
        if "/specs/" in file_str and file_path.suffix == ".md":
            return "📋 **Specification Updated**: Project specifications or plans have been updated."
        
        # Check if it's a constitution change
        if file_path.name == "constitution.md":
            return "📜 **Constitutional Update**: Project principles have been modified. All future work should align with updated constitution."
        
        return None
    
    def validate_agent_response(self, response: str) -> Dict[str, Any]:
        """Validate agent response against constitutional principles.
        
        Args:
            response: Agent response text
            
        Returns:
            Validation results
        """
        if not self.should_inject_context():
            return {"valid": True, "issues": [], "suggestions": []}
        
        constitution = self.spec_context.load_constitution()
        if not constitution:
            return {"valid": True, "issues": [], "suggestions": []}
        
        issues = []
        suggestions = []
        
        # Check for constitutional principle violations
        response_lower = response.lower()
        constitution_lower = constitution.lower()
        
        # Security checks
        if "security" in constitution_lower:
            if ("password" in response_lower or "auth" in response_lower) and "secure" not in response_lower:
                issues.append("Security concerns not addressed despite constitutional security requirements")
                suggestions.append("Consider adding security measures (encryption, validation, etc.)")
        
        # Quality checks
        if "quality" in constitution_lower or "testing" in constitution_lower:
            if ("implement" in response_lower or "code" in response_lower) and "test" not in response_lower:
                suggestions.append("Consider mentioning testing strategy per constitutional quality requirements")
        
        # User-centered checks
        if "user" in constitution_lower:
            if "feature" in response_lower and "user" not in response_lower:
                suggestions.append("Consider user impact and experience per constitutional user-centered principles")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def suggest_next_actions(self) -> List[str]:
        """Suggest next actions based on current context.
        
        Returns:
            List of suggested next actions
        """
        if not self.should_inject_context():
            return []
        
        suggestions = []
        summary = self.spec_context.get_context_summary()
        
        # Suggest missing SDD artifacts
        if not summary["has_constitution"]:
            suggestions.append("Create project constitution: `openhands spec constitution`")
        
        if not summary["has_specification"]:
            suggestions.append("Create project specification: `openhands spec specify`")
        
        if summary["has_specification"] and not summary["has_plan"]:
            suggestions.append("Generate implementation plan: `openhands spec plan`")
        
        if summary["has_plan"] and not summary["has_tasks"]:
            suggestions.append("Generate development tasks: `openhands spec tasks`")
        
        # Suggest task progression
        if summary["has_tasks"] and summary["pending_task_count"] > 0:
            tasks = self.spec_context.load_pending_tasks()
            if tasks and tasks['pending_tasks']:
                next_task = tasks['pending_tasks'][0]
                suggestions.append(f"Work on next task: {next_task['description']}")
        
        # Suggest documentation updates
        if summary["pending_task_count"] < summary["total_task_count"] / 2:
            suggestions.append("Update project documentation with progress")
        
        return suggestions
    
    def get_progress_summary(self) -> str:
        """Get current project progress summary.
        
        Returns:
            Progress summary string
        """
        if not self.should_inject_context():
            return "No SDD context available"
        
        summary = self.spec_context.get_context_summary()
        
        progress_parts = []
        
        # SDD artifact completion
        artifacts = []
        if summary["has_constitution"]:
            artifacts.append("✅ Constitution")
        else:
            artifacts.append("❌ Constitution")
        
        if summary["has_specification"]:
            artifacts.append("✅ Specification")
        else:
            artifacts.append("❌ Specification")
        
        if summary["has_plan"]:
            artifacts.append("✅ Implementation Plan")
        else:
            artifacts.append("❌ Implementation Plan")
        
        if summary["has_tasks"]:
            artifacts.append("✅ Development Tasks")
        else:
            artifacts.append("❌ Development Tasks")
        
        progress_parts.append("**SDD Artifacts**: " + " | ".join(artifacts))
        
        # Task completion
        if summary["has_tasks"]:
            completed = summary["total_task_count"] - summary["pending_task_count"]
            total = summary["total_task_count"]
            progress_pct = (completed / total * 100) if total > 0 else 0
            progress_parts.append(f"**Task Progress**: {completed}/{total} ({progress_pct:.0f}%)")
        
        return "\n".join(progress_parts)