"""Template management for spec-kit integration."""

import shutil
from pathlib import Path
from typing import Dict, Any


class TemplateManager:
    """Manages SDD templates and project structure."""
    
    def __init__(self):
        """Initialize template manager."""
        # Use embedded templates for now (Phase 1)
        # In later phases, this could pull from spec-kit repository
        pass
    
    def copy_templates(self, project_path: Path, ai_assistant: str, script_type: str) -> None:
        """Copy specification templates to project.
        
        Args:
            project_path: Target project directory
            ai_assistant: AI assistant being configured
            script_type: Script type (sh or ps)
        """
        templates_dir = project_path / ".specify" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic template files
        self._create_spec_template(templates_dir / "spec-template.md")
        self._create_plan_template(templates_dir / "plan-template.md", ai_assistant)
        self._create_tasks_template(templates_dir / "tasks-template.md")
        self._create_agent_file_template(templates_dir / "agent-file-template.md")
        
        # Create agent-specific command templates for OpenHands
        if ai_assistant == "openhands":
            self._create_openhands_commands(project_path)
    
    def copy_memory(self, project_path: Path) -> None:
        """Copy knowledge base files to project.
        
        Args:
            project_path: Target project directory
        """
        memory_dir = project_path / ".specify" / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create constitution template
        self.create_constitution_template(memory_dir / "constitution.md")
        
        # Create other memory files (placeholders for now)
        self._create_best_practices(memory_dir / "best_practices.md")
    
    def copy_scripts(self, project_path: Path, script_type: str) -> None:
        """Copy automation scripts to project.
        
        Args:
            project_path: Target project directory
            script_type: Script type (sh or ps)
        """
        scripts_dir = project_path / ".specify" / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        if script_type == "sh":
            self._create_bash_scripts(scripts_dir)
        elif script_type == "ps":
            self._create_powershell_scripts(scripts_dir)
    
    def create_constitution_template(self, constitution_path: Path) -> None:
        """Create a constitution template file.
        
        Args:
            constitution_path: Path where constitution should be created
        """
        content = '''# Project Constitution

## Project Overview
<!-- Describe the purpose, goals, and scope of this project -->

## Core Principles
<!-- Define the fundamental principles that guide all decisions -->

### Development Philosophy
- **Quality First**: Prioritize code quality, testing, and maintainability
- **User-Centered**: Focus on user needs and experience
- **Iterative**: Build incrementally with continuous feedback

### Technical Standards
- **Documentation**: All code must be well-documented
- **Testing**: Comprehensive test coverage required
- **Security**: Security considerations in all design decisions
- **Performance**: Optimize for performance and scalability

## Constraints
<!-- List any limitations, requirements, or non-negotiables -->

### Technical Constraints
- Programming languages and frameworks to use
- Platform and deployment requirements
- Performance benchmarks

### Business Constraints
- Timeline and milestones
- Budget considerations
- Compliance requirements

## Success Criteria
<!-- Define what success looks like for this project -->

### Functional Requirements
- Core features that must be delivered
- User workflows that must be supported

### Non-Functional Requirements
- Performance targets
- Reliability standards
- Security requirements

## Decision Framework
<!-- How should decisions be made when conflicts arise -->

When facing trade-offs, prioritize in this order:
1. User safety and security
2. Core functionality delivery
3. Code quality and maintainability
4. Performance optimization
5. Feature completeness

---
*This constitution serves as the foundation for all project decisions and specifications.*
'''
        constitution_path.write_text(content, encoding='utf-8')
    
    def _create_spec_template(self, spec_path: Path) -> None:
        """Create specification template."""
        content = '''---
title: "Project Specification"
version: "1.0"
created: "{{ date }}"
status: "draft"
---

# Project Specification

## Overview
<!-- High-level description of what this project aims to achieve -->

## Requirements

### Functional Requirements
<!-- What the system must do -->

### Non-Functional Requirements
<!-- How the system should behave -->

## User Stories
<!-- From the user's perspective -->

## Technical Specifications
<!-- Technical details and constraints -->

## Success Metrics
<!-- How will we measure success -->

## Dependencies
<!-- External systems, libraries, or services -->

## Assumptions
<!-- What we're assuming to be true -->

## Open Questions
<!-- Areas that need clarification -->
'''
        spec_path.write_text(content, encoding='utf-8')
    
    def _create_plan_template(self, plan_path: Path, ai_assistant: str) -> None:
        """Create implementation plan template."""
        content = f'''---
title: "Implementation Plan"
version: "1.0"
created: "{{{{ date }}}}"
agent: "{ai_assistant}"
---

# Implementation Plan

## Architecture Overview
<!-- High-level system architecture -->

## Implementation Phases
<!-- Break down into manageable phases -->

### Phase 1: Foundation
<!-- Core infrastructure and setup -->

### Phase 2: Core Features
<!-- Essential functionality -->

### Phase 3: Enhancement
<!-- Additional features and polish -->

## Technical Decisions
<!-- Key technical choices and rationale -->

## Risk Assessment
<!-- Potential risks and mitigation strategies -->

## Testing Strategy
<!-- How will we ensure quality -->

## Deployment Plan
<!-- How will we release the software -->
'''
        plan_path.write_text(content, encoding='utf-8')
    
    def _create_tasks_template(self, tasks_path: Path) -> None:
        """Create tasks template."""
        content = '''---
title: "Project Tasks"
version: "1.0"
created: "{{ date }}"
---

# Project Tasks

## Phase 1: Setup
- [ ] Initialize project structure
- [ ] Set up development environment
- [ ] Configure version control

## Phase 2: Core Development
- [ ] Implement core functionality
- [ ] Write unit tests
- [ ] Create documentation

## Phase 3: Integration
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Security review

## Phase 4: Deployment
- [ ] Deployment preparation
- [ ] User acceptance testing
- [ ] Production deployment
'''
        tasks_path.write_text(content, encoding='utf-8')
    
    def _create_agent_file_template(self, agent_path: Path) -> None:
        """Create agent file template for OpenHands integration."""
        content = '''# Agent Context

## Project Context
This file provides context for AI agents working on this project.

## Constitutional Principles
<!-- Reference to constitution.md -->

## Current Specifications
<!-- Reference to active specifications -->

## Implementation Status
<!-- What has been built, what's in progress -->

## Next Steps
<!-- Immediate priorities for the agent -->

## Guidelines for Agent
- Always refer to the constitution before making decisions
- Follow the established specifications
- Update this file as work progresses
- Ask for clarification when specifications are ambiguous
'''
        agent_path.write_text(content, encoding='utf-8')
    
    def _create_openhands_commands(self, project_path: Path) -> None:
        """Create OpenHands-specific command templates."""
        # This would create .openhands or similar directory structure
        # For Phase 1, we'll create a simple commands directory
        commands_dir = project_path / ".specify" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        
        # Create basic command templates
        (commands_dir / "README.md").write_text("""# OpenHands Commands

This directory contains command templates for OpenHands agent integration.

Commands will be enhanced in Phase 2 of the integration.
""", encoding='utf-8')
    
    def _create_best_practices(self, practices_path: Path) -> None:
        """Create best practices template."""
        content = '''# Development Best Practices

## Code Quality
- Write clean, readable code
- Follow established coding standards
- Use meaningful variable and function names

## Testing
- Write tests for all new functionality
- Maintain high test coverage
- Test edge cases and error conditions

## Documentation
- Document all public APIs
- Keep README files updated
- Comment complex logic

## Git Workflow
- Write clear commit messages
- Use feature branches
- Review code before merging
'''
        practices_path.write_text(content, encoding='utf-8')
    
    def _create_bash_scripts(self, scripts_dir: Path) -> None:
        """Create bash automation scripts."""
        bash_dir = scripts_dir / "bash"
        bash_dir.mkdir(parents=True, exist_ok=True)
        
        # Create setup script
        setup_script = bash_dir / "setup-plan.sh"
        setup_script.write_text('''#!/bin/bash
# Setup script for specification-driven development

echo "Setting up SDD environment..."
echo "Constitution: .specify/memory/constitution.md"
echo "Templates: .specify/templates/"
echo "Scripts: .specify/scripts/"
''', encoding='utf-8')
        
        # Make script executable
        setup_script.chmod(0o755)
    
    def _create_powershell_scripts(self, scripts_dir: Path) -> None:
        """Create PowerShell automation scripts."""
        ps_dir = scripts_dir / "powershell"
        ps_dir.mkdir(parents=True, exist_ok=True)
        
        # Create setup script
        setup_script = ps_dir / "setup-plan.ps1"
        setup_script.write_text('''# Setup script for specification-driven development

Write-Host "Setting up SDD environment..."
Write-Host "Constitution: .specify/memory/constitution.md"
Write-Host "Templates: .specify/templates/"
Write-Host "Scripts: .specify/scripts/"
''', encoding='utf-8')