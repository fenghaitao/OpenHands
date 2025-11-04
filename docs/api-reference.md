# API Reference: Constitutional AI Development Assistant

## Overview

The Constitutional AI Development Assistant provides a comprehensive command-line interface for **Specification-Driven Development (SDD)** with **constitutional AI guidance**. All commands are accessed through the `openhands spec` command structure.

## Command Structure

```bash
openhands spec <command> [options]
```

## Core Commands

### `openhands spec init`

Initialize a new specification-driven development project.

**Syntax:**
```bash
openhands spec init <project_name> [options]
```

**Arguments:**
- `project_name` - Name for the new project directory (optional if using `--here`)

**Options:**
- `--here` - Initialize in current directory instead of creating new directory
- `--ai <assistant>` - AI assistant to configure for (default: `openhands`)
  - Choices: `openhands`, `claude`, `cursor`, `gemini`, `qwen`, `windsurf`, `codex`, `adk`
- `--script-type <type>` - Script type to use (default: `sh`)
  - Choices: `sh`, `ps`
- `--no-git` - Skip git repository initialization

**Examples:**
```bash
# Create new project directory
openhands spec init my-webapp

# Initialize in current directory
openhands spec init --here

# Initialize with specific AI assistant
openhands spec init my-api --ai claude

# Initialize without git
openhands spec init my-tool --no-git

# Initialize with PowerShell scripts
openhands spec init my-project --script-type ps
```

**Project Structure Created:**
```
project-name/
├── .specify/
│   ├── memory/
│   │   ├── constitution.md      # Project constitutional principles
│   │   └── best_practices.md    # Development guidelines
│   ├── templates/
│   │   ├── spec-template.md     # Specification template
│   │   ├── plan-template.md     # Implementation plan template
│   │   ├── tasks-template.md    # Task breakdown template
│   │   └── agent-file-template.md # Agent context template
│   ├── scripts/
│   │   └── bash/setup-plan.sh   # Automation scripts
│   └── commands/
│       └── README.md            # OpenHands integration notes
├── specs/                       # Generated specifications directory
└── .git/                       # Version control (unless --no-git)
```

---

### `openhands spec constitution`

Create or manage project constitutional principles.

**Syntax:**
```bash
openhands spec constitution [options]
```

**Options:**
- `--edit` - Open constitution file in editor for manual editing

**Examples:**
```bash
# Create constitutional template
openhands spec constitution

# Edit existing constitution
openhands spec constitution --edit
```

**Constitutional Framework:**
- Creates `.specify/memory/constitution.md` with template structure
- Includes core principles, decision frameworks, and constraints
- Serves as foundation for all project decisions
- Guides AI assistant responses and recommendations

---

### `openhands spec specify`

Create comprehensive project specifications through interactive dialog.

**Syntax:**
```bash
openhands spec specify [spec_name]
```

**Arguments:**
- `spec_name` - Name for the specification (auto-generated if not provided)

**Examples:**
```bash
# Create specification with auto-generated name
openhands spec specify

# Create specification with specific name
openhands spec specify user-auth-system

# Create specification for version 2
openhands spec specify webapp-v2
```

**Interactive Process:**
1. **Project Overview** - Title and purpose description
2. **Functional Requirements** - What the system must do
3. **Non-Functional Requirements** - How the system should behave
4. **User Stories** - From user perspective
5. **Technical Specifications** - Technology choices and constraints
6. **Success Metrics** - How to measure project success
7. **Dependencies** - External systems and services
8. **Assumptions** - What we assume to be true
9. **Open Questions** - Areas needing clarification

**Constitutional Validation:**
- Specifications automatically validated against constitutional principles
- Violations and conflicts identified
- Suggestions provided for constitutional alignment
- Option to revise or accept with warnings

**Output Files:**
- `specs/{spec_name}.md` - Comprehensive specification document
- `specs/{spec_name}.json` - Metadata and tracking information

---

### `openhands spec clarify`

Detect and resolve ambiguities in specifications through interactive workflows.

**Syntax:**
```bash
openhands spec clarify [options]
```

**Options:**
- `--spec <name>` - Specification to clarify (uses latest if not specified)

**Examples:**
```bash
# Clarify latest specification
openhands spec clarify

# Clarify specific specification
openhands spec clarify --spec user-auth-system
```

**Ambiguity Detection:**
The system automatically detects 6 types of ambiguities:

1. **Modal Verbs** - `should`, `could`, `might`, `may`
   - **Issue**: Creates uncertainty about requirements
   - **Resolution**: Replace with definitive language (`must`, `will`, `shall`)

2. **Vague Quantifiers** - `some`, `many`, `few`, `several`
   - **Issue**: Imprecise quantities
   - **Resolution**: Specify exact numbers or ranges

3. **Subjective Adjectives** - `fast`, `slow`, `easy`, `hard`, `simple`
   - **Issue**: Unmeasurable criteria
   - **Resolution**: Define with specific, measurable benchmarks

4. **Open-ended Lists** - `etc.`, `and so on`, `and more`
   - **Issue**: Incomplete specifications
   - **Resolution**: Complete the list or specify what's included

5. **UX Terms** - `user-friendly`, `intuitive`, `simple`
   - **Issue**: Undefined usability criteria
   - **Resolution**: Specify measurable usability standards

6. **Subjective Judgments** - `appropriate`, `suitable`, `reasonable`
   - **Issue**: Undefined evaluation criteria
   - **Resolution**: Establish specific criteria and standards

**Clarification Process:**
1. **Ambiguity Detection** - Automatic scanning and severity assessment
2. **Priority Ordering** - High severity issues addressed first
3. **Interactive Resolution** - Guided clarification questions
4. **Quality Validation** - Ensures clarifications are specific and measurable
5. **Specification Update** - Automatic updating with clarified language
6. **Documentation** - Clarification rationale preserved

**Output:**
- Updated specification with clarified language
- Clarification section documenting all changes
- New version with `_clarified_timestamp` suffix

---

### `openhands spec plan`

Generate comprehensive implementation plans from specifications.

**Syntax:**
```bash
openhands spec plan [options]
```

**Options:**
- `--spec <name>` - Specification to create plan for (uses latest if not specified)

**Examples:**
```bash
# Generate plan from latest specification
openhands spec plan

# Generate plan from specific specification
openhands spec plan --spec user-auth-system
```

**Plan Generation Process:**
1. **Load Specification** - Parse requirements and constraints
2. **Load Constitutional Context** - Apply constitutional principles
3. **Architecture Analysis** - Recommend system architecture
4. **Phase Breakdown** - Create manageable implementation phases
5. **Risk Assessment** - Identify and plan for potential issues
6. **Testing Strategy** - Define quality assurance approach
7. **Deployment Planning** - Strategy for production release

**Plan Structure:**
```markdown
# Implementation Plan: [Project Title]

## Architecture Overview
- System architecture recommendations
- Component breakdown
- Technology stack suggestions
- Integration patterns

## Implementation Phases
### Phase 1: Foundation
- Infrastructure and core systems
- Duration, tasks, deliverables

### Phase 2: Core Features
- Essential functionality implementation
- Duration, tasks, deliverables

### Phase 3: Enhancement
- Additional features and optimization
- Duration, tasks, deliverables

### Phase 4: Polish & Deployment
- Final testing and production release
- Duration, tasks, deliverables

## Technical Decisions
- Key technology choices with rationale
- Constitutional principle alignment

## Risk Assessment
- Potential risks and mitigation strategies
- Impact and probability analysis

## Testing Strategy
- Testing levels and approaches
- Coverage targets and quality gates

## Deployment Plan
- Environment strategy
- Release process and monitoring
```

**Constitutional Integration:**
- Plans incorporate constitutional principles throughout
- Risk assessment includes constitutional constraint analysis
- Testing strategy reflects constitutional quality requirements
- Deployment approach aligns with constitutional values

**Output Files:**
- `specs/plan_{spec_name}_{timestamp}.md` - Complete implementation plan
- `specs/plan_{spec_name}_{timestamp}.json` - Plan metadata and tracking

---

### `openhands spec tasks`

Generate actionable development tasks from implementation plans.

**Syntax:**
```bash
openhands spec tasks [options]
```

**Options:**
- `--plan <name>` - Plan to generate tasks for (uses latest if not specified)

**Examples:**
```bash
# Generate tasks from latest plan
openhands spec tasks

# Generate tasks from specific plan
openhands spec tasks --plan plan_webapp_20241104_120000
```

**Task Generation Process:**
1. **Load Implementation Plan** - Parse phases and high-level tasks
2. **Constitutional Context** - Apply constitutional prioritization
3. **Task Decomposition** - Break down high-level tasks into specific work items
4. **Effort Estimation** - Provide time estimates for each task
5. **Dependency Analysis** - Identify task dependencies and ordering
6. **Priority Assignment** - Use constitutional principles for prioritization

**Task Categories:**
- **Foundation** - Infrastructure, setup, core systems (High priority)
- **Core Features** - Essential functionality (High priority)
- **Enhancement** - Additional features and improvements (Medium priority)
- **Polish & Deployment** - Final testing and release (Medium priority)
- **Cross-Cutting Concerns** - Quality, security, documentation (High priority)

**Task Breakdown Example:**
```markdown
### Foundation
- [ ] **1.** Set up development environment (TypeScript, React, Node.js) *(3h)* `setup`
- [ ] **2.** Configure CI/CD pipeline with automated testing *(4h)* `setup`
- [ ] **3.** Implement JWT authentication middleware *(6h)* `development`
- [ ] **4.** Set up database with encryption and connection pooling *(4h)* `setup`

### Core Features
- [ ] **5.** Design and implement user data model *(4h)* `development`
- [ ] **6.** Create user registration and login API endpoints *(8h)* `development`
- [ ] **7.** Build responsive user interface components *(10h)* `development`
- [ ] **8.** Write comprehensive unit tests *(6h)* `testing`
```

**Constitutional Prioritization:**
- Tasks prioritized based on constitutional principles
- Security tasks elevated if constitution emphasizes security
- Quality tasks prioritized if constitution requires high standards
- User experience tasks prioritized for user-centered constitutions

**Output Files:**
- `specs/tasks_{plan_name}_{timestamp}.md` - Complete task breakdown
- `specs/tasks_{plan_name}_{timestamp}.json` - Task metadata and progress tracking

---

### `openhands spec analyze`

Perform comprehensive consistency analysis across all SDD artifacts.

**Syntax:**
```bash
openhands spec analyze [options]
```

**Options:**
- `--verbose` - Show detailed analysis output with specific issues
- `--project-dir <path>` - Project directory to analyze (default: current directory)

**Examples:**
```bash
# Basic consistency analysis
openhands spec analyze

# Detailed analysis with specific issues
openhands spec analyze --verbose

# Analyze specific project directory
openhands spec analyze --project-dir /path/to/project --verbose
```

**Analysis Dimensions:**

#### 1. Constitutional Alignment (0-100 score)
- **Validates** specifications against constitutional principles
- **Detects** principle violations and conflicts
- **Identifies** missing constitutional requirements
- **Suggests** alignment improvements

#### 2. Spec-Plan Alignment (0-100 score)
- **Verifies** implementation plans fulfill all specification requirements
- **Identifies** missing requirements in plans
- **Detects** orphaned features not tied to requirements
- **Analyzes** coverage gaps and alignment issues

#### 3. Plan-Task Coverage (0-100 score)
- **Ensures** tasks cover all implementation plan phases
- **Identifies** uncovered plan elements
- **Detects** orphaned tasks not tied to plan phases
- **Validates** task categorization and organization

#### 4. Requirement Traceability (0-100 score)
- **Tracks** requirements end-to-end from specification to tasks
- **Validates** complete traceability chain
- **Identifies** untraceable requirements
- **Creates** traceability matrix for audit purposes

#### 5. Gap Analysis (0-100 score)
- **Identifies** missing SDD artifacts
- **Detects** version conflicts between artifacts
- **Finds** naming inconsistencies
- **Validates** artifact completeness

**Sample Analysis Output:**
```
╭─────────── Overall Consistency Score ───────────╮
│ 89/100                                         │
╰────────────────────────────────────────────────╯

              Consistency Analysis Summary              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━┓
┃ Area                     ┃ Score ┃ Status   ┃ Issues ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━┩
│ Constitutional Alignment │    95 │ ✅ Good  │      1 │
│ Spec-Plan Alignment      │    92 │ ✅ Good  │      3 │
│ Plan-Task Coverage       │    87 │ ✅ Good  │      5 │
│ Requirement Traceability │    84 │ ✅ Good  │      4 │
│ Gap Analysis             │    88 │ ✅ Good  │      2 │
└──────────────────────────┴───────┴──────────┴────────┘

Recommendations:
   1. Review and align specifications with constitutional principles
   2. Update implementation plan to cover all specification requirements
   3. Generate tasks for all implementation plan phases
   4. Ensure all requirements are traceable through plan to tasks
```

**Verbose Output Includes:**
- Detailed issue descriptions
- Specific recommendations for each problem
- Constitutional violation explanations
- Missing requirement lists
- Traceability gap details

**Output Files:**
- `specs/consistency_analysis_{timestamp}.json` - Detailed analysis report (with `--verbose`)

---

### `openhands spec check`

Verify that all required tools and dependencies are available.

**Syntax:**
```bash
openhands spec check
```

**Tool Verification:**
- **git** - Version control system
- **openhands** - OpenHands CLI
- **python** - Python interpreter
- **code** - Visual Studio Code (optional)
- **cursor** - Cursor IDE (optional)
- **claude** - Claude CLI (optional)

**Example Output:**
```
Check Specification-Driven Development Tools

● Git version control ✓ (available)
● OpenHands CLI ✓ (available)  
● Python interpreter ✓ (available)
● Visual Studio Code ○ (not found)
● Cursor IDE ○ (not found)
● Claude CLI ○ (not found)

✓ Tool check complete!

Recommendations:
For the best experience, consider installing:
• git - Version control for your specifications
• code or cursor - IDE for editing specifications  
• claude - Additional AI assistant option
```

---

## AI Integration Commands

When working within an active OpenHands session in an SDD project, additional commands become available:

### `/sdd` or `/context`

Display current SDD context within OpenHands conversation.

**Example Output:**
```
🔍 Specification-Driven Development Context:
📜 Constitutional Principles: User-Centered | Quality First | Security by Design
📋 Specification: Task Management Application (clarified, 45 requirements)
✅ Progress: 23/67 tasks (34%) | Current Phase: Core Features
🎯 Next Task: Implement user authentication system (6h)
```

### `/progress`

Show detailed project progress and suggested next actions.

**Example Output:**
```
**SDD Artifacts**: ✅ Constitution | ✅ Specification | ✅ Plan | ✅ Tasks
**Task Progress**: 23/67 (34%)
**Current Phase**: Core Features (Week 4 of 12)
**Consistency Score**: 92/100

Suggested next actions:
  1. Work on next task: Implement user authentication system (6h)
  2. Regular code reviews per constitutional quality requirements
  3. Update documentation with current progress
  4. Schedule user feedback session per user-centered principles
```

---

## Global Options

These options are available for all `openhands spec` commands:

- `--project-dir <path>` - Project directory to operate on (default: current directory)
- `--config <file>` - Configuration file to use
- `--help` - Show command-specific help information

---

## Configuration

### Project Configuration

SDD projects can be configured through:

1. **Constitutional Framework** (`.specify/memory/constitution.md`)
   - Core project principles and values
   - Decision-making framework
   - Quality standards and constraints

2. **Template Customization** (`.specify/templates/`)
   - Modify specification templates
   - Customize plan templates  
   - Adjust task breakdown templates

3. **Script Configuration** (`.specify/scripts/`)
   - Automation scripts for workflows
   - Platform-specific implementations
   - Custom tool integrations

### AI Assistant Configuration

Configure AI assistant behavior through:
- **Constitutional Principles** - Guide AI responses and recommendations
- **Project Context** - Specifications provide AI with project understanding
- **Quality Standards** - Constitutional quality requirements influence AI suggestions

---

## Exit Codes

All commands return standard exit codes:
- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - Missing dependencies
- `4` - Project not found or invalid

---

## Examples and Use Cases

### Complete Workflow Example

```bash
# 1. Initialize new SDD project
openhands spec init my-app --ai openhands

# 2. Navigate to project
cd my-app

# 3. Create constitutional framework
openhands spec constitution

# 4. Create comprehensive specification
openhands spec specify webapp-v1

# 5. Resolve any ambiguities
openhands spec clarify

# 6. Generate implementation plan
openhands spec plan

# 7. Create actionable task breakdown
openhands spec tasks

# 8. Validate consistency
openhands spec analyze --verbose

# 9. Start AI-assisted development
openhands
```

### Ongoing Development Workflow

```bash
# Regular consistency checks during development
openhands spec analyze

# Update specifications as requirements evolve
openhands spec specify webapp-v2

# Regenerate plans and tasks for new requirements
openhands spec plan --spec webapp-v2
openhands spec tasks

# Clarify new ambiguities
openhands spec clarify --spec webapp-v2
```

### Team Collaboration Workflow

```bash
# Each team member initializes local SDD context
git clone project-repo
cd project-repo
openhands spec check

# Work with constitutional AI assistance
openhands

# Regular team consistency validation
openhands spec analyze --verbose
```

---

This comprehensive API reference provides all the information needed to effectively use the Constitutional AI Development Assistant for systematic, principled software development with AI assistance.

---

*For additional help, examples, and tutorials, see the [complete documentation](README.md).*