"""Utility functions for spec-kit integration."""

from rich.console import Console
from rich.align import Align
from rich.text import Text
from rich.tree import Tree


def setup_console() -> Console:
    """Set up Rich console with consistent configuration."""
    return Console()


def show_spec_banner(console: Console) -> None:
    """Display the spec-kit integration banner."""
    banner = """
╔═╗╔═╗╔═╗╔═╗  ╦╔═╦╦╔╦╗
╚═╗╠═╝║╣ ║     ╠╩╗║ ║ 
╚═╝╩  ╚═╝╚═╝  ╩ ╩╩ ╩ 
"""
    
    tagline = "Specification-Driven Development for OpenHands"
    
    # Create styled banner
    styled_banner = Text()
    banner_lines = banner.strip().split('\n')
    colors = ["bright_blue", "cyan", "bright_cyan"]
    
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)
    
    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(tagline, style="italic bright_yellow")))
    console.print()


class StepTracker:
    """Track and render hierarchical steps for spec operations."""
    
    def __init__(self, title: str):
        """Initialize step tracker.
        
        Args:
            title: Title for the operation being tracked
        """
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
    
    def add(self, key: str, label: str) -> None:
        """Add a new step to track.
        
        Args:
            key: Unique identifier for the step
            label: Human-readable description
        """
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({
                "key": key, 
                "label": label, 
                "status": "pending", 
                "detail": ""
            })
    
    def complete(self, key: str, detail: str = "") -> None:
        """Mark a step as completed.
        
        Args:
            key: Step identifier
            detail: Additional completion details
        """
        self._update(key, status="done", detail=detail)
    
    def error(self, key: str, detail: str = "") -> None:
        """Mark a step as failed.
        
        Args:
            key: Step identifier
            detail: Error details
        """
        self._update(key, status="error", detail=detail)
    
    def skip(self, key: str, detail: str = "") -> None:
        """Mark a step as skipped.
        
        Args:
            key: Step identifier
            detail: Skip reason
        """
        self._update(key, status="skipped", detail=detail)
    
    def _update(self, key: str, status: str, detail: str) -> None:
        """Update step status and details."""
        for step in self.steps:
            if step["key"] == key:
                step["status"] = status
                if detail:
                    step["detail"] = detail
                return
        
        # If not found, add it
        self.steps.append({
            "key": key, 
            "label": key, 
            "status": status, 
            "detail": detail
        })
    
    def render(self) -> Tree:
        """Render the current state as a Rich Tree."""
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""
            status = step["status"]
            
            # Choose symbol based on status
            if status == "done":
                symbol = "[green]●[/green]"
                text_style = "[white]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
                text_style = "[bright_black]"
            elif status == "error":
                symbol = "[red]●[/red]"
                text_style = "[white]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
                text_style = "[white]"
            else:
                symbol = " "
                text_style = "[white]"
            
            # Format the line
            if detail_text:
                line = f"{symbol} {text_style}{label}[/{text_style}] [bright_black]({detail_text})[/bright_black]"
            else:
                line = f"{symbol} {text_style}{label}[/{text_style}]"
            
            tree.add(line)
        
        return tree