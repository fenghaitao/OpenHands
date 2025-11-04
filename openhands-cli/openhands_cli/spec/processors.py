"""Specification processing and creation for SDD workflow."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.text import Text

from .validators import SpecificationValidator, ConstitutionValidator


class SpecificationProcessor:
    """Processes specification creation with interactive guidance."""
    
    def __init__(self, console: Console, project_dir: Path):
        """Initialize specification processor.
        
        Args:
            console: Rich console for output
            project_dir: Project directory path
        """
        self.console = console
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.validator = SpecificationValidator(console)
        self.constitution_validator = ConstitutionValidator(console)
    
    def create_interactive_spec(self, spec_name: Optional[str] = None) -> Path:
        """Create specification through interactive dialog.
        
        Args:
            spec_name: Optional name for the specification
            
        Returns:
            Path to the created specification file
        """
        self.console.print("\n[bold cyan]Creating Project Specification[/bold cyan]")
        self.console.print("[dim]This interactive process will guide you through creating a comprehensive specification.[/dim]\n")
        
        # Load constitutional context
        constitution = self._load_constitution()
        if constitution:
            self.console.print("[green]✓ Constitutional principles loaded[/green]")
        else:
            self.console.print("[yellow]⚠ No constitution found - consider running 'openhands spec constitution' first[/yellow]")
        
        # Generate spec name if not provided
        if not spec_name:
            spec_name = self._generate_spec_name()
        
        # Gather specification content through interactive dialog
        spec_data = self._interactive_specification_dialog(constitution)
        
        # Validate against constitutional principles
        if constitution:
            validation_results = self.constitution_validator.validate_against_constitution(
                spec_data, constitution
            )
            if not self._handle_validation_results(validation_results):
                self.console.print("[red]Specification creation cancelled due to constitutional conflicts.[/red]")
                return None
        
        # Generate specification document
        spec_path = self._generate_specification_document(spec_name, spec_data)
        
        # Show completion message
        self._show_specification_summary(spec_path, spec_data)
        
        return spec_path
    
    def _load_constitution(self) -> Optional[str]:
        """Load project constitution if it exists."""
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        if constitution_path.exists():
            return constitution_path.read_text(encoding='utf-8')
        return None
    
    def _generate_spec_name(self) -> str:
        """Generate a unique specification name."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try to get a descriptive name from user
        project_name = Prompt.ask(
            "\n[cyan]What would you like to call this specification?[/cyan]",
            default=f"spec_{timestamp}"
        )
        
        # Sanitize the name
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', project_name.lower())
        return sanitized
    
    def _interactive_specification_dialog(self, constitution: Optional[str]) -> Dict[str, Any]:
        """Guide user through specification creation dialog."""
        spec_data = {
            "title": "",
            "overview": "",
            "functional_requirements": [],
            "non_functional_requirements": [],
            "user_stories": [],
            "technical_specifications": {},
            "success_metrics": [],
            "dependencies": [],
            "assumptions": [],
            "open_questions": [],
            "constitutional_alignment": {}
        }
        
        # Project Overview
        self.console.print("\n" + "="*60)
        self.console.print("[bold]1. Project Overview[/bold]")
        self.console.print("="*60)
        
        spec_data["title"] = Prompt.ask(
            "[cyan]Project Title[/cyan]",
            default="My Project"
        )
        
        spec_data["overview"] = self._get_multiline_input(
            "\n[cyan]Project Overview[/cyan] (describe the project's purpose and goals):"
        )
        
        # Functional Requirements
        self.console.print("\n" + "="*60)
        self.console.print("[bold]2. Functional Requirements[/bold]")
        self.console.print("="*60)
        self.console.print("[dim]What must the system DO? (features, capabilities, behaviors)[/dim]\n")
        
        spec_data["functional_requirements"] = self._collect_list_items(
            "functional requirement",
            "Enter a functional requirement (or press Enter to finish):"
        )
        
        # Non-Functional Requirements
        self.console.print("\n" + "="*60)
        self.console.print("[bold]3. Non-Functional Requirements[/bold]")
        self.console.print("="*60)
        self.console.print("[dim]How should the system behave? (performance, security, usability, etc.)[/dim]\n")
        
        spec_data["non_functional_requirements"] = self._collect_list_items(
            "non-functional requirement",
            "Enter a non-functional requirement (or press Enter to finish):"
        )
        
        # User Stories
        self.console.print("\n" + "="*60)
        self.console.print("[bold]4. User Stories[/bold]")
        self.console.print("="*60)
        self.console.print("[dim]From the user's perspective: 'As a [user], I want [goal] so that [benefit]'[/dim]\n")
        
        spec_data["user_stories"] = self._collect_list_items(
            "user story",
            "Enter a user story (or press Enter to finish):"
        )
        
        # Technical Specifications
        self.console.print("\n" + "="*60)
        self.console.print("[bold]5. Technical Specifications[/bold]")
        self.console.print("="*60)
        
        if Confirm.ask("[cyan]Would you like to specify technical details?[/cyan]", default=True):
            spec_data["technical_specifications"] = self._collect_technical_specs()
        
        # Success Metrics
        self.console.print("\n" + "="*60)
        self.console.print("[bold]6. Success Metrics[/bold]")
        self.console.print("="*60)
        self.console.print("[dim]How will you measure project success?[/dim]\n")
        
        spec_data["success_metrics"] = self._collect_list_items(
            "success metric",
            "Enter a success metric (or press Enter to finish):"
        )
        
        # Dependencies and Assumptions
        if Confirm.ask("\n[cyan]Would you like to specify dependencies and assumptions?[/cyan]", default=True):
            spec_data["dependencies"] = self._collect_list_items(
                "dependency",
                "Enter a dependency (external system, library, service):"
            )
            
            spec_data["assumptions"] = self._collect_list_items(
                "assumption",
                "Enter an assumption (what are you assuming to be true?):"
            )
        
        # Open Questions
        if Confirm.ask("\n[cyan]Are there any open questions or areas needing clarification?[/cyan]", default=False):
            spec_data["open_questions"] = self._collect_list_items(
                "open question",
                "Enter an open question (or press Enter to finish):"
            )
        
        return spec_data
    
    def _get_multiline_input(self, prompt_text: str) -> str:
        """Get multiline input from user."""
        self.console.print(prompt_text)
        self.console.print("[dim]Type your response. Press Enter twice when finished.[/dim]")
        
        lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input("  ")
                if not line.strip():
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        
        return "\n".join(lines).strip()
    
    def _collect_list_items(self, item_type: str, prompt_text: str) -> List[str]:
        """Collect a list of items from user input."""
        items = []
        
        while True:
            item = Prompt.ask(f"  {prompt_text}", default="").strip()
            if not item:
                break
            items.append(item)
            self.console.print(f"    [green]✓ Added {item_type}: {item}[/green]")
        
        if items:
            self.console.print(f"\n[green]Collected {len(items)} {item_type}(s)[/green]")
        
        return items
    
    def _collect_technical_specs(self) -> Dict[str, Any]:
        """Collect technical specification details."""
        tech_specs = {}
        
        # Programming languages
        if Confirm.ask("[cyan]Specify programming languages?[/cyan]", default=True):
            tech_specs["languages"] = self._collect_list_items(
                "programming language",
                "Enter a programming language:"
            )
        
        # Frameworks and libraries
        if Confirm.ask("[cyan]Specify frameworks/libraries?[/cyan]", default=True):
            tech_specs["frameworks"] = self._collect_list_items(
                "framework/library",
                "Enter a framework or library:"
            )
        
        # Architecture
        architecture = Prompt.ask(
            "[cyan]System architecture (e.g., monolith, microservices, serverless)[/cyan]",
            default=""
        )
        if architecture:
            tech_specs["architecture"] = architecture
        
        # Database
        database = Prompt.ask(
            "[cyan]Database technology (e.g., PostgreSQL, MongoDB, Redis)[/cyan]",
            default=""
        )
        if database:
            tech_specs["database"] = database
        
        # Deployment
        deployment = Prompt.ask(
            "[cyan]Deployment platform (e.g., AWS, Docker, Kubernetes)[/cyan]",
            default=""
        )
        if deployment:
            tech_specs["deployment"] = deployment
        
        return tech_specs
    
    def _handle_validation_results(self, validation_results: Dict[str, Any]) -> bool:
        """Handle constitutional validation results.
        
        Returns:
            True if user wants to proceed, False to cancel
        """
        if validation_results["is_valid"]:
            self.console.print("[green]✓ Specification aligns with constitutional principles[/green]")
            return True
        
        # Show violations
        self.console.print("\n[yellow]⚠ Constitutional Alignment Issues Found:[/yellow]")
        for violation in validation_results["violations"]:
            self.console.print(f"  • {violation}")
        
        # Show suggestions
        if validation_results["suggestions"]:
            self.console.print("\n[cyan]Suggestions for improvement:[/cyan]")
            for suggestion in validation_results["suggestions"]:
                self.console.print(f"  • {suggestion}")
        
        # Ask user how to proceed
        self.console.print("\n[yellow]How would you like to proceed?[/yellow]")
        self.console.print("1. Revise specification to address issues")
        self.console.print("2. Continue anyway (not recommended)")
        self.console.print("3. Cancel specification creation")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3"], default="1")
        
        if choice == "1":
            self.console.print("[cyan]Please revise your specification to address the constitutional issues.[/cyan]")
            return False  # For now, return False - in full implementation, would loop back
        elif choice == "2":
            return Confirm.ask("[yellow]Are you sure you want to proceed despite constitutional conflicts?[/yellow]")
        else:
            return False
    
    def _generate_specification_document(self, spec_name: str, spec_data: Dict[str, Any]) -> Path:
        """Generate the specification document.
        
        Args:
            spec_name: Name for the specification
            spec_data: Collected specification data
            
        Returns:
            Path to the generated specification file
        """
        # Create specs directory if it doesn't exist
        specs_dir = self.project_dir / "specs"
        specs_dir.mkdir(exist_ok=True)
        
        # Generate timestamp and metadata
        timestamp = datetime.now().isoformat()
        
        # Load template
        template_path = self.specify_dir / "templates" / "spec-template.md"
        if template_path.exists():
            template_content = template_path.read_text(encoding='utf-8')
        else:
            template_content = self._get_default_spec_template()
        
        # Replace template placeholders
        spec_content = self._render_specification_template(template_content, spec_data, timestamp)
        
        # Write specification file
        spec_filename = f"{spec_name}.md"
        spec_path = specs_dir / spec_filename
        spec_path.write_text(spec_content, encoding='utf-8')
        
        # Create metadata file
        metadata = {
            "name": spec_name,
            "title": spec_data["title"],
            "created": timestamp,
            "version": "1.0",
            "status": "draft"
        }
        
        metadata_path = specs_dir / f"{spec_name}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        return spec_path
    
    def _render_specification_template(self, template: str, spec_data: Dict[str, Any], timestamp: str) -> str:
        """Render specification template with collected data."""
        content = template
        
        # Replace basic placeholders
        content = content.replace("{{ date }}", timestamp)
        content = content.replace("{{ title }}", spec_data["title"])
        
        # Replace sections
        content = self._replace_section(content, "OVERVIEW", spec_data["overview"])
        content = self._replace_list_section(content, "FUNCTIONAL_REQUIREMENTS", spec_data["functional_requirements"])
        content = self._replace_list_section(content, "NON_FUNCTIONAL_REQUIREMENTS", spec_data["non_functional_requirements"])
        content = self._replace_list_section(content, "USER_STORIES", spec_data["user_stories"])
        content = self._replace_list_section(content, "SUCCESS_METRICS", spec_data["success_metrics"])
        content = self._replace_list_section(content, "DEPENDENCIES", spec_data["dependencies"])
        content = self._replace_list_section(content, "ASSUMPTIONS", spec_data["assumptions"])
        content = self._replace_list_section(content, "OPEN_QUESTIONS", spec_data["open_questions"])
        
        # Replace technical specifications
        if spec_data["technical_specifications"]:
            tech_content = self._format_technical_specifications(spec_data["technical_specifications"])
            content = self._replace_section(content, "TECHNICAL_SPECIFICATIONS", tech_content)
        
        return content
    
    def _replace_section(self, content: str, section_name: str, section_content: str) -> str:
        """Replace a template section with actual content."""
        placeholder = f"{{{{ {section_name} }}}}"
        if placeholder in content:
            return content.replace(placeholder, section_content)
        return content
    
    def _replace_list_section(self, content: str, section_name: str, items: List[str]) -> str:
        """Replace a template list section with formatted items."""
        if not items:
            formatted_items = "*No items specified*"
        else:
            formatted_items = "\n".join(f"- {item}" for item in items)
        
        return self._replace_section(content, section_name, formatted_items)
    
    def _format_technical_specifications(self, tech_specs: Dict[str, Any]) -> str:
        """Format technical specifications for the document."""
        lines = []
        
        for key, value in tech_specs.items():
            if isinstance(value, list):
                if value:
                    lines.append(f"**{key.title()}:** {', '.join(value)}")
            elif value:
                lines.append(f"**{key.title()}:** {value}")
        
        return "\n".join(lines) if lines else "*No technical specifications provided*"
    
    def _get_default_spec_template(self) -> str:
        """Get default specification template if none exists."""
        return '''---
title: "{{ title }}"
created: "{{ date }}"
version: "1.0"
status: "draft"
---

# {{ title }}

## Overview
{{ OVERVIEW }}

## Functional Requirements
{{ FUNCTIONAL_REQUIREMENTS }}

## Non-Functional Requirements
{{ NON_FUNCTIONAL_REQUIREMENTS }}

## User Stories
{{ USER_STORIES }}

## Technical Specifications
{{ TECHNICAL_SPECIFICATIONS }}

## Success Metrics
{{ SUCCESS_METRICS }}

## Dependencies
{{ DEPENDENCIES }}

## Assumptions
{{ ASSUMPTIONS }}

## Open Questions
{{ OPEN_QUESTIONS }}
'''
    
    def _show_specification_summary(self, spec_path: Path, spec_data: Dict[str, Any]) -> None:
        """Show summary of created specification."""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]✓ Specification Created Successfully![/bold green]")
        self.console.print("="*60)
        
        self.console.print(f"[cyan]Title:[/cyan] {spec_data['title']}")
        self.console.print(f"[cyan]Location:[/cyan] {spec_path}")
        self.console.print(f"[cyan]Functional Requirements:[/cyan] {len(spec_data['functional_requirements'])}")
        self.console.print(f"[cyan]Non-Functional Requirements:[/cyan] {len(spec_data['non_functional_requirements'])}")
        self.console.print(f"[cyan]User Stories:[/cyan] {len(spec_data['user_stories'])}")
        
        # Show next steps
        panel = Panel(
            "1. Review the generated specification\n"
            "2. Run: [cyan]openhands spec plan[/cyan] to create implementation plan\n"
            "3. Run: [cyan]openhands spec tasks[/cyan] to generate actionable tasks\n"
            "4. Start development: [cyan]openhands[/cyan]",
            title="[bold]Next Steps[/bold]",
            border_style="green"
        )
        
        self.console.print()
        self.console.print(panel)