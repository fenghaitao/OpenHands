"""Specification context management for OpenHands agent integration."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console


class SpecContext:
    """Manages specification context for OpenHands agents."""
    
    def __init__(self, project_dir: Path, console: Optional[Console] = None):
        """Initialize specification context manager.
        
        Args:
            project_dir: Project directory path
            console: Rich console for output (optional)
        """
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.specs_dir = project_dir / "specs"
        self.console = console or Console()
    
    def is_sdd_project(self) -> bool:
        """Check if current directory is a specification-driven project.
        
        Returns:
            True if SDD project structure exists
        """
        return (
            self.specify_dir.exists() and
            (self.specify_dir / "memory" / "constitution.md").exists()
        )
    
    def load_constitution(self) -> Optional[str]:
        """Load constitutional principles.
        
        Returns:
            Constitutional text or None if not found
        """
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        if constitution_path.exists():
            return constitution_path.read_text(encoding='utf-8')
        return None
    
    def load_latest_specification(self) -> Optional[Dict[str, Any]]:
        """Load most recent specification.
        
        Returns:
            Specification data or None if not found
        """
        if not self.specs_dir.exists():
            return None
        
        # Find latest specification (not plan or tasks)
        spec_files = [
            f for f in self.specs_dir.glob("*.json")
            if not f.stem.startswith(("plan_", "tasks_"))
        ]
        
        if not spec_files:
            return None
        
        # Sort by creation time (latest first)
        spec_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        metadata_path = spec_files[0]
        spec_path = self.specs_dir / f"{metadata_path.stem}.md"
        
        if not spec_path.exists():
            return None
        
        # Load metadata and content
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        content = spec_path.read_text(encoding='utf-8')
        
        return {
            "metadata": metadata,
            "content": content,
            "path": spec_path
        }
    
    def load_active_plan(self) -> Optional[Dict[str, Any]]:
        """Load current implementation plan.
        
        Returns:
            Plan data or None if not found
        """
        if not self.specs_dir.exists():
            return None
        
        # Find latest plan
        plan_files = list(self.specs_dir.glob("plan_*.json"))
        if not plan_files:
            return None
        
        # Sort by creation time (latest first)
        plan_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        metadata_path = plan_files[0]
        plan_path = self.specs_dir / f"{metadata_path.stem}.md"
        
        if not plan_path.exists():
            return None
        
        # Load metadata and content
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        content = plan_path.read_text(encoding='utf-8')
        
        return {
            "metadata": metadata,
            "content": content,
            "path": plan_path
        }
    
    def load_pending_tasks(self) -> Optional[Dict[str, Any]]:
        """Load outstanding tasks.
        
        Returns:
            Tasks data or None if not found
        """
        if not self.specs_dir.exists():
            return None
        
        # Find latest tasks
        task_files = list(self.specs_dir.glob("tasks_*.json"))
        if not task_files:
            return None
        
        # Sort by creation time (latest first)
        task_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        metadata_path = task_files[0]
        tasks_path = self.specs_dir / f"{metadata_path.stem}.md"
        
        if not tasks_path.exists():
            return None
        
        # Load metadata and content
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        content = tasks_path.read_text(encoding='utf-8')
        
        # Parse tasks to identify completed vs pending
        pending_tasks = self._parse_pending_tasks(content)
        
        return {
            "metadata": metadata,
            "content": content,
            "path": tasks_path,
            "pending_tasks": pending_tasks,
            "total_tasks": metadata.get("total_tasks", 0)
        }
    
    def _parse_pending_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Parse task content to identify pending tasks.
        
        Args:
            content: Tasks markdown content
            
        Returns:
            List of pending task dictionaries
        """
        pending_tasks = []
        current_category = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Detect category headers
            if line.startswith('### ') and not line.startswith('###'):
                current_category = line[4:].strip()
            
            # Detect unchecked task items
            elif line.startswith('- [ ] '):
                task_text = line[6:].strip()
                # Extract task number and description
                if task_text.startswith('**') and '.**' in task_text:
                    parts = task_text.split('.**', 1)
                    if len(parts) == 2:
                        task_num = parts[0].replace('**', '').strip()
                        description = parts[1].strip()
                        
                        # Extract time estimate and type
                        time_estimate = None
                        task_type = None
                        
                        if '*(' in description and 'h)*' in description:
                            time_part = description.split('*(')[1].split('h)*')[0]
                            try:
                                time_estimate = float(time_part)
                            except ValueError:
                                pass
                        
                        if '`' in description:
                            type_parts = description.split('`')
                            if len(type_parts) >= 2:
                                task_type = type_parts[1]
                        
                        # Clean description
                        clean_desc = description
                        if '*(' in clean_desc:
                            clean_desc = clean_desc.split('*(')[0].strip()
                        if '`' in clean_desc:
                            clean_desc = clean_desc.split('`')[0].strip()
                        
                        pending_tasks.append({
                            "category": current_category,
                            "number": task_num,
                            "description": clean_desc,
                            "time_estimate": time_estimate,
                            "type": task_type
                        })
        
        return pending_tasks
    
    def get_agent_context(self, include_tasks: bool = True) -> str:
        """Compile full context for agent.
        
        Args:
            include_tasks: Whether to include detailed task information
            
        Returns:
            Formatted context string for agent
        """
        if not self.is_sdd_project():
            return ""
        
        context_parts = []
        
        # Add header
        context_parts.append("# 📋 SPECIFICATION-DRIVEN DEVELOPMENT CONTEXT")
        context_parts.append("")
        context_parts.append("This project follows Specification-Driven Development (SDD) methodology.")
        context_parts.append("All development decisions should align with the constitutional principles and specifications below.")
        context_parts.append("")
        
        # Load and add constitutional principles
        constitution = self.load_constitution()
        if constitution:
            context_parts.append("## 📜 CONSTITUTIONAL PRINCIPLES")
            context_parts.append("")
            context_parts.append("These foundational principles guide ALL project decisions:")
            context_parts.append("")
            # Extract key principles for summary
            principles = self._extract_key_principles(constitution)
            for principle in principles:
                context_parts.append(f"• {principle}")
            context_parts.append("")
            context_parts.append("⚖️ **CRITICAL**: All code changes must align with these constitutional principles.")
            context_parts.append("")
        
        # Load and add current specification
        spec = self.load_latest_specification()
        if spec:
            context_parts.append("## 📋 CURRENT SPECIFICATION")
            context_parts.append("")
            context_parts.append(f"**Title**: {spec['metadata'].get('title', 'Unknown')}")
            context_parts.append(f"**Created**: {spec['metadata'].get('created', 'Unknown')}")
            context_parts.append(f"**Status**: {spec['metadata'].get('status', 'Unknown')}")
            context_parts.append("")
            
            # Extract key requirements
            requirements = self._extract_requirements_summary(spec['content'])
            if requirements:
                context_parts.append("**Key Requirements:**")
                for req in requirements[:5]:  # Top 5 requirements
                    context_parts.append(f"• {req}")
                context_parts.append("")
        
        # Load and add implementation plan
        plan = self.load_active_plan()
        if plan:
            context_parts.append("## 🏗️ IMPLEMENTATION PLAN")
            context_parts.append("")
            phases = self._extract_plan_phases(plan['content'])
            if phases:
                context_parts.append("**Implementation Phases:**")
                for i, phase in enumerate(phases, 1):
                    context_parts.append(f"{i}. **{phase['name']}** - {phase.get('description', 'No description')}")
                context_parts.append("")
        
        # Load and add pending tasks
        if include_tasks:
            tasks = self.load_pending_tasks()
            if tasks and tasks['pending_tasks']:
                context_parts.append("## ✅ PENDING TASKS")
                context_parts.append("")
                context_parts.append(f"**Progress**: {tasks['total_tasks'] - len(tasks['pending_tasks'])}/{tasks['total_tasks']} tasks completed")
                context_parts.append("")
                
                # Group tasks by priority/category
                high_priority_tasks = [
                    t for t in tasks['pending_tasks']
                    if t.get('category') and 'foundation' in t['category'].lower()
                ]
                
                if high_priority_tasks:
                    context_parts.append("**Next High-Priority Tasks:**")
                    for task in high_priority_tasks[:3]:  # Top 3 high-priority
                        time_str = f" ({task['time_estimate']}h)" if task['time_estimate'] else ""
                        context_parts.append(f"• {task['description']}{time_str}")
                    context_parts.append("")
                
                # Show immediate next tasks
                next_tasks = tasks['pending_tasks'][:5]  # Next 5 tasks
                if next_tasks:
                    context_parts.append("**Immediate Next Tasks:**")
                    for task in next_tasks:
                        time_str = f" ({task['time_estimate']}h)" if task['time_estimate'] else ""
                        type_str = f" [{task['type']}]" if task['type'] else ""
                        context_parts.append(f"• {task['description']}{time_str}{type_str}")
                    context_parts.append("")
        
        # Add guidance for agent
        context_parts.append("## 🤖 GUIDANCE FOR AI ASSISTANT")
        context_parts.append("")
        context_parts.append("As an AI assistant working on this SDD project:")
        context_parts.append("")
        context_parts.append("1. **Constitutional Compliance**: Always validate suggestions against constitutional principles")
        context_parts.append("2. **Specification Alignment**: Ensure all implementations fulfill specification requirements")
        context_parts.append("3. **Task Focus**: Prioritize pending tasks, especially high-priority foundation work")
        context_parts.append("4. **Quality Standards**: Maintain high code quality as specified in constitution")
        context_parts.append("5. **Progress Tracking**: Help update task completion status as work progresses")
        context_parts.append("")
        context_parts.append("💡 **Tip**: Reference specific requirements and constitutional principles in your responses.")
        context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _extract_key_principles(self, constitution: str) -> List[str]:
        """Extract key principles from constitution.
        
        Args:
            constitution: Constitutional text
            
        Returns:
            List of key principles
        """
        principles = []
        
        # Look for bold principles or list items
        lines = constitution.split('\n')
        for line in lines:
            line = line.strip()
            
            # Bold text patterns
            if '**' in line and ':' in line:
                principle = line.split('**')[1].split('**')[0]
                if principle and len(principle) < 100:
                    principles.append(principle)
            
            # List items that look like principles
            elif line.startswith('- ') and ('must' in line.lower() or 'should' in line.lower()):
                principle = line[2:].strip()
                if len(principle) < 100:
                    principles.append(principle)
        
        # Fallback to common patterns
        if not principles:
            if 'quality' in constitution.lower():
                principles.append("Quality First - Prioritize code quality and testing")
            if 'security' in constitution.lower():
                principles.append("Security - Security considerations in all decisions")
            if 'user' in constitution.lower():
                principles.append("User-Centered - Focus on user needs and experience")
        
        return principles[:5]  # Top 5 principles
    
    def _extract_requirements_summary(self, spec_content: str) -> List[str]:
        """Extract key requirements from specification.
        
        Args:
            spec_content: Specification content
            
        Returns:
            List of key requirements
        """
        requirements = []
        current_section = None
        
        for line in spec_content.split('\n'):
            line = line.strip()
            
            # Detect requirements sections
            if line.startswith('## ') and 'requirement' in line.lower():
                current_section = 'requirements'
            elif line.startswith('## '):
                current_section = None
            
            # Extract requirements
            elif current_section == 'requirements' and line.startswith('- '):
                req = line[2:].strip()
                if req and req != "*No items specified*":
                    requirements.append(req)
        
        return requirements
    
    def _extract_plan_phases(self, plan_content: str) -> List[Dict[str, str]]:
        """Extract phases from plan content.
        
        Args:
            plan_content: Plan content
            
        Returns:
            List of phase dictionaries
        """
        phases = []
        current_phase = None
        
        for line in plan_content.split('\n'):
            line = line.strip()
            
            # Detect phase headers
            if line.startswith('### Phase '):
                if current_phase:
                    phases.append(current_phase)
                
                phase_name = line.split(': ', 1)[1] if ': ' in line else line[10:]
                current_phase = {"name": phase_name}
            
            # Extract phase description
            elif current_phase and line.startswith('**Description:**'):
                current_phase["description"] = line.split(':', 1)[1].strip()
        
        # Add the last phase
        if current_phase:
            phases.append(current_phase)
        
        return phases
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of available context.
        
        Returns:
            Dictionary with context availability and stats
        """
        summary = {
            "is_sdd_project": self.is_sdd_project(),
            "has_constitution": False,
            "has_specification": False,
            "has_plan": False,
            "has_tasks": False,
            "pending_task_count": 0,
            "total_task_count": 0
        }
        
        if summary["is_sdd_project"]:
            summary["has_constitution"] = self.load_constitution() is not None
            
            spec = self.load_latest_specification()
            summary["has_specification"] = spec is not None
            
            plan = self.load_active_plan()
            summary["has_plan"] = plan is not None
            
            tasks = self.load_pending_tasks()
            summary["has_tasks"] = tasks is not None
            if tasks:
                summary["pending_task_count"] = len(tasks['pending_tasks'])
                summary["total_task_count"] = tasks['total_tasks']
        
        return summary