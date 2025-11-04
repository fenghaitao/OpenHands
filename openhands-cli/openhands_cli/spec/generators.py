"""Plan and task generation for SDD workflow."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn


class PlanGenerator:
    """Generates implementation plans from specifications."""
    
    def __init__(self, console: Console, project_dir: Path):
        """Initialize plan generator.
        
        Args:
            console: Rich console for output
            project_dir: Project directory path
        """
        self.console = console
        self.project_dir = project_dir
        self.specify_dir = project_dir / ".specify"
        self.specs_dir = project_dir / "specs"
    
    def generate_plan(self, spec_name: Optional[str] = None) -> Optional[Path]:
        """Generate implementation plan from specification.
        
        Args:
            spec_name: Name of specification to create plan for
            
        Returns:
            Path to generated plan file, or None if cancelled
        """
        self.console.print("\n[bold cyan]Creating Implementation Plan[/bold cyan]")
        self.console.print("[dim]Generating structured implementation plan from specification.[/dim]\n")
        
        # Load specification
        spec_data = self._load_specification(spec_name)
        if not spec_data:
            return None
        
        # Load constitutional context
        constitution = self._load_constitution()
        
        # Generate plan content
        plan_data = self._generate_plan_content(spec_data, constitution)
        
        # Create plan document
        plan_path = self._create_plan_document(plan_data, spec_data["metadata"]["name"])
        
        # Show completion message
        self._show_plan_summary(plan_path, plan_data)
        
        return plan_path
    
    def _load_specification(self, spec_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load specification data.
        
        Args:
            spec_name: Specification name, or None to use latest
            
        Returns:
            Specification data or None if not found
        """
        if spec_name:
            spec_path = self.specs_dir / f"{spec_name}.md"
            metadata_path = self.specs_dir / f"{spec_name}.json"
        else:
            # Find latest specification
            spec_files = list(self.specs_dir.glob("*.json"))
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
        
        # Load metadata
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))
        
        # Parse specification content
        spec_content = spec_path.read_text(encoding='utf-8')
        spec_data = self._parse_specification_content(spec_content, metadata)
        
        self.console.print(f"[green]✓ Loaded specification: {metadata['title']}[/green]")
        return spec_data
    
    def _load_constitution(self) -> Optional[str]:
        """Load project constitution."""
        constitution_path = self.specify_dir / "memory" / "constitution.md"
        if constitution_path.exists():
            return constitution_path.read_text(encoding='utf-8')
        return None
    
    def _parse_specification_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Parse specification content into structured data.
        
        Args:
            content: Specification markdown content
            metadata: Specification metadata
            
        Returns:
            Parsed specification data
        """
        spec_data = {
            "metadata": metadata,
            "title": metadata.get("title", ""),
            "overview": "",
            "functional_requirements": [],
            "non_functional_requirements": [],
            "user_stories": [],
            "technical_specifications": {},
            "success_metrics": [],
            "dependencies": [],
            "assumptions": [],
            "open_questions": []
        }
        
        # Simple parsing - extract list items under each section
        current_section = None
        for line in content.split('\n'):
            line = line.strip()
            
            # Detect sections
            if line.startswith('## '):
                section_title = line[3:].strip().lower()
                if 'functional requirement' in section_title:
                    current_section = 'functional_requirements'
                elif 'non-functional requirement' in section_title:
                    current_section = 'non_functional_requirements'
                elif 'user stories' in section_title:
                    current_section = 'user_stories'
                elif 'success metric' in section_title:
                    current_section = 'success_metrics'
                elif 'dependencies' in section_title:
                    current_section = 'dependencies'
                elif 'assumptions' in section_title:
                    current_section = 'assumptions'
                elif 'open questions' in section_title:
                    current_section = 'open_questions'
                elif 'overview' in section_title:
                    current_section = 'overview'
                else:
                    current_section = None
            
            # Extract content
            elif current_section == 'overview' and line and not line.startswith('-'):
                if spec_data["overview"]:
                    spec_data["overview"] += " " + line
                else:
                    spec_data["overview"] = line
            elif current_section and line.startswith('- '):
                item = line[2:].strip()
                if item and item != "*No items specified*":
                    spec_data[current_section].append(item)
        
        return spec_data
    
    def _generate_plan_content(self, spec_data: Dict[str, Any], constitution: Optional[str]) -> Dict[str, Any]:
        """Generate implementation plan content.
        
        Args:
            spec_data: Specification data
            constitution: Constitutional principles
            
        Returns:
            Plan data structure
        """
        plan_data = {
            "title": f"Implementation Plan: {spec_data['title']}",
            "spec_reference": spec_data["metadata"]["name"],
            "created": datetime.now().isoformat(),
            "architecture": self._analyze_architecture(spec_data),
            "phases": self._generate_phases(spec_data, constitution),
            "technical_decisions": self._generate_technical_decisions(spec_data),
            "risks": self._assess_risks(spec_data),
            "testing_strategy": self._generate_testing_strategy(spec_data, constitution),
            "deployment_plan": self._generate_deployment_plan(spec_data)
        }
        
        return plan_data
    
    def _analyze_architecture(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and recommend system architecture.
        
        Args:
            spec_data: Specification data
            
        Returns:
            Architecture recommendations
        """
        architecture = {
            "overview": "System architecture analysis based on requirements",
            "recommendations": [],
            "components": [],
            "data_flow": []
        }
        
        # Analyze functional requirements for architecture hints
        func_reqs = spec_data.get("functional_requirements", [])
        user_stories = spec_data.get("user_stories", [])
        
        # Simple heuristics for architecture recommendations
        if any("user" in req.lower() for req in func_reqs + user_stories):
            architecture["components"].append("User Management System")
            architecture["recommendations"].append("Implement user authentication and authorization")
        
        if any("data" in req.lower() for req in func_reqs):
            architecture["components"].append("Data Storage Layer")
            architecture["recommendations"].append("Design robust data persistence strategy")
        
        if any("api" in req.lower() for req in func_reqs):
            architecture["components"].append("API Layer")
            architecture["recommendations"].append("Design RESTful API interface")
        
        if len(func_reqs) > 10:
            architecture["recommendations"].append("Consider microservices architecture for scalability")
        else:
            architecture["recommendations"].append("Monolithic architecture suitable for current scope")
        
        return architecture
    
    def _generate_phases(self, spec_data: Dict[str, Any], constitution: Optional[str]) -> List[Dict[str, Any]]:
        """Generate implementation phases.
        
        Args:
            spec_data: Specification data
            constitution: Constitutional principles
            
        Returns:
            List of implementation phases
        """
        phases = []
        
        # Phase 1: Foundation
        foundation_phase = {
            "name": "Foundation",
            "description": "Set up project infrastructure and core systems",
            "duration": "2-3 weeks",
            "tasks": [
                "Set up development environment",
                "Initialize project structure",
                "Configure version control",
                "Set up CI/CD pipeline"
            ],
            "deliverables": [
                "Working development environment",
                "Project repository with basic structure",
                "Automated build and test pipeline"
            ]
        }
        
        # Add constitutional requirements to foundation
        if constitution and "testing" in constitution.lower():
            foundation_phase["tasks"].extend([
                "Set up testing framework",
                "Configure code quality tools"
            ])
        
        if constitution and "security" in constitution.lower():
            foundation_phase["tasks"].extend([
                "Set up security scanning tools",
                "Configure authentication framework"
            ])
        
        phases.append(foundation_phase)
        
        # Phase 2: Core Features
        core_phase = {
            "name": "Core Features",
            "description": "Implement essential functionality",
            "duration": "4-6 weeks",
            "tasks": [],
            "deliverables": []
        }
        
        # Convert functional requirements to tasks
        func_reqs = spec_data.get("functional_requirements", [])
        for req in func_reqs[:5]:  # Prioritize first 5 requirements
            task = f"Implement: {req}"
            core_phase["tasks"].append(task)
            deliverable = f"Working {req.lower()}"
            core_phase["deliverables"].append(deliverable)
        
        phases.append(core_phase)
        
        # Phase 3: Enhancement
        if len(func_reqs) > 5:
            enhancement_phase = {
                "name": "Enhancement",
                "description": "Additional features and improvements",
                "duration": "2-4 weeks",
                "tasks": [f"Implement: {req}" for req in func_reqs[5:]],
                "deliverables": [f"Enhanced {req.lower()}" for req in func_reqs[5:]]
            }
            phases.append(enhancement_phase)
        
        # Phase 4: Polish & Deployment
        polish_phase = {
            "name": "Polish & Deployment",
            "description": "Final testing, optimization, and deployment",
            "duration": "1-2 weeks",
            "tasks": [
                "Performance optimization",
                "Security audit",
                "User acceptance testing",
                "Production deployment",
                "Documentation completion"
            ],
            "deliverables": [
                "Optimized application",
                "Security assessment report",
                "Production-ready deployment",
                "Complete documentation"
            ]
        }
        phases.append(polish_phase)
        
        return phases
    
    def _generate_technical_decisions(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate key technical decisions.
        
        Args:
            spec_data: Specification data
            
        Returns:
            List of technical decisions with rationale
        """
        decisions = []
        
        # Analyze technical specifications if provided
        tech_specs = spec_data.get("technical_specifications", {})
        
        if tech_specs.get("languages"):
            decisions.append({
                "decision": f"Programming Language: {', '.join(tech_specs['languages'])}",
                "rationale": "Based on specified requirements and team expertise"
            })
        
        if tech_specs.get("database"):
            decisions.append({
                "decision": f"Database: {tech_specs['database']}",
                "rationale": "Aligns with data requirements and scalability needs"
            })
        
        # Default technical decisions if not specified
        if not decisions:
            decisions.extend([
                {
                    "decision": "Use version control (Git) for all code",
                    "rationale": "Essential for collaboration and change tracking"
                },
                {
                    "decision": "Implement comprehensive testing strategy",
                    "rationale": "Ensures code quality and reliability"
                },
                {
                    "decision": "Use containerization for deployment",
                    "rationale": "Provides consistency across environments"
                }
            ])
        
        return decisions
    
    def _assess_risks(self, spec_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess project risks and mitigation strategies.
        
        Args:
            spec_data: Specification data
            
        Returns:
            List of risks with mitigation strategies
        """
        risks = []
        
        # Analyze open questions for risks
        open_questions = spec_data.get("open_questions", [])
        if open_questions:
            risks.append({
                "risk": "Requirement ambiguity",
                "impact": "Medium",
                "probability": "High",
                "mitigation": "Regular stakeholder meetings to clarify requirements"
            })
        
        # Check for security requirements
        non_func_reqs = spec_data.get("non_functional_requirements", [])
        if not any("security" in req.lower() for req in non_func_reqs):
            risks.append({
                "risk": "Security vulnerabilities",
                "impact": "High", 
                "probability": "Medium",
                "mitigation": "Implement security best practices and regular audits"
            })
        
        # Check for performance requirements
        if not any("performance" in req.lower() for req in non_func_reqs):
            risks.append({
                "risk": "Performance issues",
                "impact": "Medium",
                "probability": "Medium", 
                "mitigation": "Regular performance testing and optimization"
            })
        
        # Add common project risks
        risks.extend([
            {
                "risk": "Scope creep",
                "impact": "Medium",
                "probability": "High",
                "mitigation": "Strict change control process and regular reviews"
            },
            {
                "risk": "Technical debt accumulation",
                "impact": "Medium",
                "probability": "Medium",
                "mitigation": "Regular code reviews and refactoring sessions"
            }
        ])
        
        return risks
    
    def _generate_testing_strategy(self, spec_data: Dict[str, Any], constitution: Optional[str]) -> Dict[str, Any]:
        """Generate testing strategy.
        
        Args:
            spec_data: Specification data
            constitution: Constitutional principles
            
        Returns:
            Testing strategy details
        """
        strategy = {
            "overview": "Comprehensive testing approach to ensure quality",
            "levels": [],
            "tools": [],
            "coverage_targets": {}
        }
        
        # Basic testing levels
        strategy["levels"] = [
            "Unit Testing - Test individual components",
            "Integration Testing - Test component interactions",
            "System Testing - Test complete system functionality",
            "User Acceptance Testing - Validate user requirements"
        ]
        
        # Add security testing if constitution emphasizes security
        if constitution and "security" in constitution.lower():
            strategy["levels"].append("Security Testing - Validate security requirements")
        
        # Add performance testing if non-functional requirements include performance
        non_func_reqs = spec_data.get("non_functional_requirements", [])
        if any("performance" in req.lower() for req in non_func_reqs):
            strategy["levels"].append("Performance Testing - Validate performance requirements")
        
        # Coverage targets
        if constitution and ("quality" in constitution.lower() or "testing" in constitution.lower()):
            strategy["coverage_targets"] = {
                "unit_test_coverage": "90%+",
                "integration_test_coverage": "80%+",
                "critical_path_coverage": "100%"
            }
        else:
            strategy["coverage_targets"] = {
                "unit_test_coverage": "80%+",
                "integration_test_coverage": "70%+"
            }
        
        return strategy
    
    def _generate_deployment_plan(self, spec_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment plan.
        
        Args:
            spec_data: Specification data
            
        Returns:
            Deployment plan details
        """
        plan = {
            "overview": "Systematic deployment approach",
            "environments": [
                "Development - Local development environment",
                "Testing - Automated testing environment", 
                "Staging - Production-like testing environment",
                "Production - Live user environment"
            ],
            "strategy": "Blue-green deployment for zero-downtime updates",
            "rollback_plan": "Automated rollback on deployment failure",
            "monitoring": [
                "Application health monitoring",
                "Performance metrics tracking",
                "Error rate monitoring",
                "User activity tracking"
            ]
        }
        
        # Check technical specifications for deployment hints
        tech_specs = spec_data.get("technical_specifications", {})
        if tech_specs.get("deployment"):
            plan["platform"] = tech_specs["deployment"]
        else:
            plan["platform"] = "Cloud platform (AWS/Azure/GCP) recommended"
        
        return plan
    
    def _create_plan_document(self, plan_data: Dict[str, Any], spec_name: str) -> Path:
        """Create implementation plan document.
        
        Args:
            plan_data: Plan data structure
            spec_name: Source specification name
            
        Returns:
            Path to created plan document
        """
        # Create plan filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_filename = f"plan_{spec_name}_{timestamp}.md"
        plan_path = self.specs_dir / plan_filename
        
        # Generate plan content
        content = self._render_plan_template(plan_data)
        
        # Write plan file
        plan_path.write_text(content, encoding='utf-8')
        
        # Create metadata file
        metadata = {
            "name": plan_filename.replace('.md', ''),
            "title": plan_data["title"],
            "spec_reference": plan_data["spec_reference"],
            "created": plan_data["created"],
            "type": "implementation_plan",
            "version": "1.0"
        }
        
        metadata_path = self.specs_dir / f"{metadata['name']}.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        
        return plan_path
    
    def _render_plan_template(self, plan_data: Dict[str, Any]) -> str:
        """Render plan template with data.
        
        Args:
            plan_data: Plan data structure
            
        Returns:
            Rendered plan content
        """
        content = f"""---
title: "{plan_data['title']}"
spec_reference: "{plan_data['spec_reference']}"
created: "{plan_data['created']}"
type: "implementation_plan"
version: "1.0"
---

# {plan_data['title']}

## Architecture Overview

{plan_data['architecture']['overview']}

### Recommended Components
{self._format_list(plan_data['architecture']['components'])}

### Architecture Recommendations
{self._format_list(plan_data['architecture']['recommendations'])}

## Implementation Phases

{self._format_phases(plan_data['phases'])}

## Technical Decisions

{self._format_technical_decisions(plan_data['technical_decisions'])}

## Risk Assessment

{self._format_risks(plan_data['risks'])}

## Testing Strategy

{plan_data['testing_strategy']['overview']}

### Testing Levels
{self._format_list(plan_data['testing_strategy']['levels'])}

### Coverage Targets
{self._format_dict(plan_data['testing_strategy']['coverage_targets'])}

## Deployment Plan

{plan_data['deployment_plan']['overview']}

### Environments
{self._format_list(plan_data['deployment_plan']['environments'])}

### Deployment Strategy
{plan_data['deployment_plan']['strategy']}

### Monitoring
{self._format_list(plan_data['deployment_plan']['monitoring'])}

---
*This implementation plan was generated from specification: {plan_data['spec_reference']}*
"""
        return content
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items for markdown."""
        if not items:
            return "*No items specified*"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_dict(self, items: Dict[str, str]) -> str:
        """Format dictionary items for markdown."""
        if not items:
            return "*No items specified*"
        return "\n".join(f"- **{key}:** {value}" for key, value in items.items())
    
    def _format_phases(self, phases: List[Dict[str, Any]]) -> str:
        """Format implementation phases for markdown."""
        content = []
        for i, phase in enumerate(phases, 1):
            content.append(f"### Phase {i}: {phase['name']}")
            content.append(f"**Duration:** {phase['duration']}")
            content.append(f"**Description:** {phase['description']}")
            content.append("**Tasks:**")
            content.append(self._format_list(phase['tasks']))
            content.append("**Deliverables:**")
            content.append(self._format_list(phase['deliverables']))
            content.append("")
        return "\n".join(content)
    
    def _format_technical_decisions(self, decisions: List[Dict[str, Any]]) -> str:
        """Format technical decisions for markdown."""
        content = []
        for decision in decisions:
            content.append(f"### {decision['decision']}")
            content.append(f"**Rationale:** {decision['rationale']}")
            content.append("")
        return "\n".join(content)
    
    def _format_risks(self, risks: List[Dict[str, Any]]) -> str:
        """Format risks for markdown."""
        content = []
        for risk in risks:
            content.append(f"### {risk['risk']}")
            content.append(f"**Impact:** {risk['impact']}")
            content.append(f"**Probability:** {risk['probability']}")
            content.append(f"**Mitigation:** {risk['mitigation']}")
            content.append("")
        return "\n".join(content)
    
    def _show_plan_summary(self, plan_path: Path, plan_data: Dict[str, Any]) -> None:
        """Show summary of created plan."""
        self.console.print("\n" + "="*60)
        self.console.print("[bold green]✓ Implementation Plan Created Successfully![/bold green]")
        self.console.print("="*60)
        
        self.console.print(f"[cyan]Title:[/cyan] {plan_data['title']}")
        self.console.print(f"[cyan]Location:[/cyan] {plan_path}")
        self.console.print(f"[cyan]Phases:[/cyan] {len(plan_data['phases'])}")
        self.console.print(f"[cyan]Technical Decisions:[/cyan] {len(plan_data['technical_decisions'])}")
        self.console.print(f"[cyan]Identified Risks:[/cyan] {len(plan_data['risks'])}")
        
        # Show next steps
        panel = Panel(
            "1. Review the generated implementation plan\n"
            "2. Run: [cyan]openhands spec tasks[/cyan] to generate actionable tasks\n"
            "3. Begin implementation following the planned phases\n"
            "4. Start development: [cyan]openhands[/cyan]",
            title="[bold]Next Steps[/bold]",
            border_style="green"
        )
        
        self.console.print()
        self.console.print(panel)