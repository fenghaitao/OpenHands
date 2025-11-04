"""Task generation for SDD workflow."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table


class TaskGenerator:
    """Generates actionable tasks from implementation plans."""
    
    def __init__(self, console: Console, project_dir: Path):
        """Initialize task generator.
        
        Args:
            console: Rich console for output
            project_dir: Project directory path
        """
        self.console = console
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.specs_dir = project_dir / "specs"
    
    def generate_tasks(self, plan_name: Optional[str] = None) -> Optional[Path]:
        """Generate actionable tasks from implementation plan.
        
        Args:
            plan_name: Name of plan to create tasks for
            
        Returns:
            Path to generated tasks file, or None if cancelled
        """
        self.console.print("\n[bold cyan]Generating Actionable Tasks[/bold cyan]")
        self.console.print("[dim]Breaking down implementation plan into specific development tasks.[/dim]\n")
        
        # Load implementation plan
        plan_data = self._load_plan(plan_name)
        if not plan_data:
            return None
        
        # Load constitutional context for prioritization
        constitution = self._load_constitution()
        
        # Generate task structure
        tasks_data = self._generate_tasks_content(plan_data, constitution)
        
        # Create tasks document
        tasks_path = self._create_tasks_document(tasks_data, plan_data["metadata"]["name"])
        
        # Show completion message
        self._show_tasks_summary(tasks_path, tasks_data)
        
        return tasks_path
    
    def _load_plan(self, plan_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load implementation plan data.
        
        Args:
            plan_name: Plan name, or None to use latest
            
        Returns:
            Plan data or None if not found
        """
        if plan_name:
            plan_path = self.specs_dir / f"{plan_name}.md"
            metadata_path = self.specs_dir / f"{plan_name}.json"
        else:
            # Find latest plan
            plan_files = list(self.specs_dir.glob("plan_*.json"))
            if not plan_files:
                self.console.print("[red]No implementation plans found. Run 'openhands spec plan' first.[/red]")
                return None
            
            # Sort by creation time (latest first)
            plan_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            metadata_path = plan_files[0]
            plan_name = metadata_path.stem
            plan_path = self.specs_dir / f"{plan_name}.md"
        
        if not plan_path.exists() or not metadata_path.exists():
            self.console.print(f"[red]Implementation plan '{plan_name}' not found.[/red]")
            return None
        
        # Load metadata
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        
        # Parse plan content
        plan_content = plan_path.read_text(encoding='utf-8')
        plan_data = self._parse_plan_content(plan_content, metadata)
        
        self.console.print(f"[green]✓ Loaded implementation plan: {metadata['title']}[/green]")
        return plan_data
    
    def _load_constitution(self) -> Optional[str]:
        """Load project constitution."""
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        if constitution_path.exists():
            return constitution_path.read_text(encoding='utf-8')
        return None
    
    def _parse_plan_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Parse plan content into structured data.
        
        Args:
            content: Plan markdown content
            metadata: Plan metadata
            
        Returns:
            Parsed plan data
        """
        plan_data = {
            "metadata": metadata,
            "title": metadata.get("title", ""),
            "phases": [],
            "technical_decisions": [],
            "risks": []
        }
        
        # Simple parsing to extract phases and their tasks
        current_phase = None
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Detect phase sections
            if line.startswith('### Phase '):
                if current_phase:
                    plan_data["phases"].append(current_phase)
                
                phase_name = line.split(': ', 1)[1] if ': ' in line else line[10:]
                current_phase = {
                    "name": phase_name,
                    "tasks": [],
                    "deliverables": []
                }
                current_section = None
            
            # Detect subsections within phases
            elif line == "**Tasks:**":
                current_section = "tasks"
            elif line == "**Deliverables:**":
                current_section = "deliverables"
            elif line.startswith("**Duration:**"):
                if current_phase:
                    current_phase["duration"] = line.split(":", 1)[1].strip()
            elif line.startswith("**Description:**"):
                if current_phase:
                    current_phase["description"] = line.split(":", 1)[1].strip()
            
            # Extract list items
            elif current_phase and current_section and line.startswith('- '):
                item = line[2:].strip()
                if item and current_section in current_phase:
                    current_phase[current_section].append(item)
        
        # Add the last phase
        if current_phase:
            plan_data["phases"].append(current_phase)
        
        return plan_data
    
    def _generate_tasks_content(self, plan_data: Dict[str, Any], constitution: Optional[str]) -> Dict[str, Any]:
        """Generate task structure from plan data.
        
        Args:
            plan_data: Implementation plan data
            constitution: Constitutional principles
            
        Returns:
            Tasks data structure
        """
        tasks_data = {
            "title": f"Development Tasks: {plan_data['title'].replace('Implementation Plan: ', '')}",
            "plan_reference": plan_data["metadata"]["name"],
            "created": datetime.now().isoformat(),
            "task_categories": [],
            "constitutional_priorities": self._extract_constitutional_priorities(constitution) if constitution else [],
            "total_tasks": 0
        }
        
        # Process each phase into task categories
        for phase in plan_data.get("phases", []):
            category = self._process_phase_to_tasks(phase, constitution)
            tasks_data["task_categories"].append(category)
            tasks_data["total_tasks"] += len(category["tasks"])
        
        # Add cross-cutting concerns as additional task category
        cross_cutting = self._generate_cross_cutting_tasks(constitution)
        if cross_cutting["tasks"]:
            tasks_data["task_categories"].append(cross_cutting)
            tasks_data["total_tasks"] += len(cross_cutting["tasks"])
        
        return tasks_data
    
    def _extract_constitutional_priorities(self, constitution: str) -> List[str]:
        """Extract priority guidelines from constitution.
        
        Args:
            constitution: Constitutional text
            
        Returns:
            List of priority guidelines
        """
        priorities = []
        
        # Look for decision framework or priority sections
        if "decision framework" in constitution.lower():
            priorities.append("Follow constitutional decision framework")
        
        if "quality" in constitution.lower():
            priorities.append("Prioritize code quality and testing")
        
        if "security" in constitution.lower():
            priorities.append("Security considerations in all tasks")
        
        if "user" in constitution.lower():
            priorities.append("User-centered approach to all features")
        
        return priorities or ["Follow project principles", "Maintain high quality standards"]
    
    def _process_phase_to_tasks(self, phase: Dict[str, Any], constitution: Optional[str]) -> Dict[str, Any]:
        """Process a phase into detailed tasks.
        
        Args:
            phase: Phase data from plan
            constitution: Constitutional principles
            
        Returns:
            Task category data
        """
        category = {
            "name": phase["name"],
            "description": phase.get("description", ""),
            "duration": phase.get("duration", ""),
            "tasks": [],
            "priority": self._determine_phase_priority(phase, constitution)
        }
        
        # Convert high-level tasks to specific actionable tasks
        for task in phase.get("tasks", []):
            detailed_tasks = self._break_down_task(task, constitution)
            category["tasks"].extend(detailed_tasks)
        
        return category
    
    def _determine_phase_priority(self, phase: Dict[str, Any], constitution: Optional[str]) -> str:
        """Determine phase priority based on constitutional principles.
        
        Args:
            phase: Phase data
            constitution: Constitutional principles
            
        Returns:
            Priority level (High/Medium/Low)
        """
        phase_name = phase["name"].lower()
        
        # Foundation phase is always high priority
        if "foundation" in phase_name:
            return "High"
        
        # Security and testing phases get high priority if constitution emphasizes them
        if constitution:
            if ("security" in phase_name or "test" in phase_name) and "security" in constitution.lower():
                return "High"
            if "quality" in constitution.lower() and ("test" in phase_name or "quality" in phase_name):
                return "High"
        
        # Core features are typically high priority
        if "core" in phase_name:
            return "High"
        
        # Polish and enhancement phases are medium/low priority
        if "polish" in phase_name or "enhancement" in phase_name:
            return "Medium"
        
        return "Medium"
    
    def _break_down_task(self, high_level_task: str, constitution: Optional[str]) -> List[Dict[str, Any]]:
        """Break down high-level task into specific actionable tasks.
        
        Args:
            high_level_task: High-level task description
            constitution: Constitutional principles
            
        Returns:
            List of detailed task dictionaries
        """
        tasks = []
        task_lower = high_level_task.lower()
        
        # Task breakdown patterns
        if "set up development environment" in task_lower:
            tasks.extend([
                {"description": "Install required development tools", "type": "setup", "estimated_hours": 2},
                {"description": "Configure IDE/editor with project settings", "type": "setup", "estimated_hours": 1},
                {"description": "Set up virtual environment", "type": "setup", "estimated_hours": 1},
                {"description": "Install project dependencies", "type": "setup", "estimated_hours": 1}
            ])
        
        elif "initialize project structure" in task_lower:
            tasks.extend([
                {"description": "Create project directory structure", "type": "setup", "estimated_hours": 1},
                {"description": "Set up configuration files", "type": "setup", "estimated_hours": 2},
                {"description": "Create initial documentation", "type": "documentation", "estimated_hours": 2}
            ])
        
        elif "configure version control" in task_lower:
            tasks.extend([
                {"description": "Initialize git repository", "type": "setup", "estimated_hours": 0.5},
                {"description": "Create .gitignore file", "type": "setup", "estimated_hours": 0.5},
                {"description": "Set up branch protection rules", "type": "setup", "estimated_hours": 1},
                {"description": "Configure commit hooks", "type": "setup", "estimated_hours": 1}
            ])
        
        elif "implement" in task_lower:
            # Extract what to implement
            feature = high_level_task.replace("Implement: ", "").replace("Implement ", "")
            tasks.extend([
                {"description": f"Design {feature} architecture", "type": "design", "estimated_hours": 4},
                {"description": f"Implement {feature} core logic", "type": "development", "estimated_hours": 8},
                {"description": f"Write unit tests for {feature}", "type": "testing", "estimated_hours": 4},
                {"description": f"Create {feature} documentation", "type": "documentation", "estimated_hours": 2}
            ])
        
        elif "testing" in task_lower:
            tasks.extend([
                {"description": "Set up testing framework", "type": "setup", "estimated_hours": 2},
                {"description": "Write unit tests", "type": "testing", "estimated_hours": 8},
                {"description": "Write integration tests", "type": "testing", "estimated_hours": 6},
                {"description": "Set up test coverage reporting", "type": "testing", "estimated_hours": 2}
            ])
        
        elif "security" in task_lower:
            tasks.extend([
                {"description": "Conduct security assessment", "type": "security", "estimated_hours": 4},
                {"description": "Implement security best practices", "type": "security", "estimated_hours": 6},
                {"description": "Set up security monitoring", "type": "security", "estimated_hours": 3}
            ])
        
        else:
            # Generic task breakdown
            tasks.append({
                "description": high_level_task,
                "type": "development",
                "estimated_hours": 4
            })
        
        # Add constitutional requirements to each task
        if constitution:
            for task in tasks:
                if "security" in constitution.lower() and task["type"] == "development":
                    task["security_requirements"] = "Follow security guidelines"
                if "quality" in constitution.lower():
                    task["quality_requirements"] = "Meet code quality standards"
        
        return tasks
    
    def _generate_cross_cutting_tasks(self, constitution: Optional[str]) -> Dict[str, Any]:
        """Generate cross-cutting concern tasks.
        
        Args:
            constitution: Constitutional principles
            
        Returns:
            Cross-cutting task category
        """
        category = {
            "name": "Cross-Cutting Concerns",
            "description": "Tasks that span across multiple phases",
            "duration": "Ongoing",
            "tasks": [],
            "priority": "High"
        }
        
        # Always include basic cross-cutting concerns
        base_tasks = [
            {"description": "Maintain code quality standards", "type": "quality", "estimated_hours": 2},
            {"description": "Keep documentation updated", "type": "documentation", "estimated_hours": 2},
            {"description": "Regular code reviews", "type": "quality", "estimated_hours": 4}
        ]
        
        # Add constitutional requirements
        if constitution:
            if "security" in constitution.lower():
                base_tasks.extend([
                    {"description": "Regular security reviews", "type": "security", "estimated_hours": 3},
                    {"description": "Security testing throughout development", "type": "security", "estimated_hours": 4}
                ])
            
            if "testing" in constitution.lower() or "quality" in constitution.lower():
                base_tasks.extend([
                    {"description": "Maintain test coverage above 90%", "type": "testing", "estimated_hours": 6},
                    {"description": "Regular refactoring sessions", "type": "quality", "estimated_hours": 4}
                ])
        
        category["tasks"] = base_tasks
        return category
    
    def _create_tasks_document(self, tasks_data: Dict[str, Any], plan_name: str) -> Path:
        """Create tasks document.
        
        Args:
            tasks_data: Tasks data structure
            plan_name: Source plan name
            
        Returns:
            Path to created tasks document
        """
        # Create tasks filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tasks_filename = f"tasks_{plan_name}_{timestamp}.md"
        tasks_path = self.specs_dir / tasks_filename
        
        # Generate tasks content
        content = self._render_tasks_template(tasks_data)
        
        # Write tasks file
        tasks_path.write_text(content, encoding='utf-8')
        
        # Create metadata file
        metadata = {
            "name": tasks_filename.replace('.md', ''),
            "title": tasks_data["title"],
            "plan_reference": tasks_data["plan_reference"],
            "created": tasks_data["created"],
            "type": "task_list",
            "total_tasks": tasks_data["total_tasks"],
            "version": "1.0"
        }
        
        metadata_path = self.specs_dir / f"{metadata['name']}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        return tasks_path
    
    def _render_tasks_template(self, tasks_data: Dict[str, Any]) -> str:
        """Render tasks template with data.
        
        Args:
            tasks_data: Tasks data structure
            
        Returns:
            Rendered tasks content
        """
        content = f"""---
title: "{tasks_data['title']}"
plan_reference: "{tasks_data['plan_reference']}"
created: "{tasks_data['created']}"
type: "task_list"
total_tasks: {tasks_data['total_tasks']}
version: "1.0"
---

# {tasks_data['title']}

## Overview
This document contains {tasks_data['total_tasks']} actionable development tasks broken down from the implementation plan.

## Constitutional Priorities
{self._format_list(tasks_data['constitutional_priorities'])}

## Task Categories

{self._format_task_categories(tasks_data['task_categories'])}

## Summary by Type
{self._generate_task_summary(tasks_data['task_categories'])}

---
*This task list was generated from plan: {tasks_data['plan_reference']}*
"""
        return content
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for markdown."""
        if not items:
            return "*No items specified*"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_task_categories(self, categories: List[Dict[str, Any]]) -> str:
        """Format task categories for markdown."""
        content = []
        
        for category in categories:
            content.append(f"### {category['name']}")
            content.append(f"**Priority:** {category['priority']}")
            if category.get("duration"):
                content.append(f"**Duration:** {category['duration']}")
            if category.get("description"):
                content.append(f"**Description:** {category['description']}")
            content.append("")
            
            # Format tasks as checklist
            for i, task in enumerate(category['tasks'], 1):
                task_line = f"- [ ] **{i}.** {task['description']}"
                if task.get("estimated_hours"):
                    task_line += f" *({task['estimated_hours']}h)*"
                if task.get("type"):
                    task_line += f" `{task['type']}`"
                content.append(task_line)
            
            content.append("")
        
        return "\n".join(content)
    
    def _generate_task_summary(self, categories: List[Dict[str, Any]]) -> str:
        """Generate task summary by type."""
        type_counts = {}
        total_hours = 0
        
        for category in categories:
            for task in category['tasks']:
                task_type = task.get('type', 'other')
                type_counts[task_type] = type_counts.get(task_type, 0) + 1
                total_hours += task.get('estimated_hours', 0)
        
        content = []
        for task_type, count in sorted(type_counts.items()):
            content.append(f"- **{task_type.title()}:** {count} tasks")
        
        content.append(f"- **Total Estimated Hours:** {total_hours}")
        
        return "\n".join(content)
    
    def _show_tasks_summary(self, tasks_path: Path, tasks_data: Dict[str, Any]) -> None:
        """Show summary of created tasks."""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]✓ Development Tasks Generated Successfully![/bold green]")
        self.console.print("="*60)
        
        self.console.print(f"[cyan]Title:[/cyan] {tasks_data['title']}")
        self.console.print(f"[cyan]Location:[/cyan] {tasks_path}")
        self.console.print(f"[cyan]Total Tasks:[/cyan] {tasks_data['total_tasks']}")
        self.console.print(f"[cyan]Task Categories:[/cyan] {len(tasks_data['task_categories'])}")
        
        # Show task breakdown
        table = Table(title="Task Breakdown")
        table.add_column("Category", style="cyan")
        table.add_column("Tasks", justify="right")
        table.add_column("Priority", style="yellow")
        
        for category in tasks_data['task_categories']:
            table.add_row(
                category['name'],
                str(len(category['tasks'])),
                category['priority']
            )
        
        self.console.print()
        self.console.print(table)
        
        # Show next steps
        panel = Panel(
            "1. Review the generated task list\n"
            "2. Prioritize tasks based on constitutional principles\n"
            "3. Begin implementation following the task order\n"
            "4. Track progress by checking off completed tasks\n"
            "5. Start development: [cyan]openhands[/cyan]",
            title="[bold]Next Steps[/bold]",
            border_style="green"
        )
        
        self.console.print()
        self.console.print(panel)