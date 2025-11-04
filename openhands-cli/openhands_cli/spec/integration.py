"""Simple integration module for testing SDD context."""

from pathlib import Path
from typing import Optional


def check_sdd_project(project_dir: Optional[Path] = None) -> bool:
    """Check if directory is an SDD project.
    
    Args:
        project_dir: Directory to check, defaults to current
        
    Returns:
        True if SDD project structure exists
    """
    if project_dir is None:
        project_dir = Path.cwd()
    
    specify_dir = project_dir / ".specify"
    constitution_path = specify_dir / "memory" / "constitution.md"
    
    return specify_dir.exists() and constitution_path.exists()


def get_sdd_summary(project_dir: Optional[Path] = None) -> dict:
    """Get SDD project summary.
    
    Args:
        project_dir: Directory to check, defaults to current
        
    Returns:
        Dictionary with SDD project information
    """
    if project_dir is None:
        project_dir = Path.cwd()
    
    summary = {
        "is_sdd_project": check_sdd_project(project_dir),
        "artifacts": {},
        "progress": {}
    }
    
    if summary["is_sdd_project"]:
        specs_dir = project_dir / "specs"
        
        if specs_dir.exists():
            # Count different types of files
            all_files = list(specs_dir.glob("*.md"))
            plan_files = [f for f in all_files if f.name.startswith("plan_")]
            task_files = [f for f in all_files if f.name.startswith("tasks_")]
            spec_files = [f for f in all_files if not f.name.startswith(("plan_", "tasks_"))]
            
            summary["artifacts"] = {
                "specifications": len(spec_files),
                "plans": len(plan_files),
                "task_lists": len(task_files)
            }
            
            # Get latest files
            if spec_files:
                latest_spec = max(spec_files, key=lambda f: f.stat().st_mtime)
                summary["latest_spec"] = latest_spec.name
            
            if plan_files:
                latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)
                summary["latest_plan"] = latest_plan.name
            
            if task_files:
                latest_tasks = max(task_files, key=lambda f: f.stat().st_mtime)
                summary["latest_tasks"] = latest_tasks.name
    
    return summary


def get_context_message() -> str:
    """Get SDD context message for agent.
    
    Returns:
        Context message string
    """
    if not check_sdd_project():
        return ""
    
    summary = get_sdd_summary()
    
    message_parts = [
        "🔍 SPECIFICATION-DRIVEN DEVELOPMENT PROJECT",
        "",
        "This project follows SDD methodology. All development should align with:",
        "• Constitutional principles (see .specify/memory/constitution.md)",
        "• Project specifications and implementation plans",
        "• Current development tasks and priorities",
        ""
    ]
    
    if summary["artifacts"]["specifications"] > 0:
        message_parts.append(f"📋 Active specifications: {summary['artifacts']['specifications']}")
    
    if summary["artifacts"]["plans"] > 0:
        message_parts.append(f"🏗️ Implementation plans: {summary['artifacts']['plans']}")
    
    if summary["artifacts"]["task_lists"] > 0:
        message_parts.append(f"✅ Task lists: {summary['artifacts']['task_lists']}")
    
    message_parts.extend([
        "",
        "💡 Use /sdd command to view current context",
        "💡 Use /progress command to check development progress",
        ""
    ])
    
    return "\n".join(message_parts)


if __name__ == "__main__":
    summary = get_sdd_summary()
    print("SDD Project Summary:")
    print(f"  Is SDD Project: {summary['is_sdd_project']}")
    
    if summary["is_sdd_project"]:
        print(f"  Artifacts: {summary['artifacts']}")
        if "latest_spec" in summary:
            print(f"  Latest Spec: {summary['latest_spec']}")
        if "latest_plan" in summary:
            print(f"  Latest Plan: {summary['latest_plan']}")
        if "latest_tasks" in summary:
            print(f"  Latest Tasks: {summary['latest_tasks']}")
        
        print("\nContext Message:")
        print(get_context_message())