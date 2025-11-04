# Troubleshooting Guide

## Common Issues and Solutions

### Installation and Setup Issues

#### Issue: `openhands spec` command not found

**Symptoms:**
```bash
$ openhands spec --help
command not found: openhands spec
```

**Solution:**
1. Verify OpenHands CLI is installed:
```bash
pip install openhands-cli
```

2. Check if SDD integration is available:
```bash
openhands --help
# Look for 'spec' in subcommands list
```

3. Update to latest version:
```bash
pip install --upgrade openhands-cli
```

**Alternative Solution:**
If using virtual environment:
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install/upgrade OpenHands
pip install --upgrade openhands-cli
```

---

#### Issue: SDD project not detected

**Symptoms:**
```bash
$ openhands
# No SDD context banner appears
# AI agent doesn't have constitutional context
```

**Diagnosis:**
```bash
# Check project structure
ls -la .specify/
ls -la .specify/memory/constitution.md
```

**Solution:**
1. Ensure you're in an SDD project directory
2. Verify `.specify/` directory exists
3. Check constitution file exists:
```bash
# Initialize if missing
openhands spec constitution
```

4. Verify project structure:
```bash
# Should have this structure:
.specify/
├── memory/constitution.md
├── templates/
└── scripts/
```

---

### Specification Creation Issues

#### Issue: Constitutional validation fails

**Symptoms:**
```
⚠ Constitutional Alignment Issues Found:
• No security requirements found, violating 'Security First' principle
• No testing requirements found, violating 'Quality Standards' principle
```

**Solution:**
1. **Review constitutional principles** in `.specify/memory/constitution.md`
2. **Add missing requirements** to your specification:

```markdown
## Non-Functional Requirements
- System must use multi-factor authentication (Security principle)
- System must have 90% test coverage (Quality principle)
- All data must be encrypted at rest and in transit (Security principle)
```

3. **Re-run specification creation:**
```bash
openhands spec specify updated-spec
```

4. **Adjust constitution if needed:**
   - If constitutional requirements are too strict, modify constitution
   - If requirements are appropriate, update specification to meet them

---

#### Issue: Interactive specification dialog freezes

**Symptoms:**
- Specification creation stops accepting input
- Terminal becomes unresponsive during dialog

**Solution:**
1. **Cancel and restart:**
```bash
Ctrl+C  # Cancel current operation
openhands spec specify new-attempt
```

2. **Check terminal compatibility:**
```bash
# Test basic input
python3 -c "input('Test: ')"
```

3. **Use alternative input method:**
   - Prepare answers in advance
   - Use shorter, simpler responses
   - Skip optional sections if problematic

4. **Alternative approach:**
   - Edit specification template directly
   - Create minimal spec through dialog
   - Manually enhance specification file

---

### Clarification Workflow Issues

#### Issue: No ambiguities detected when some exist

**Symptoms:**
```
✓ No ambiguities detected in specification!
```
But specification contains vague language.

**Diagnosis:**
Check for these patterns that should be detected:
- Modal verbs: should, could, might, may
- Quantifiers: some, many, few, several
- Subjective terms: fast, easy, simple, user-friendly

**Solution:**
1. **Manual ambiguity review:**
```bash
# Search for problematic patterns
grep -i "should\|could\|might\|may" specs/your-spec.md
grep -i "fast\|slow\|easy\|hard" specs/your-spec.md
grep -i "some\|many\|few" specs/your-spec.md
```

2. **Update ambiguity patterns:**
   - The system may need additional pattern recognition
   - Manually clarify identified ambiguous language

3. **Re-run clarification:**
```bash
openhands spec clarify --spec your-spec
```

---

#### Issue: Clarification quality validation too strict

**Symptoms:**
```
⚠ Clarification could be more specific
Would you like to revise it?
```

**Solution:**
1. **Include specific measurements:**
```
BAD:  "The system should be fast"
GOOD: "The system must respond within 2 seconds for 95% of requests"
```

2. **Use definitive language:**
```
BAD:  "Users might want this feature"
GOOD: "Users must be able to complete this workflow"
```

3. **Provide measurable criteria:**
```
BAD:  "Interface should be user-friendly"
GOOD: "Interface must allow task completion with 95% success rate on first attempt"
```

---

### Plan and Task Generation Issues

#### Issue: Generated plan doesn't match specification

**Symptoms:**
- Plan missing key requirements from specification
- Plan includes features not in specification
- Phase breakdown doesn't align with project scope

**Diagnosis:**
```bash
# Check specification-plan alignment
openhands spec analyze --verbose
```

**Solution:**
1. **Verify specification quality:**
```bash
# Ensure specification is complete and clear
openhands spec clarify
```

2. **Regenerate plan:**
```bash
# Create new plan from clarified specification
openhands spec plan --spec clarified-spec-name
```

3. **Manual plan review:**
   - Review generated plan content
   - Compare with specification requirements
   - Add missing elements manually if needed

---

#### Issue: Task breakdown too vague or too detailed

**Symptoms:**
- Tasks like "Implement user management" (too vague)
- Tasks like "Add semicolon to line 47" (too detailed)

**Solution:**
1. **Review constitutional principles:**
   - Adjust quality standards in constitution
   - Modify task generation preferences

2. **Regenerate with different context:**
```bash
# Update specification with more detail
openhands spec specify enhanced-spec

# Generate new task breakdown
openhands spec tasks
```

3. **Manual task refinement:**
   - Edit task files directly for appropriate granularity
   - Break down overly large tasks
   - Combine overly small tasks

---

### AI Integration Issues

#### Issue: AI agent doesn't show SDD context

**Symptoms:**
```bash
$ openhands
Welcome to OpenHands CLI! 🙌
# No SDD detection banner
```

**Diagnosis:**
1. **Check SDD project structure:**
```bash
ls -la .specify/memory/constitution.md
```

2. **Verify OpenHands CLI version:**
```bash
openhands --version
```

**Solution:**
1. **Ensure SDD project setup:**
```bash
# Verify project is properly initialized
openhands spec check
```

2. **Restart OpenHands in SDD project:**
```bash
# Make sure you're in project root directory
cd /path/to/your/sdd-project
openhands
```

3. **Manual context verification:**
```bash
# Test SDD commands within OpenHands session
/sdd
/progress
```

---

#### Issue: AI responses don't reflect constitutional principles

**Symptoms:**
- AI suggests solutions that conflict with constitution
- AI doesn't reference constitutional principles
- AI responses seem generic rather than project-specific

**Solution:**
1. **Verify constitutional context loading:**
```bash
# Within OpenHands session
/sdd
# Should show constitutional principles
```

2. **Strengthen constitutional principles:**
   - Make principles more specific and actionable
   - Include measurement criteria
   - Add clear decision frameworks

3. **Provide explicit constitutional guidance:**
```
User: "Remember to consider our constitutional principle of 'Security First' 
when suggesting authentication approaches."
```

---

### Consistency Analysis Issues

#### Issue: Low consistency scores without clear reasons

**Symptoms:**
```
Overall Consistency Score: 45/100
```
But detailed analysis doesn't show major issues.

**Solution:**
1. **Run verbose analysis:**
```bash
openhands spec analyze --verbose
```

2. **Address specific issues:**
   - Follow recommendations provided
   - Focus on lowest-scoring areas first
   - Check for missing artifacts

3. **Verify all artifacts exist:**
```bash
ls -la specs/
# Should have: constitution, specification, plan, tasks
```

---

#### Issue: False positive consistency issues

**Symptoms:**
- Analysis reports issues that don't actually exist
- Traceability problems for properly traced requirements

**Solution:**
1. **Manual verification:**
   - Review reported issues manually
   - Check if analysis correctly understands content

2. **Improve artifact clarity:**
   - Use more consistent terminology across artifacts
   - Ensure requirements are clearly stated
   - Add explicit traceability markers

3. **Document known limitations:**
   - Analysis may struggle with complex language
   - Some valid patterns might not be recognized

---

## Platform-Specific Issues

### Windows Issues

#### Issue: PowerShell script execution policy

**Symptoms:**
```
execution of scripts is disabled on this system
```

**Solution:**
```powershell
# Set execution policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run specific script
powershell -ExecutionPolicy Bypass -File .specify/scripts/powershell/setup-plan.ps1
```

#### Issue: Path separator issues

**Symptoms:**
- File paths with wrong separators
- Cannot find specification files

**Solution:**
```bash
# Use forward slashes or double backslashes
openhands spec plan --spec "webapp-v1"
# Not: openhands spec plan --spec "webapp\v1"
```

### macOS Issues

#### Issue: Permission denied errors

**Symptoms:**
```
Permission denied: .specify/scripts/bash/setup-plan.sh
```

**Solution:**
```bash
# Make scripts executable
chmod +x .specify/scripts/bash/*.sh

# Or run specific script
bash .specify/scripts/bash/setup-plan.sh
```

### Linux Issues

#### Issue: Missing dependencies

**Symptoms:**
```
ModuleNotFoundError: No module named 'rich'
```

**Solution:**
```bash
# Install with pip
pip install rich

# Or reinstall OpenHands CLI
pip install --upgrade --force-reinstall openhands-cli
```

---

## Performance Issues

#### Issue: Slow specification creation

**Symptoms:**
- Long delays during interactive dialog
- Slow constitutional validation

**Solution:**
1. **Simplify constitutional principles:**
   - Reduce number of principles
   - Simplify validation logic

2. **Reduce specification complexity:**
   - Break large specifications into smaller ones
   - Use shorter requirement descriptions

3. **Check system resources:**
   - Ensure adequate memory available
   - Close unnecessary applications

---

#### Issue: Large project analysis takes too long

**Symptoms:**
- `openhands spec analyze` runs for minutes
- System becomes unresponsive during analysis

**Solution:**
1. **Use basic analysis:**
```bash
# Skip verbose mode for large projects
openhands spec analyze
```

2. **Analyze specific artifacts:**
   - Focus on most recent specifications
   - Remove outdated artifacts from specs/

3. **Break down analysis:**
   - Analyze constitutional alignment separately
   - Check specific artifact relationships

---

## Data and File Issues

#### Issue: Corrupted specification files

**Symptoms:**
- JSON parsing errors
- Malformed markdown files
- Missing metadata

**Solution:**
1. **Backup and recreate:**
```bash
# Backup existing files
cp specs/broken-spec.md specs/broken-spec.md.backup

# Recreate specification
openhands spec specify fixed-spec
```

2. **Manual file repair:**
   - Check JSON syntax in metadata files
   - Verify markdown structure in specification files
   - Restore from git history if available

---

#### Issue: Git integration problems

**Symptoms:**
- Cannot initialize git repository
- Git commands fail during project setup

**Solution:**
1. **Manual git setup:**
```bash
git init
git add .
git commit -m "Initial SDD project setup"
```

2. **Skip git integration:**
```bash
openhands spec init my-project --no-git
```

3. **Check git configuration:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Recovery Procedures

### Complete Project Recovery

If your SDD project becomes corrupted:

1. **Backup existing work:**
```bash
cp -r .specify .specify.backup
cp -r specs specs.backup
```

2. **Reinitialize project:**
```bash
# Remove corrupted SDD structure
rm -rf .specify specs

# Reinitialize
openhands spec init --here
```

3. **Restore content:**
   - Copy constitutional content from backup
   - Recreate specifications using backed-up content
   - Regenerate plans and tasks

### Specification Recovery

If specifications become corrupted:

1. **Identify latest good version:**
```bash
ls -la specs/*.md
# Look for recent, complete files
```

2. **Use git history:**
```bash
git log --oneline specs/
git checkout <commit> -- specs/good-spec.md
```

3. **Recreate from scratch:**
```bash
openhands spec specify recovered-spec
# Use backed-up content as reference
```

---

## Getting Help

### Enable Verbose Logging

For debugging issues:

```bash
# Add verbose output
openhands spec analyze --verbose

# Check system information
openhands spec check
```

### Collect Debug Information

When reporting issues, collect:

1. **System information:**
```bash
python --version
pip show openhands-cli
openhands --version
```

2. **Project structure:**
```bash
tree .specify
ls -la specs/
```

3. **Error messages:**
   - Copy complete error output
   - Include command that caused error
   - Note when error started occurring

### Common Command Patterns

```bash
# Diagnosis commands
openhands spec check                    # Verify tool availability
openhands spec analyze --verbose       # Detailed consistency analysis
ls -la .specify/                       # Check project structure

# Recovery commands
openhands spec constitution             # Recreate constitution
openhands spec specify recovery-spec    # Recreate specification
openhands spec plan                     # Regenerate plan
openhands spec tasks                    # Regenerate tasks

# Verification commands
openhands spec clarify                  # Check for ambiguities
openhands spec analyze                  # Verify consistency
```

---

## Known Limitations

### Current System Limitations

1. **Language Support:**
   - Ambiguity detection optimized for English
   - Constitutional principles assume English text

2. **Complexity Handling:**
   - Very large specifications may have performance issues
   - Complex constitutional frameworks may slow validation

3. **Integration Scope:**
   - Focus on OpenHands CLI integration
   - Limited integration with other development tools

### Workarounds

1. **For non-English projects:**
   - Use English for constitutional principles
   - Translate key requirements for analysis

2. **For large projects:**
   - Break specifications into multiple smaller documents
   - Use modular constitutional frameworks

3. **For complex requirements:**
   - Simplify language while maintaining precision
   - Use structured formats for complex dependencies

---

*For additional support, see the [complete documentation](README.md) or join the community discussions.*