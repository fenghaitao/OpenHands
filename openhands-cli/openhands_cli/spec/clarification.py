"""Clarification workflows for resolving specification ambiguities."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text

from .validators import AmbiguityDetector
from .context import SpecContext


class ClarificationWorkflow:
    """Manages clarification workflows for specification ambiguities."""
    
    def __init__(self, console: Console, project_dir: Path):
        """Initialize clarification workflow.
        
        Args:
            console: Rich console for output
            project_dir: Project directory path
        """
        self.console = console
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.specs_dir = project_dir / "specs"
        self.ambiguity_detector = AmbiguityDetector(console)
        self.spec_context = SpecContext(project_dir, console)
    
    def run_clarification_workflow(self, spec_name: Optional[str] = None) -> Optional[Path]:
        """Run complete clarification workflow.
        
        Args:
            spec_name: Specification to clarify, or None for latest
            
        Returns:
            Path to updated specification or None if cancelled
        """
        self.console.print("\n[bold cyan]Specification Clarification Workflow[/bold cyan]")
        self.console.print("[dim]Identifying and resolving ambiguous areas in specifications.[/dim]\n")
        
        # Load specification
        spec_data = self._load_specification(spec_name)
        if not spec_data:
            return None
        
        # Detect ambiguities
        ambiguities = self._detect_ambiguities(spec_data)
        if not ambiguities:
            self.console.print("[green]✓ No ambiguities detected in specification![/green]")
            return spec_data["path"]
        
        # Show ambiguity report
        self._show_ambiguity_report(ambiguities)
        
        # Ask if user wants to proceed
        if not Confirm.ask("\n[cyan]Would you like to resolve these ambiguities?[/cyan]"):
            return spec_data["path"]
        
        # Run clarification process
        clarifications = self._gather_clarifications(ambiguities)
        
        if clarifications:
            # Update specification with clarifications
            updated_path = self._update_specification_with_clarifications(
                spec_data, clarifications
            )
            
            # Show completion summary
            self._show_clarification_summary(updated_path, len(clarifications))
            
            return updated_path
        
        return spec_data["path"]
    
    def _load_specification(self, spec_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load specification for clarification.
        
        Args:
            spec_name: Specification name or None for latest
            
        Returns:
            Specification data or None if not found
        """
        if spec_name:
            spec_path = self.specs_dir / f"{spec_name}.md"
            metadata_path = self.specs_dir / f"{spec_name}.json"
        else:
            # Find latest specification
            spec_files = [
                f for f in self.specs_dir.glob("*.json")
                if not f.stem.startswith(("plan_", "tasks_"))
            ]
            
            if not spec_files:
                self.console.print("[red]No specifications found. Run 'openhands spec specify' first.[/red]")
                return None
            
            # Sort by creation time (latest first)
            spec_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            metadata_path = spec_files[0]
            spec_name = metadata_path.stem
            spec_path = self.specs_dir / f"{spec_name}.md"
        
        if not spec_path.exists() or not metadata_path.exists():
            self.console.print(f"[red]Specification '{spec_name}' not found.[/red]")
            return None
        
        # Load metadata and content
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        content = spec_path.read_text(encoding='utf-8')
        
        self.console.print(f"[green]✓ Loaded specification: {metadata['title']}[/green]")
        
        return {
            "metadata": metadata,
            "content": content,
            "path": spec_path,
            "metadata_path": metadata_path
        }
    
    def _detect_ambiguities(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect ambiguities in specification.
        
        Args:
            spec_data: Specification data
            
        Returns:
            List of detected ambiguities
        """
        content = spec_data["content"]
        ambiguities = self.ambiguity_detector.detect_ambiguities(content)
        
        # Enhance ambiguities with context
        enhanced_ambiguities = []
        lines = content.split('\n')
        
        for ambiguity in ambiguities:
            start_pos, end_pos = ambiguity["position"]
            
            # Find line number and context
            char_count = 0
            line_num = 0
            line_context = ""
            
            for i, line in enumerate(lines):
                if char_count <= start_pos <= char_count + len(line):
                    line_num = i + 1
                    line_context = line.strip()
                    break
                char_count += len(line) + 1  # +1 for newline
            
            enhanced_ambiguity = {
                **ambiguity,
                "line_number": line_num,
                "line_context": line_context,
                "severity": self._assess_ambiguity_severity(ambiguity)
            }
            
            enhanced_ambiguities.append(enhanced_ambiguity)
        
        # Sort by severity (high to low)
        enhanced_ambiguities.sort(
            key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["severity"]], 
            reverse=True
        )
        
        return enhanced_ambiguities
    
    def _assess_ambiguity_severity(self, ambiguity: Dict[str, Any]) -> str:
        """Assess severity of ambiguity.
        
        Args:
            ambiguity: Ambiguity data
            
        Returns:
            Severity level (high/medium/low)
        """
        issue = ambiguity["issue"].lower()
        text = ambiguity["text"].lower()
        
        # High severity issues
        if "modal verbs" in issue and text in ["should", "could", "might"]:
            return "high"
        if "quantifiers" in issue and text in ["some", "many", "few"]:
            return "high"
        if "subjective" in issue and text in ["fast", "easy", "simple"]:
            return "high"
        
        # Medium severity issues
        if "open-ended" in issue:
            return "medium"
        if "ux terms" in issue:
            return "medium"
        
        # Low severity by default
        return "low"
    
    def _show_ambiguity_report(self, ambiguities: List[Dict[str, Any]]) -> None:
        """Show detailed ambiguity report.
        
        Args:
            ambiguities: List of detected ambiguities
        """
        self.console.print(f"\n[yellow]⚠ Found {len(ambiguities)} ambiguities in specification:[/yellow]\n")
        
        # Create ambiguity table
        table = Table(title="Specification Ambiguities")
        table.add_column("Severity", style="bold")
        table.add_column("Line", justify="right")
        table.add_column("Ambiguous Text", style="red")
        table.add_column("Issue", style="yellow")
        table.add_column("Context", style="dim")
        
        for ambiguity in ambiguities:
            severity_color = {
                "high": "[red]HIGH[/red]",
                "medium": "[yellow]MEDIUM[/yellow]", 
                "low": "[green]LOW[/green]"
            }[ambiguity["severity"]]
            
            # Truncate context if too long
            context = ambiguity["line_context"]
            if len(context) > 50:
                context = context[:47] + "..."
            
            table.add_row(
                severity_color,
                str(ambiguity["line_number"]),
                f'"{ambiguity["text"]}"',
                ambiguity["issue"],
                context
            )
        
        self.console.print(table)
        
        # Show severity summary
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for ambiguity in ambiguities:
            severity_counts[ambiguity["severity"]] += 1
        
        summary_text = []
        if severity_counts["high"] > 0:
            summary_text.append(f"🔴 {severity_counts['high']} high-severity (require immediate attention)")
        if severity_counts["medium"] > 0:
            summary_text.append(f"🟡 {severity_counts['medium']} medium-severity (should be addressed)")
        if severity_counts["low"] > 0:
            summary_text.append(f"🟢 {severity_counts['low']} low-severity (minor improvements)")
        
        if summary_text:
            panel = Panel(
                "\n".join(summary_text),
                title="[bold]Severity Summary[/bold]",
                border_style="yellow"
            )
            self.console.print()
            self.console.print(panel)
    
    def _gather_clarifications(self, ambiguities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gather clarifications for ambiguities.
        
        Args:
            ambiguities: List of ambiguities to clarify
            
        Returns:
            List of clarification data
        """
        clarifications = []
        
        self.console.print("\n[bold]Clarification Process[/bold]")
        self.console.print("We'll go through each ambiguity and gather specific clarifications.\n")
        
        # Focus on high and medium severity first
        priority_ambiguities = [
            a for a in ambiguities 
            if a["severity"] in ["high", "medium"]
        ]
        
        if priority_ambiguities:
            self.console.print("[yellow]Addressing high and medium priority ambiguities first.[/yellow]\n")
            target_ambiguities = priority_ambiguities
        else:
            target_ambiguities = ambiguities
        
        for i, ambiguity in enumerate(target_ambiguities, 1):
            self.console.print(f"[bold cyan]Clarification {i}/{len(target_ambiguities)}[/bold cyan]")
            self.console.print(f"[red]Ambiguous text:[/red] \"{ambiguity['text']}\"")
            self.console.print(f"[yellow]Issue:[/yellow] {ambiguity['issue']}")
            self.console.print(f"[dim]Context:[/dim] {ambiguity['line_context']}")
            self.console.print(f"[blue]Suggestion:[/blue] {ambiguity['suggestion']}")
            self.console.print()
            
            # Generate clarifying questions
            questions = self._generate_clarifying_questions(ambiguity)
            
            if questions:
                self.console.print("[bold]Clarifying Questions:[/bold]")
                for j, question in enumerate(questions, 1):
                    self.console.print(f"   {j}. {question}")
                self.console.print()
            
            # Get clarification from user
            clarification = self._get_clarification_input(ambiguity)
            
            if clarification:
                clarifications.append({
                    "ambiguity": ambiguity,
                    "clarification": clarification,
                    "timestamp": datetime.now().isoformat()
                })
            
            # Ask if user wants to continue
            if i < len(target_ambiguities):
                if not Confirm.ask(f"\n[cyan]Continue to next ambiguity ({i+1}/{len(target_ambiguities)})?[/cyan]"):
                    break
            
            self.console.print("\n" + "─" * 60 + "\n")
        
        return clarifications
    
    def _generate_clarifying_questions(self, ambiguity: Dict[str, Any]) -> List[str]:
        """Generate specific clarifying questions for ambiguity.
        
        Args:
            ambiguity: Ambiguity data
            
        Returns:
            List of clarifying questions
        """
        questions = []
        issue = ambiguity["issue"].lower()
        text = ambiguity["text"].lower()
        
        if "modal verbs" in issue:
            if text in ["should", "could", "might", "may"]:
                questions.extend([
                    f"Is '{ambiguity['text']}' a strict requirement (must) or optional (could)?",
                    "What are the consequences if this is not implemented?",
                    "Under what conditions would this not be required?"
                ])
        
        elif "quantifiers" in issue:
            questions.extend([
                f"What specific number or range does '{ambiguity['text']}' represent?",
                "What is the minimum acceptable amount?", 
                "What is the maximum expected amount?",
                "How was this quantity determined?"
            ])
        
        elif "subjective" in issue:
            questions.extend([
                f"What measurable criteria define '{ambiguity['text']}'?",
                "How will this be tested or verified?",
                "What benchmarks or standards apply?",
                "What would be considered unacceptable?"
            ])
        
        elif "open-ended" in issue:
            questions.extend([
                f"What specific items are included in '{ambiguity['text']}'?",
                "Are there any exclusions or limitations?",
                "How comprehensive should this list be?"
            ])
        
        elif "ux terms" in issue:
            questions.extend([
                f"What specific usability criteria define '{ambiguity['text']}'?",
                "How will user experience be measured?",
                "What user testing methods will be used?",
                "What are the acceptance criteria?"
            ])
        
        return questions
    
    def _get_clarification_input(self, ambiguity: Dict[str, Any]) -> Optional[str]:
        """Get clarification input from user.
        
        Args:
            ambiguity: Ambiguity data
            
        Returns:
            Clarification text or None if skipped
        """
        self.console.print("[cyan]Please provide clarification for this ambiguity:[/cyan]")
        self.console.print("[dim]Enter your specific, measurable clarification (or press Enter to skip):[/dim]")
        
        # Multi-line input for clarification
        lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input("  ")
                if not line.strip():
                    empty_line_count += 1
                    if empty_line_count >= 2 or (empty_line_count >= 1 and not lines):
                        break
                else:
                    empty_line_count = 0
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                break
        
        clarification = "\n".join(lines).strip()
        
        if clarification:
            # Validate clarification quality
            if self._validate_clarification(ambiguity, clarification):
                self.console.print(f"[green]✓ Clarification accepted[/green]")
                return clarification
            else:
                self.console.print("[yellow]⚠ Clarification could be more specific[/yellow]")
                if Confirm.ask("Would you like to revise it?"):
                    return self._get_clarification_input(ambiguity)
                else:
                    return clarification
        
        return None
    
    def _validate_clarification(self, ambiguity: Dict[str, Any], clarification: str) -> bool:
        """Validate quality of clarification.
        
        Args:
            ambiguity: Original ambiguity
            clarification: Proposed clarification
            
        Returns:
            True if clarification is good quality
        """
        clarification_lower = clarification.lower()
        
        # Check for vague language
        vague_terms = ["somehow", "maybe", "possibly", "kind of", "sort of", 
                      "probably", "approximately", "around", "about"]
        
        for term in vague_terms:
            if term in clarification_lower:
                return False
        
        # Check for specific criteria based on ambiguity type
        issue = ambiguity["issue"].lower()
        
        if "quantifiers" in issue:
            # Should contain numbers or ranges
            import re
            has_numbers = bool(re.search(r'\d+', clarification))
            has_ranges = any(word in clarification_lower for word in ['between', 'from', 'to', 'range'])
            return has_numbers or has_ranges
        
        elif "modal verbs" in issue:
            # Should contain definitive language
            definitive_terms = ["must", "will", "shall", "required", "mandatory", "optional"]
            return any(term in clarification_lower for term in definitive_terms)
        
        elif "subjective" in issue:
            # Should contain measurable criteria
            measurable_terms = ["measured", "tested", "verified", "benchmark", "criteria", 
                              "standard", "metric", "percentage", "seconds", "minutes"]
            return any(term in clarification_lower for term in measurable_terms)
        
        return len(clarification) > 20  # Minimum length check
    
    def _update_specification_with_clarifications(
        self, 
        spec_data: Dict[str, Any], 
        clarifications: List[Dict[str, Any]]
    ) -> Path:
        """Update specification with clarifications.
        
        Args:
            spec_data: Original specification data
            clarifications: List of clarifications
            
        Returns:
            Path to updated specification
        """
        content = spec_data["content"]
        
        # Apply clarifications (simple replacement for now)
        for clarification_data in clarifications:
            ambiguity = clarification_data["ambiguity"]
            clarification = clarification_data["clarification"]
            
            # Replace ambiguous text with clarified version
            old_text = ambiguity["text"]
            
            # Create clarified replacement
            if ambiguity["issue"] == "Modal verbs create ambiguity":
                # Replace modal verb with definitive language
                new_text = f"{old_text} (CLARIFIED: {clarification})"
            else:
                # General clarification format
                new_text = f"{old_text} (CLARIFIED: {clarification})"
            
            content = content.replace(old_text, new_text, 1)
        
        # Add clarification section
        clarification_section = self._generate_clarification_section(clarifications)
        content += "\n\n" + clarification_section
        
        # Create new version
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = spec_data["metadata"]["name"]
        new_name = f"{original_name}_clarified_{timestamp}"
        
        # Write updated specification
        new_spec_path = self.specs_dir / f"{new_name}.md"
        new_spec_path.write_text(content, encoding='utf-8')
        
        # Update metadata
        new_metadata = {
            **spec_data["metadata"],
            "name": new_name,
            "version": "1.1",
            "status": "clarified",
            "clarified": datetime.now().isoformat(),
            "clarifications_count": len(clarifications),
            "original_spec": original_name
        }
        
        new_metadata_path = self.specs_dir / f"{new_name}.json"
        new_metadata_path.write_text(json.dumps(new_metadata, indent=2), encoding='utf-8')
        
        return new_spec_path
    
    def _generate_clarification_section(self, clarifications: List[Dict[str, Any]]) -> str:
        """Generate clarification section for specification.
        
        Args:
            clarifications: List of clarifications
            
        Returns:
            Clarification section content
        """
        lines = [
            "## Clarifications",
            "",
            f"This specification has been clarified to resolve {len(clarifications)} ambiguities.",
            f"Clarification completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        for i, clarification_data in enumerate(clarifications, 1):
            ambiguity = clarification_data["ambiguity"]
            clarification = clarification_data["clarification"]
            
            lines.extend([
                f"### Clarification {i}",
                f"**Original ambiguous text:** \"{ambiguity['text']}\"",
                f"**Issue:** {ambiguity['issue']}",
                f"**Clarification:** {clarification}",
                f"**Line:** {ambiguity['line_number']}",
                ""
            ])
        
        return "\n".join(lines)
    
    def _show_clarification_summary(self, updated_path: Path, clarification_count: int) -> None:
        """Show clarification completion summary.
        
        Args:
            updated_path: Path to updated specification
            clarification_count: Number of clarifications made
        """
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]✓ Specification Clarification Complete![/bold green]")
        self.console.print("="*60)
        
        self.console.print(f"[cyan]Updated specification:[/cyan] {updated_path}")
        self.console.print(f"[cyan]Clarifications made:[/cyan] {clarification_count}")
        self.console.print(f"[cyan]Status:[/cyan] Clarified and ready for implementation")
        
        # Show next steps
        panel = Panel(
            "1. Review the clarified specification\n"
            "2. Update implementation plan if needed: [cyan]openhands spec plan[/cyan]\n"
            "3. Regenerate tasks if necessary: [cyan]openhands spec tasks[/cyan]\n"
            "4. Continue development with clarified requirements",
            title="[bold]Next Steps[/bold]",
            border_style="green"
        )
        
        self.console.print()
        self.console.print(panel)