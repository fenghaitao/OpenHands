"""Consistency analysis for SDD artifacts."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .context import SpecContext


class ConsistencyAnalyzer:
    """Analyzes consistency across SDD artifacts."""
    
    def __init__(self, console: Console, project_dir: Path):
        """Initialize consistency analyzer.
        
        Args:
            console: Rich console for output
            project_dir: Project directory path
        """
        self.console = console
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.specs_dir = project_dir / "specs"
        self.spec_context = SpecContext(project_dir, console)
    
    def run_consistency_analysis(self, verbose: bool = False) -> Dict[str, Any]:
        """Run comprehensive consistency analysis.
        
        Args:
            verbose: Show detailed analysis output
            
        Returns:
            Analysis results dictionary
        """
        self.console.print("\n[bold cyan]Cross-Artifact Consistency Analysis[/bold cyan]")
        self.console.print("[dim]Analyzing alignment between specifications, plans, and tasks.[/dim]\n")
        
        # Check if SDD project
        if not self.spec_context.is_sdd_project():
            self.console.print("[red]This is not a Specification-Driven Development project.[/red]")
            return {"error": "Not an SDD project"}
        
        # Load all artifacts
        artifacts = self._load_all_artifacts()
        
        if not artifacts["specifications"]:
            self.console.print("[red]No specifications found. Run 'openhands spec specify' first.[/red]")
            return {"error": "No specifications"}
        
        # Run analysis
        analysis_results = {
            "constitutional_analysis": self._analyze_constitutional_consistency(artifacts),
            "spec_plan_analysis": self._analyze_spec_plan_alignment(artifacts),
            "plan_task_analysis": self._analyze_plan_task_coverage(artifacts),
            "requirement_traceability": self._analyze_requirement_traceability(artifacts),
            "gap_analysis": self._analyze_gaps_and_conflicts(artifacts),
            "overall_score": 0,
            "recommendations": []
        }
        
        # Calculate overall consistency score
        analysis_results["overall_score"] = self._calculate_consistency_score(analysis_results)
        
        # Generate recommendations
        analysis_results["recommendations"] = self._generate_recommendations(analysis_results)
        
        # Show results
        self._show_analysis_results(analysis_results, verbose)
        
        # Save analysis report
        if verbose:
            report_path = self._save_analysis_report(analysis_results)
            self.console.print(f"\n[cyan]Detailed report saved to:[/cyan] {report_path}")
        
        return analysis_results
    
    def _load_all_artifacts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all SDD artifacts.
        
        Returns:
            Dictionary containing all artifacts
        """
        artifacts = {
            "constitution": None,
            "specifications": [],
            "plans": [],
            "tasks": []
        }
        
        # Load constitution
        constitution = self.spec_context.load_constitution()
        if constitution:
            artifacts["constitution"] = constitution
        
        # Load all specifications, plans, and tasks
        if self.specs_dir.exists():
            json_files = list(self.specs_dir.glob("*.json"))
            
            for json_file in json_files:
                try:
                    metadata = json.loads(json_file.read_text(encoding='utf-8'))
                    md_file = self.specs_dir / f"{json_file.stem}.md"
                    
                    if md_file.exists():
                        content = md_file.read_text(encoding='utf-8')
                        
                        artifact = {
                            "metadata": metadata,
                            "content": content,
                            "path": md_file
                        }
                        
                        # Categorize by type
                        if json_file.stem.startswith("plan_"):
                            artifacts["plans"].append(artifact)
                        elif json_file.stem.startswith("tasks_"):
                            artifacts["tasks"].append(artifact)
                        else:
                            artifacts["specifications"].append(artifact)
                
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        # Sort by creation time (latest first)
        for artifact_type in ["specifications", "plans", "tasks"]:
            artifacts[artifact_type].sort(
                key=lambda x: x["metadata"].get("created", ""), 
                reverse=True
            )
        
        return artifacts
    
    def _analyze_constitutional_consistency(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze consistency with constitutional principles.
        
        Args:
            artifacts: All loaded artifacts
            
        Returns:
            Constitutional consistency analysis
        """
        analysis = {
            "score": 100,
            "violations": [],
            "missing_principles": [],
            "recommendations": []
        }
        
        constitution = artifacts["constitution"]
        if not constitution:
            analysis["score"] = 0
            analysis["violations"].append("No constitution found")
            return analysis
        
        # Extract constitutional principles
        principles = self._extract_constitutional_principles(constitution)
        
        # Check each specification
        for spec in artifacts["specifications"]:
            violations = self._check_constitutional_violations(spec, principles)
            analysis["violations"].extend(violations)
        
        # Check plans
        for plan in artifacts["plans"]:
            violations = self._check_plan_constitutional_alignment(plan, principles)
            analysis["violations"].extend(violations)
        
        # Calculate score based on violations
        if analysis["violations"]:
            analysis["score"] = max(0, 100 - len(analysis["violations"]) * 15)
        
        return analysis
    
    def _analyze_spec_plan_alignment(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze alignment between specifications and plans.
        
        Args:
            artifacts: All loaded artifacts
            
        Returns:
            Spec-plan alignment analysis
        """
        analysis = {
            "score": 100,
            "missing_requirements": [],
            "orphaned_features": [],
            "coverage_gaps": [],
            "recommendations": []
        }
        
        if not artifacts["specifications"] or not artifacts["plans"]:
            analysis["score"] = 0
            return analysis
        
        # Get latest spec and plan
        latest_spec = artifacts["specifications"][0]
        latest_plan = artifacts["plans"][0] if artifacts["plans"] else None
        
        if not latest_plan:
            analysis["score"] = 0
            analysis["coverage_gaps"].append("No implementation plan found")
            return analysis
        
        # Extract requirements from specification
        spec_requirements = self._extract_requirements(latest_spec["content"])
        
        # Extract planned features from plan
        plan_features = self._extract_plan_features(latest_plan["content"])
        
        # Check coverage
        for requirement in spec_requirements:
            if not self._requirement_covered_in_plan(requirement, plan_features):
                analysis["missing_requirements"].append(requirement)
        
        # Check for orphaned features
        for feature in plan_features:
            if not self._feature_maps_to_requirement(feature, spec_requirements):
                analysis["orphaned_features"].append(feature)
        
        # Calculate score
        total_requirements = len(spec_requirements)
        if total_requirements > 0:
            coverage_rate = (total_requirements - len(analysis["missing_requirements"])) / total_requirements
            analysis["score"] = int(coverage_rate * 100)
        
        return analysis
    
    def _analyze_plan_task_coverage(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze coverage between plans and tasks.
        
        Args:
            artifacts: All loaded artifacts
            
        Returns:
            Plan-task coverage analysis
        """
        analysis = {
            "score": 100,
            "uncovered_phases": [],
            "orphaned_tasks": [],
            "missing_task_categories": [],
            "recommendations": []
        }
        
        if not artifacts["plans"] or not artifacts["tasks"]:
            analysis["score"] = 0
            return analysis
        
        # Get latest plan and tasks
        latest_plan = artifacts["plans"][0]
        latest_tasks = artifacts["tasks"][0] if artifacts["tasks"] else None
        
        if not latest_tasks:
            analysis["score"] = 0
            analysis["missing_task_categories"].append("No task breakdown found")
            return analysis
        
        # Extract plan phases
        plan_phases = self._extract_plan_phases(latest_plan["content"])
        
        # Extract task categories
        task_categories = self._extract_task_categories(latest_tasks["content"])
        
        # Check phase coverage
        for phase in plan_phases:
            if not self._phase_covered_in_tasks(phase, task_categories):
                analysis["uncovered_phases"].append(phase)
        
        # Calculate score
        if plan_phases:
            coverage_rate = (len(plan_phases) - len(analysis["uncovered_phases"])) / len(plan_phases)
            analysis["score"] = int(coverage_rate * 100)
        
        return analysis
    
    def _analyze_requirement_traceability(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze end-to-end requirement traceability.
        
        Args:
            artifacts: All loaded artifacts
            
        Returns:
            Traceability analysis
        """
        analysis = {
            "score": 100,
            "traceable_requirements": [],
            "untraceable_requirements": [],
            "traceability_matrix": {},
            "recommendations": []
        }
        
        if not all([artifacts["specifications"], artifacts["plans"], artifacts["tasks"]]):
            analysis["score"] = 0
            return analysis
        
        # Get latest artifacts
        latest_spec = artifacts["specifications"][0]
        latest_plan = artifacts["plans"][0]
        latest_tasks = artifacts["tasks"][0]
        
        # Extract requirements
        requirements = self._extract_requirements(latest_spec["content"])
        
        # Trace each requirement through the chain
        for requirement in requirements:
            trace = self._trace_requirement(requirement, latest_plan, latest_tasks)
            analysis["traceability_matrix"][requirement] = trace
            
            if trace["traceable"]:
                analysis["traceable_requirements"].append(requirement)
            else:
                analysis["untraceable_requirements"].append(requirement)
        
        # Calculate score
        if requirements:
            traceability_rate = len(analysis["traceable_requirements"]) / len(requirements)
            analysis["score"] = int(traceability_rate * 100)
        
        return analysis
    
    def _analyze_gaps_and_conflicts(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gaps and conflicts across artifacts.
        
        Args:
            artifacts: All loaded artifacts
            
        Returns:
            Gap and conflict analysis
        """
        analysis = {
            "score": 100,
            "gaps": [],
            "conflicts": [],
            "inconsistencies": [],
            "recommendations": []
        }
        
        # Check for common gaps
        if not artifacts["constitution"]:
            analysis["gaps"].append("Missing project constitution")
        
        if not artifacts["specifications"]:
            analysis["gaps"].append("Missing project specifications")
        
        if not artifacts["plans"]:
            analysis["gaps"].append("Missing implementation plans")
        
        if not artifacts["tasks"]:
            analysis["gaps"].append("Missing task breakdown")
        
        # Check for version conflicts
        conflicts = self._detect_version_conflicts(artifacts)
        analysis["conflicts"].extend(conflicts)
        
        # Check for naming inconsistencies
        inconsistencies = self._detect_naming_inconsistencies(artifacts)
        analysis["inconsistencies"].extend(inconsistencies)
        
        # Calculate score
        total_issues = len(analysis["gaps"]) + len(analysis["conflicts"]) + len(analysis["inconsistencies"])
        if total_issues > 0:
            analysis["score"] = max(0, 100 - total_issues * 10)
        
        return analysis
    
    def _calculate_consistency_score(self, analysis_results: Dict[str, Any]) -> int:
        """Calculate overall consistency score.
        
        Args:
            analysis_results: All analysis results
            
        Returns:
            Overall consistency score (0-100)
        """
        scores = []
        
        for key, analysis in analysis_results.items():
            if key != "overall_score" and key != "recommendations" and isinstance(analysis, dict):
                if "score" in analysis:
                    scores.append(analysis["score"])
        
        if scores:
            return int(sum(scores) / len(scores))
        
        return 0
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations.
        
        Args:
            analysis_results: All analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Constitutional recommendations
        constitutional = analysis_results.get("constitutional_analysis", {})
        if constitutional.get("score", 100) < 80:
            recommendations.append("Review and align specifications with constitutional principles")
        
        # Spec-plan recommendations
        spec_plan = analysis_results.get("spec_plan_analysis", {})
        if spec_plan.get("missing_requirements"):
            recommendations.append("Update implementation plan to cover all specification requirements")
        
        # Plan-task recommendations
        plan_task = analysis_results.get("plan_task_analysis", {})
        if plan_task.get("uncovered_phases"):
            recommendations.append("Generate tasks for all implementation plan phases")
        
        # Traceability recommendations
        traceability = analysis_results.get("requirement_traceability", {})
        if traceability.get("untraceable_requirements"):
            recommendations.append("Ensure all requirements are traceable through plan to tasks")
        
        # Gap recommendations
        gaps = analysis_results.get("gap_analysis", {})
        if gaps.get("gaps"):
            recommendations.append("Address missing SDD artifacts to complete methodology")
        
        # Overall score recommendations
        overall_score = analysis_results.get("overall_score", 0)
        if overall_score < 70:
            recommendations.append("Consider running clarification workflow to resolve ambiguities")
            recommendations.append("Review and update all SDD artifacts for better alignment")
        
        return recommendations
    
    def _show_analysis_results(self, analysis_results: Dict[str, Any], verbose: bool) -> None:
        """Display analysis results.
        
        Args:
            analysis_results: Analysis results
            verbose: Show detailed output
        """
        overall_score = analysis_results["overall_score"]
        
        # Overall score panel
        score_color = "green" if overall_score >= 80 else "yellow" if overall_score >= 60 else "red"
        score_panel = Panel(
            f"[bold {score_color}]{overall_score}/100[/bold {score_color}]",
            title="[bold]Overall Consistency Score[/bold]",
            border_style=score_color
        )
        
        self.console.print(score_panel)
        self.console.print()
        
        # Summary table
        table = Table(title="Consistency Analysis Summary")
        table.add_column("Area", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Status", style="bold")
        table.add_column("Issues", justify="right")
        
        analysis_areas = [
            ("Constitutional Alignment", "constitutional_analysis"),
            ("Spec-Plan Alignment", "spec_plan_analysis"),
            ("Plan-Task Coverage", "plan_task_analysis"),
            ("Requirement Traceability", "requirement_traceability"),
            ("Gap Analysis", "gap_analysis")
        ]
        
        for area_name, area_key in analysis_areas:
            area_data = analysis_results.get(area_key, {})
            score = area_data.get("score", 0)
            
            # Count issues
            issue_count = 0
            for issue_key in ["violations", "missing_requirements", "orphaned_features", 
                            "uncovered_phases", "untraceable_requirements", "gaps", "conflicts"]:
                if issue_key in area_data:
                    issue_count += len(area_data[issue_key])
            
            status = "✅ Good" if score >= 80 else "⚠️ Issues" if score >= 60 else "❌ Poor"
            score_style = "green" if score >= 80 else "yellow" if score >= 60 else "red"
            
            table.add_row(
                area_name,
                f"[{score_style}]{score}[/{score_style}]",
                status,
                str(issue_count) if issue_count > 0 else "0"
            )
        
        self.console.print(table)
        
        # Show detailed issues if verbose
        if verbose:
            self._show_detailed_issues(analysis_results)
        
        # Show recommendations
        recommendations = analysis_results["recommendations"]
        if recommendations:
            self.console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for i, rec in enumerate(recommendations, 1):
                self.console.print(f"   {i}. {rec}")
        
        # Show next steps
        next_steps = []
        if overall_score < 70:
            next_steps.append("Run clarification workflow: [cyan]openhands spec clarify[/cyan]")
            next_steps.append("Review and update specifications")
        if overall_score >= 70:
            next_steps.append("Continue development with confidence")
            next_steps.append("Regular consistency checks recommended")
        
        if next_steps:
            panel = Panel(
                "\n".join(next_steps),
                title="[bold]Next Steps[/bold]",
                border_style="blue"
            )
            self.console.print()
            self.console.print(panel)
    
    def _show_detailed_issues(self, analysis_results: Dict[str, Any]) -> None:
        """Show detailed issues from analysis.
        
        Args:
            analysis_results: Analysis results
        """
        self.console.print("\n[bold]Detailed Issues:[/bold]\n")
        
        # Constitutional issues
        constitutional = analysis_results.get("constitutional_analysis", {})
        if constitutional.get("violations"):
            self.console.print("[red]Constitutional Violations:[/red]")
            for violation in constitutional["violations"]:
                self.console.print(f"  • {violation}")
            self.console.print()
        
        # Spec-plan issues
        spec_plan = analysis_results.get("spec_plan_analysis", {})
        if spec_plan.get("missing_requirements"):
            self.console.print("[yellow]Missing Requirements in Plan:[/yellow]")
            for req in spec_plan["missing_requirements"]:
                self.console.print(f"  • {req}")
            self.console.print()
        
        # Plan-task issues
        plan_task = analysis_results.get("plan_task_analysis", {})
        if plan_task.get("uncovered_phases"):
            self.console.print("[yellow]Uncovered Plan Phases:[/yellow]")
            for phase in plan_task["uncovered_phases"]:
                self.console.print(f"  • {phase}")
            self.console.print()
        
        # Traceability issues
        traceability = analysis_results.get("requirement_traceability", {})
        if traceability.get("untraceable_requirements"):
            self.console.print("[red]Untraceable Requirements:[/red]")
            for req in traceability["untraceable_requirements"]:
                self.console.print(f"  • {req}")
            self.console.print()
    
    def _save_analysis_report(self, analysis_results: Dict[str, Any]) -> Path:
        """Save detailed analysis report.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Path to saved report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"consistency_analysis_{timestamp}.json"
        report_path = self.specs_dir / report_filename
        
        # Add metadata
        report_data = {
            "analysis_timestamp": datetime.now().isoformat(),
            "project_directory": str(self.project_dir),
            "overall_score": analysis_results["overall_score"],
            **analysis_results
        }
        
        report_path.write_text(json.dumps(report_data, indent=2), encoding='utf-8')
        
        return report_path
    
    # Helper methods for extracting and analyzing content
    def _extract_constitutional_principles(self, constitution: str) -> List[str]:
        """Extract principles from constitution."""
        # Implementation similar to what we have in context.py
        return self.spec_context._extract_key_principles(constitution)
    
    def _extract_requirements(self, spec_content: str) -> List[str]:
        """Extract requirements from specification."""
        requirements = []
        current_section = None
        
        for line in spec_content.split('\n'):
            line = line.strip()
            
            if line.startswith('## ') and 'requirement' in line.lower():
                current_section = 'requirements'
            elif line.startswith('## '):
                current_section = None
            elif current_section == 'requirements' and line.startswith('- '):
                req = line[2:].strip()
                if req and req != "*No items specified*":
                    requirements.append(req)
        
        return requirements
    
    def _extract_plan_features(self, plan_content: str) -> List[str]:
        """Extract features from implementation plan."""
        features = []
        current_phase = False
        
        for line in plan_content.split('\n'):
            line = line.strip()
            
            if line.startswith('### Phase '):
                current_phase = True
            elif line.startswith('**Tasks:**'):
                current_phase = True
            elif current_phase and line.startswith('- '):
                feature = line[2:].strip()
                if feature:
                    features.append(feature)
            elif line.startswith('### ') and not line.startswith('### Phase'):
                current_phase = False
        
        return features
    
    def _extract_plan_phases(self, plan_content: str) -> List[str]:
        """Extract phases from implementation plan."""
        phases = []
        
        for line in plan_content.split('\n'):
            line = line.strip()
            
            if line.startswith('### Phase '):
                phase = line.split(': ', 1)[1] if ': ' in line else line[10:]
                phases.append(phase)
        
        return phases
    
    def _extract_task_categories(self, tasks_content: str) -> List[str]:
        """Extract task categories from tasks document."""
        categories = []
        
        for line in tasks_content.split('\n'):
            line = line.strip()
            
            if line.startswith('### ') and not line.startswith('###'):
                category = line[4:].strip()
                categories.append(category)
        
        return categories
    
    def _check_constitutional_violations(self, spec: Dict[str, Any], principles: List[str]) -> List[str]:
        """Check for constitutional violations in specification."""
        violations = []
        content = spec["content"].lower()
        
        # Simple checks based on principles
        for principle in principles:
            if "security" in principle.lower():
                if not any(word in content for word in ["security", "secure", "auth", "encrypt"]):
                    violations.append(f"No security considerations found (violates: {principle})")
            
            if "quality" in principle.lower() or "testing" in principle.lower():
                if not any(word in content for word in ["test", "quality", "coverage"]):
                    violations.append(f"No testing/quality requirements found (violates: {principle})")
        
        return violations
    
    def _check_plan_constitutional_alignment(self, plan: Dict[str, Any], principles: List[str]) -> List[str]:
        """Check plan alignment with constitutional principles."""
        violations = []
        content = plan["content"].lower()
        
        for principle in principles:
            if "security" in principle.lower():
                if "security" not in content:
                    violations.append(f"Plan lacks security considerations (violates: {principle})")
        
        return violations
    
    def _requirement_covered_in_plan(self, requirement: str, plan_features: List[str]) -> bool:
        """Check if requirement is covered in plan features."""
        req_words = set(requirement.lower().split())
        
        for feature in plan_features:
            feature_words = set(feature.lower().split())
            if len(req_words.intersection(feature_words)) >= 2:
                return True
        
        return False
    
    def _feature_maps_to_requirement(self, feature: str, requirements: List[str]) -> bool:
        """Check if plan feature maps to a requirement."""
        feature_words = set(feature.lower().split())
        
        for requirement in requirements:
            req_words = set(requirement.lower().split())
            if len(feature_words.intersection(req_words)) >= 2:
                return True
        
        return False
    
    def _phase_covered_in_tasks(self, phase: str, task_categories: List[str]) -> bool:
        """Check if plan phase is covered in task categories."""
        phase_words = set(phase.lower().split())
        
        for category in task_categories:
            category_words = set(category.lower().split())
            if len(phase_words.intersection(category_words)) >= 1:
                return True
        
        return False
    
    def _trace_requirement(self, requirement: str, plan: Dict[str, Any], tasks: Dict[str, Any]) -> Dict[str, Any]:
        """Trace requirement through plan to tasks."""
        trace = {
            "requirement": requirement,
            "in_plan": False,
            "in_tasks": False,
            "traceable": False,
            "path": []
        }
        
        # Check if requirement is covered in plan
        plan_features = self._extract_plan_features(plan["content"])
        if self._requirement_covered_in_plan(requirement, plan_features):
            trace["in_plan"] = True
            trace["path"].append("plan")
        
        # Check if requirement is covered in tasks
        tasks_content = tasks["content"].lower()
        req_words = requirement.lower().split()
        if any(word in tasks_content for word in req_words):
            trace["in_tasks"] = True
            trace["path"].append("tasks")
        
        trace["traceable"] = trace["in_plan"] and trace["in_tasks"]
        
        return trace
    
    def _detect_version_conflicts(self, artifacts: Dict[str, Any]) -> List[str]:
        """Detect version conflicts between artifacts."""
        conflicts = []
        
        # Check if plan references correct spec version
        if artifacts["specifications"] and artifacts["plans"]:
            latest_spec = artifacts["specifications"][0]
            latest_plan = artifacts["plans"][0]
            
            spec_name = latest_spec["metadata"].get("name", "")
            plan_ref = latest_plan["metadata"].get("spec_reference", "")
            
            if spec_name != plan_ref:
                conflicts.append(f"Plan references '{plan_ref}' but latest spec is '{spec_name}'")
        
        return conflicts
    
    def _detect_naming_inconsistencies(self, artifacts: Dict[str, Any]) -> List[str]:
        """Detect naming inconsistencies across artifacts."""
        inconsistencies = []
        
        # Check project name consistency
        names = set()
        
        for spec in artifacts["specifications"]:
            title = spec["metadata"].get("title", "")
            if title:
                names.add(title.lower())
        
        for plan in artifacts["plans"]:
            title = plan["metadata"].get("title", "")
            if title:
                # Extract project name from plan title
                if "implementation plan:" in title.lower():
                    project_name = title.split(":", 1)[1].strip()
                    names.add(project_name.lower())
        
        if len(names) > 1:
            inconsistencies.append(f"Inconsistent project names: {', '.join(names)}")
        
        return inconsistencies