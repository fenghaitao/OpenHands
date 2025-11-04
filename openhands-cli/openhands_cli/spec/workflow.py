"""Specification-Driven Development workflow management."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree

from .templates import TemplateManager
from .utils import StepTracker


class SpecWorkflow:
    """Manages the SDD workflow for OpenHands integration."""
    
    def __init__(self, project_dir: Path, console: Console):
        """Initialize workflow manager.
        
        Args:
            project_dir: Project directory path
            console: Rich console for output
        """
        self.project_dir = project_dir
        self.console = console
        self.specify_dir = project_dir / ".specify"
        self.template_manager = TemplateManager()
        
    def init_project(
        self, 
        project_name: Optional[str] = None,
        here: bool = False,
        ai_assistant: str = "openhands",
        script_type: str = "sh",
        skip_git: bool = False
    ) -> Path:
        """Initialize a new spec-driven project.
        
        Args:
            project_name: Name of the project directory
            here: Initialize in current directory
            ai_assistant: AI assistant to configure for
            script_type: Script type (sh or ps)
            skip_git: Skip git repository initialization
            
        Returns:
            Path to the initialized project
        """
        # Determine project path
        if here:
            project_path = self.project_dir
        else:
            project_path = self.project_dir / project_name
            project_path.mkdir(exist_ok=True)
        
        # Create progress tracker
        tracker = StepTracker("Initialize Specification-Driven Project")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Setting up project structure...", total=5)
            
            # Step 1: Create .specify directory structure
            tracker.add("structure", "Create .specify directory structure")
            self._create_specify_structure(project_path)
            tracker.complete("structure", "created")
            progress.advance(task)
            
            # Step 2: Copy templates
            tracker.add("templates", "Copy specification templates")
            self.template_manager.copy_templates(project_path, ai_assistant, script_type)
            tracker.complete("templates", f"{ai_assistant} templates")
            progress.advance(task)
            
            # Step 3: Copy memory files
            tracker.add("memory", "Copy knowledge base")
            self.template_manager.copy_memory(project_path)
            tracker.complete("memory", "knowledge base")
            progress.advance(task)
            
            # Step 4: Set up scripts
            tracker.add("scripts", "Set up automation scripts")
            self.template_manager.copy_scripts(project_path, script_type)
            tracker.complete("scripts", f"{script_type} scripts")
            progress.advance(task)
            
            # Step 5: Initialize git repository
            if not skip_git:
                tracker.add("git", "Initialize git repository")
                if self._init_git_repo(project_path):
                    tracker.complete("git", "initialized")
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")
            progress.advance(task)
        
        # Show final tree
        self.console.print()
        self.console.print(tracker.render())
        
        return project_path
    
    def check_tools(self) -> None:
        """Check availability of SDD tools."""
        tracker = StepTracker("Check Specification-Driven Development Tools")
        
        tools = {
            "git": "Git version control",
            "openhands": "OpenHands CLI",
            "python": "Python interpreter", 
            "code": "Visual Studio Code",
            "cursor": "Cursor IDE",
            "claude": "Claude CLI"
        }
        
        for tool_name, description in tools.items():
            tracker.add(tool_name, description)
            if self._check_tool(tool_name):
                tracker.complete(tool_name, "available")
            else:
                tracker.error(tool_name, "not found")
        
        self.console.print(tracker.render())
        self.console.print("\n[bold green]Tool check complete![/bold green]")
        
        # Show recommendations
        self._show_tool_recommendations()
    
    def create_constitution(self) -> None:
        """Create or update project constitution."""
        self.console.print("[bold]Creating project constitution...[/bold]\n")
        
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        
        if constitution_path.exists():
            self.console.print(f"[yellow]Constitution already exists at:[/yellow] {constitution_path}")
            self.console.print("[cyan]Use 'openhands spec constitution --edit' to modify it.[/cyan]")
        else:
            # Create constitutional template
            self.template_manager.create_constitution_template(constitution_path)
            self.console.print(f"[green]✓ Constitution template created:[/green] {constitution_path}")
            self.console.print("\n[cyan]Next steps:[/cyan]")
            self.console.print("1. Edit the constitution with your project principles")
            self.console.print("2. Run: [cyan]openhands spec specify[/cyan]")
    
    def edit_constitution(self) -> None:
        """Open constitution file in editor."""
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        
        if not constitution_path.exists():
            self.console.print("[red]Constitution not found. Run 'openhands spec constitution' first.[/red]")
            return
        
        # Try to open in editor
        editor = os.environ.get('EDITOR', 'code')
        try:
            subprocess.run([editor, str(constitution_path)], check=True)
            self.console.print(f"[green]✓ Opening constitution in {editor}[/green]")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.console.print(f"[yellow]Could not open {editor}. Constitution location:[/yellow]")
            self.console.print(f"[cyan]{constitution_path}[/cyan]")
    
    def create_specification(self, spec_name: Optional[str] = None) -> None:
        """Create a new specification."""
        from .processors import SpecificationProcessor
        
        # Check if .specify directory exists
        if not self.specify_dir.exists():
            self.console.print("[red]Error:[/red] No .specify directory found.")
            self.console.print("Run [cyan]openhands spec init[/cyan] first to initialize the project.")
            return
        
        # Initialize specification processor
        processor = SpecificationProcessor(self.console, self.project_dir)
        
        # Create specification interactively
        try:
            spec_path = processor.create_interactive_spec(spec_name)
            if spec_path:
                self.console.print(f"\n[green]Specification ready for review:[/green] {spec_path}")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Specification creation cancelled.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Error creating specification:[/red] {e}")
            import traceback
            traceback.print_exc()
    
    def create_plan(self, spec_name: Optional[str] = None) -> None:
        """Create implementation plan from specification."""
        self.console.print("[bold]Creating implementation plan...[/bold]\n")
        
        # Implementation placeholder
        self.console.print("[yellow]Plan creation will be implemented in Phase 2[/yellow]")
        self.console.print("[cyan]This will generate implementation strategy from specifications[/cyan]")
    
    def create_tasks(self, plan_name: Optional[str] = None) -> None:
        """Generate actionable tasks from plan."""
        self.console.print("[bold]Generating actionable tasks...[/bold]\n")
        
        # Implementation placeholder
        self.console.print("[yellow]Task generation will be implemented in Phase 2[/yellow]")
        self.console.print("[cyan]This will break down plans into specific development tasks[/cyan]")
    
    def clarify_specification(self, spec_name: Optional[str] = None) -> None:
        """Ask clarifying questions about specification."""
        self.console.print("[bold]Clarifying specification ambiguities...[/bold]\n")
        
        # Implementation placeholder
        self.console.print("[yellow]Clarification workflow will be implemented in Phase 4[/yellow]")
        self.console.print("[cyan]This will identify and resolve specification ambiguities[/cyan]")
    
    def analyze_consistency(self, verbose: bool = False) -> None:
        """Analyze consistency across artifacts."""
        self.console.print("[bold]Analyzing cross-artifact consistency...[/bold]\n")
        
        # Implementation placeholder
        self.console.print("[yellow]Consistency analysis will be implemented in Phase 4[/yellow]")
        self.console.print("[cyan]This will check alignment between specs, plans, and tasks[/cyan]")
    
    def _create_specify_structure(self, project_path: Path) -> None:
        """Create .specify directory structure."""
        specify_dir = project_path / ".specify"
        
        # Create main directories
        directories = [
            specify_dir,
            specify_dir / "memory",
            specify_dir / "templates", 
            specify_dir / "scripts",
            project_path / "specs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _init_git_repo(self, project_path: Path) -> bool:
        """Initialize git repository if git is available."""
        if not self._check_tool("git"):
            return False
        
        try:
            # Check if already a git repo
            if (project_path / ".git").exists():
                return True
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"], 
                cwd=project_path, 
                check=True, 
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is available in PATH."""
        return shutil.which(tool_name) is not None
    
    def _show_tool_recommendations(self) -> None:
        """Show tool installation recommendations."""
        recommendations = [
            "For the best experience, consider installing:",
            "• [cyan]git[/cyan] - Version control for your specifications",
            "• [cyan]code[/cyan] or [cyan]cursor[/cyan] - IDE for editing specifications",
            "• [cyan]claude[/cyan] - Additional AI assistant option"
        ]
        
        panel = Panel(
            "\n".join(recommendations),
            title="[bold]Recommendations[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)