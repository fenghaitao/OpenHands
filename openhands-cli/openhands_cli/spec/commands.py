"""Core spec-kit command implementations for OpenHands CLI."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from .workflow import SpecWorkflow
from .utils import setup_console, show_spec_banner


def handle_spec_command(args: argparse.Namespace) -> None:
    """Handle spec subcommands.
    
    Args:
        args: Parsed command line arguments
    """
    console = setup_console()
    
    try:
        # Determine project directory
        project_dir = Path(args.project_dir) if hasattr(args, 'project_dir') and args.project_dir else Path.cwd()
        
        # Initialize workflow manager
        workflow = SpecWorkflow(project_dir, console)
        
        # Route to appropriate command handler
        if args.spec_command == 'init':
            _handle_init(args, workflow)
        elif args.spec_command == 'check':
            _handle_check(args, workflow)
        elif args.spec_command == 'constitution':
            _handle_constitution(args, workflow)
        elif args.spec_command == 'specify':
            _handle_specify(args, workflow)
        elif args.spec_command == 'plan':
            _handle_plan(args, workflow)
        elif args.spec_command == 'tasks':
            _handle_tasks(args, workflow)
        elif args.spec_command == 'clarify':
            _handle_clarify(args, workflow)
        elif args.spec_command == 'analyze':
            _handle_analyze(args, workflow)
        else:
            show_spec_banner(console)
            console.print("[yellow]No spec command specified. Use --help for available commands.[/yellow]")
            
    except KeyboardInterrupt:
        print_formatted_text(HTML('\n<yellow>Operation cancelled by user 👋</yellow>'))
    except Exception as e:
        print_formatted_text(HTML(f'<red>Error: {e}</red>'))
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _handle_init(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec init command."""
    console = workflow.console
    show_spec_banner(console)
    
    console.print("[bold]Initializing Specification-Driven Development project...[/bold]\n")
    
    # Determine project settings
    project_name = getattr(args, 'project_name', None)
    here = getattr(args, 'here', False)
    ai_assistant = getattr(args, 'ai', 'openhands')
    script_type = getattr(args, 'script_type', 'sh')
    no_git = getattr(args, 'no_git', False)
    
    # Validate project name/location
    if not project_name and not here:
        console.print("[red]Error:[/red] Project name required or use --here flag")
        sys.exit(1)
    
    if project_name == '.':
        here = True
        project_name = None
    
    # Initialize project
    try:
        project_path = workflow.init_project(
            project_name=project_name,
            here=here,
            ai_assistant=ai_assistant,
            script_type=script_type,
            skip_git=no_git
        )
        
        console.print(f"\n[bold green]✓ Project initialized successfully![/bold green]")
        console.print(f"[cyan]Location:[/cyan] {project_path}")
        console.print(f"[cyan]AI Assistant:[/cyan] {ai_assistant}")
        console.print(f"[cyan]Script Type:[/cyan] {script_type}")
        
        # Show next steps
        _show_next_steps(console, project_name, here, ai_assistant)
        
    except Exception as e:
        console.print(f"[red]Initialization failed:[/red] {e}")
        sys.exit(1)


def _handle_check(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec check command."""
    console = workflow.console
    show_spec_banner(console)
    
    console.print("[bold]Checking Specification-Driven Development tools...[/bold]\n")
    
    # Check tool availability
    workflow.check_tools()


def _handle_constitution(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec constitution command."""
    console = workflow.console
    
    if getattr(args, 'edit', False):
        workflow.edit_constitution()
    else:
        workflow.create_constitution()


def _handle_specify(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec specify command."""
    from .processors import SpecificationProcessor
    
    spec_name = getattr(args, 'spec_name', None)
    
    # Create specification processor
    processor = SpecificationProcessor(workflow.console, workflow.project_dir)
    
    # Run interactive specification creation
    spec_path = processor.create_interactive_spec(spec_name)
    
    if spec_path:
        workflow.console.print(f"\n[bold green]✓ Specification created: {spec_path}[/bold green]")
    else:
        workflow.console.print("\n[yellow]Specification creation cancelled.[/yellow]")


def _handle_plan(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec plan command."""
    from .generators import PlanGenerator
    
    spec_name = getattr(args, 'spec', None)
    
    # Create plan generator
    generator = PlanGenerator(workflow.console, workflow.project_dir)
    
    # Generate implementation plan
    plan_path = generator.generate_plan(spec_name)
    
    if plan_path:
        workflow.console.print(f"\n[bold green]✓ Implementation plan created: {plan_path}[/bold green]")
    else:
        workflow.console.print("\n[yellow]Plan generation cancelled.[/yellow]")


def _handle_tasks(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec tasks command."""
    from .task_generator import TaskGenerator
    
    plan_name = getattr(args, 'plan', None)
    
    # Create task generator
    generator = TaskGenerator(workflow.console, workflow.project_dir)
    
    # Generate actionable tasks
    tasks_path = generator.generate_tasks(plan_name)
    
    if tasks_path:
        workflow.console.print(f"\n[bold green]✓ Development tasks created: {tasks_path}[/bold green]")
    else:
        workflow.console.print("\n[yellow]Task generation cancelled.[/yellow]")


def _handle_clarify(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec clarify command."""
    from .clarification import ClarificationWorkflow
    
    spec_name = getattr(args, 'spec', None)
    
    # Create clarification workflow
    clarifier = ClarificationWorkflow(workflow.console, workflow.project_dir)
    
    # Run clarification workflow
    clarified_path = clarifier.run_clarification_workflow(spec_name)
    
    if clarified_path:
        workflow.console.print(f"\n[bold green]✓ Specification clarified: {clarified_path}[/bold green]")
    else:
        workflow.console.print("\n[yellow]Clarification workflow cancelled.[/yellow]")


def _handle_analyze(args: argparse.Namespace, workflow: SpecWorkflow) -> None:
    """Handle spec analyze command."""
    from .analysis import ConsistencyAnalyzer
    
    verbose = getattr(args, 'verbose', False)
    
    # Create consistency analyzer
    analyzer = ConsistencyAnalyzer(workflow.console, workflow.project_dir)
    
    # Run consistency analysis
    results = analyzer.run_consistency_analysis(verbose)
    
    if "error" not in results:
        score = results.get("overall_score", 0)
        if score >= 80:
            workflow.console.print(f"\n[bold green]✓ High consistency score: {score}/100[/bold green]")
        elif score >= 60:
            workflow.console.print(f"\n[bold yellow]⚠ Moderate consistency score: {score}/100[/bold yellow]")
        else:
            workflow.console.print(f"\n[bold red]❌ Low consistency score: {score}/100[/bold red]")
    else:
        workflow.console.print(f"\n[red]Analysis failed: {results['error']}[/red]")


def _show_next_steps(console, project_name: Optional[str], here: bool, ai_assistant: str) -> None:
    """Show next steps after project initialization."""
    from rich.panel import Panel
    
    steps = []
    
    if not here and project_name:
        steps.append(f"1. Navigate to project: [cyan]cd {project_name}[/cyan]")
        steps.append("2. Establish project principles: [cyan]openhands spec constitution[/cyan]")
    else:
        steps.append("1. Establish project principles: [cyan]openhands spec constitution[/cyan]")
    
    steps.extend([
        "3. Create baseline specification: [cyan]openhands spec specify[/cyan]",
        "4. Create implementation plan: [cyan]openhands spec plan[/cyan]",
        "5. Generate actionable tasks: [cyan]openhands spec tasks[/cyan]",
        "6. Start OpenHands session: [cyan]openhands[/cyan]"
    ])
    
    if ai_assistant == 'openhands':
        steps.append("\n[dim]The OpenHands agent will have full context of your specifications,[/dim]")
        steps.append("[dim]constitutional principles, and implementation plans.[/dim]")
    
    panel = Panel(
        "\n".join(steps),
        title="[bold]Next Steps[/bold]",
        border_style="cyan",
        padding=(1, 2)
    )
    
    console.print()
    console.print(panel)