"""Spec-Kit argument parser for OpenHands CLI."""

import argparse


def add_spec_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Add spec-kit subcommands to the main parser.
    
    Args:
        subparsers: The subparsers action from the main argument parser
    """
    spec_parser = subparsers.add_parser(
        'spec',
        help='Specification-Driven Development commands',
        description='Integrate spec-kit SDD workflow into OpenHands'
    )
    
    spec_subparsers = spec_parser.add_subparsers(
        dest='spec_command',
        help='SDD workflow commands',
        metavar='COMMAND'
    )
    
    # spec init command
    init_parser = spec_subparsers.add_parser(
        'init',
        help='Initialize a new spec-driven project',
        description='Set up project structure for Specification-Driven Development'
    )
    init_parser.add_argument(
        'project_name',
        nargs='?',
        help='Name for your new project directory (optional if using --here)'
    )
    init_parser.add_argument(
        '--here',
        action='store_true',
        help='Initialize in current directory'
    )
    init_parser.add_argument(
        '--ai',
        choices=['openhands', 'claude', 'cursor', 'gemini', 'qwen', 'windsurf', 'codex', 'adk'],
        default='openhands',
        help='AI assistant to configure for (default: openhands)'
    )
    init_parser.add_argument(
        '--script-type',
        choices=['sh', 'ps'],
        default='sh',
        help='Script type to use (default: sh)'
    )
    init_parser.add_argument(
        '--no-git',
        action='store_true',
        help='Skip git repository initialization'
    )
    
    # spec check command
    check_parser = spec_subparsers.add_parser(
        'check',
        help='Check that all required tools are installed',
        description='Verify SDD tool availability and configuration'
    )
    
    # spec constitution command
    constitution_parser = spec_subparsers.add_parser(
        'constitution',
        help='Establish project principles and guidelines',
        description='Create or update project constitution with foundational principles'
    )
    constitution_parser.add_argument(
        '--edit',
        action='store_true',
        help='Open constitution file in editor for manual editing'
    )
    
    # spec specify command
    specify_parser = spec_subparsers.add_parser(
        'specify',
        help='Create baseline specification',
        description='Generate or update project specification document'
    )
    specify_parser.add_argument(
        'spec_name',
        nargs='?',
        help='Name for the specification (auto-generated if not provided)'
    )
    
    # spec plan command
    plan_parser = spec_subparsers.add_parser(
        'plan',
        help='Create implementation plan',
        description='Generate implementation plan from specifications'
    )
    plan_parser.add_argument(
        '--spec',
        help='Specification to create plan for (uses latest if not specified)'
    )
    
    # spec tasks command
    tasks_parser = spec_subparsers.add_parser(
        'tasks',
        help='Generate actionable tasks',
        description='Break down implementation plan into specific tasks'
    )
    tasks_parser.add_argument(
        '--plan',
        help='Plan to generate tasks for (uses latest if not specified)'
    )
    
    # spec clarify command (optional enhancement)
    clarify_parser = spec_subparsers.add_parser(
        'clarify',
        help='Ask structured questions to resolve ambiguities',
        description='Identify and clarify ambiguous areas before planning'
    )
    clarify_parser.add_argument(
        '--spec',
        help='Specification to clarify (uses latest if not specified)'
    )
    
    # spec analyze command (optional enhancement)
    analyze_parser = spec_subparsers.add_parser(
        'analyze',
        help='Cross-artifact consistency and alignment report',
        description='Analyze consistency between specs, plans, and tasks'
    )
    analyze_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis output'
    )
    
    # Add global spec options to the main spec parser
    spec_parser.add_argument(
        '--project-dir',
        help='Project directory to operate on (default: current directory)'
    )
    spec_parser.add_argument(
        '--config',
        help='Configuration file to use'
    )