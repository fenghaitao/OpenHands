# OpenHands SDK vs Platform: Comprehensive Comparison

## Executive Summary

The **OpenHands agent-sdk** and **OpenHands Platform** serve different purposes in the AI agent ecosystem:

- **agent-sdk**: A lightweight, embeddable library for building custom AI coding agents
- **OpenHands Platform**: A complete, production-ready application for AI-powered software development

The SDK provides the core engine, while the Platform provides a fully-featured vehicle ready to drive.

---

## 1. Core Agent Capabilities

### agent-sdk
The SDK provides fundamental agent capabilities:
- Basic agent execution loop with LLM integration via LiteLLM
- Single generic `Agent` class that can be configured
- Event-based architecture using callbacks
- Context management with LLM-based condensers
- Multi-turn conversation support
- Local file-based state persistence
- Four core tools: BashTool, FileEditorTool, TaskTrackerTool, BrowserToolSet

### OpenHands Platform
The Platform extends these capabilities significantly:
- Advanced state machine with sophisticated control flow
- Seven specialized agent implementations (CodeAct, Browsing, LOC, ReadOnly, Visual Browsing, Dummy, and base Agent)
- Multi-agent delegation system where agents can call other agents for help
- EventStream architecture as the central communication backbone
- Database-backed persistence with PostgreSQL support
- Extended action system with 10+ action types
- Plugin architecture for extensibility

**Key Difference**: SDK provides one configurable agent; Platform provides multiple specialized agents that can work together.

---

## 2. Runtime Environments

### agent-sdk
Runtime capabilities are minimal:
- LocalWorkspace for file operations in a local directory
- Basic RemoteConversation for connecting to remote agent servers
- No sandboxing - runs in the same environment as the calling code
- Direct filesystem access

### OpenHands Platform
Extensive runtime options with full isolation:
- **Docker Runtime**: Full container isolation with action execution server
- **Kubernetes Runtime**: Scalable deployment on K8s clusters
- **Modal Runtime**: Serverless execution via Modal API
- **E2B Runtime**: Cloud-based code execution environments
- **Runloop Runtime**: Integration with Runloop API
- **Remote Runtime**: Custom HTTP API for remote environments
- **Local Runtime**: Direct local execution (similar to SDK)

Additional runtime features:
- Action Execution Server running inside sandboxes
- Plugin system (Jupyter, AgentSkills, etc.)
- Browser environment with BrowserGym integration
- Environment variable management
- User environment initialization

**Key Difference**: SDK runs in your process; Platform runs in isolated sandboxes with multiple deployment options.

---

## 3. Tool System

### agent-sdk
Four core tools registered via the tool registry:
- **BashTool**: Execute bash commands
- **FileEditorTool**: Read and write files
- **TaskTrackerTool**: Track subtasks and progress
- **BrowserToolSet**: Basic web browsing capabilities

Custom tools can be added via `register_tool()` function.

### OpenHands Platform
Rich action system with specialized implementations:
- **CmdRunAction**: Execute bash commands in sandbox
- **IPythonRunCellAction**: Execute Python code in Jupyter notebook
- **FileReadAction**: Read file contents
- **FileWriteAction**: Write to files
- **BrowseURLAction**: Fetch web content
- **BrowseInteractiveAction**: Interactive web browsing
- **AddTaskAction**: Add subtasks to the plan
- **ModifyTaskAction**: Update subtask status
- **AgentFinishAction**: Complete the task
- **AgentRejectAction**: Reject and stop
- **MessageAction**: Send messages
- **AgentDelegateAction**: Delegate to another agent

Each action has corresponding observations and sophisticated error handling.

**Key Difference**: SDK has 4 tools; Platform has 10+ actions with richer functionality and sandbox integration.

---

## 4. User Interfaces

### agent-sdk
API-only approach:
- Python API for programmatic access
- agent-server provides REST API and WebSocket endpoints
- No built-in user interface
- Designed to be embedded in other applications

The openhands-cli (separate package) uses the SDK to provide a terminal interface.

### OpenHands Platform
Multiple interface options:
- **Web GUI**: Full-featured React-based frontend at localhost:3000
- **REST API**: Comprehensive HTTP API for all operations
- **WebSocket**: Real-time event streaming
- **CLI**: Command-line interface (legacy V0 CLI)
- **VSCode Extension**: Integrated development environment plugin
- **GitHub Action**: CI/CD integration for automated workflows

**Key Difference**: SDK is headless; Platform provides rich user interfaces for different use cases.

---

## 5. Security and Confirmation

### agent-sdk
Core security features:
- Three confirmation policies: AlwaysConfirm, NeverConfirm, ConfirmRisky
- LLMSecurityAnalyzer for risk assessment
- Risk levels: LOW, MEDIUM, HIGH
- SecretRegistry for managing API keys and secrets
- User confirmation workflow before executing actions

Security relies on the calling application to provide isolation.

### OpenHands Platform
Enhanced security with sandboxing:
- Same confirmation policies as SDK
- Same LLMSecurityAnalyzer
- Docker-based sandboxing for complete isolation
- Network isolation options
- File system restrictions
- Resource limits (CPU, memory)
- Hardened Docker installation guide for production

**Key Difference**: SDK provides security policies; Platform adds container-level isolation.

---

## 6. Evaluation and Benchmarking

### agent-sdk
No built-in evaluation framework:
- Basic ConversationStats for metrics
- No benchmark integrations
- Developers must build their own evaluation

### OpenHands Platform
Comprehensive evaluation system:
- **SWE-bench**: Software engineering benchmark
- **WebArena**: Web navigation benchmark
- **MiniWoB**: Web interaction tasks
- **VisualWebArena**: Visual web tasks
- **Commit0**: Code generation benchmark
- **Multi-SWE-bench**: Extended SWE-bench variants

Full experiments folder with:
- Experiment manager
- Evaluation scripts
- Result analysis tools
- Metrics collection and reporting

**Key Difference**: SDK has no evaluation; Platform has extensive benchmarking infrastructure.

---

## 7. Integrations

### agent-sdk
Minimal integrations:
- **MCP (Model Context Protocol)**: Connect to MCP servers for additional tools
- LiteLLM for LLM provider abstraction

### OpenHands Platform
Extensive integration ecosystem:
- **MCP**: Full Model Context Protocol support
- **GitHub**: Issue resolver, PR creation, repository analysis
- **VSCode**: Editor extension for in-IDE agent access
- **Google Sheets**: Spreadsheet integration
- **Slack**: Notifications and webhooks
- **Jupyter**: Interactive Python notebook support
- **Redis**: Caching and session management
- **PostgreSQL**: Database persistence
- **Docker**: Container orchestration
- **Kubernetes**: Cloud deployment

**Key Difference**: SDK focuses on core functionality; Platform integrates with the entire development ecosystem.

---

## 8. Deployment and Scalability

### agent-sdk
Designed for embedding:
- Single-process execution
- File-based storage
- No multi-tenancy support
- Lightweight and portable
- Can be embedded in any Python application
- agent-server provides basic HTTP interface

Ideal for:
- Custom applications
- Internal tools
- Prototypes and experiments
- Single-user scenarios

### OpenHands Platform
Production-ready deployment:
- Multi-service architecture
- Database-backed persistence
- Session management with ConversationManager
- Docker images pre-built and published
- OpenHands Cloud for managed hosting
- Kubernetes deployment options
- Load balancing possible with custom setup

Note: Not designed for multi-tenant SaaS (single-user per instance).

**Key Difference**: SDK is a library to embed; Platform is an application to deploy.

---

## 9. Advanced Features

### agent-sdk
Core features only:
- Stuck detection to prevent infinite loops
- Basic conversation visualization
- Title generation for conversations
- Context condensation when history is too long
- Async callback wrappers for event handling

### OpenHands Platform
Rich feature set:
- **Microagents**: Specialized sub-agents for specific tasks (RepoStudyAgent, VerifierAgent)
- **Memory System**: Long-term memory across conversations
- **Critic System**: Automated code review and quality checks
- **Linter Integration**: Code quality enforcement
- **Resolver**: Automated issue resolution from GitHub
- **Advanced Stuck Detection**: More sophisticated loop prevention
- **Conversation Visualizer**: Rich visualization of agent behavior
- **Multi-agent Delegation**: Agents can delegate to specialists
- **Traffic Control**: Rate limiting and resource management
- **Confirmation Mode**: Interactive approval workflow

**Key Difference**: SDK provides building blocks; Platform provides complete workflows.

---

## 10. Developer Experience

### agent-sdk
Clean and minimal:
- Well-documented Python API
- Type hints throughout
- Examples in the repository
- Basic logging with get_logger()
- Simple testing setup
- Fast iteration with hot reload in agent-server
- Small dependency footprint

Documentation focuses on:
- Getting started guide
- API reference
- Architecture overview
- Custom tool creation

### OpenHands Platform
Comprehensive tooling:
- Extensive documentation site
- Multiple tutorials and guides
- Advanced logging and debugging
- Conversation visualizers for debugging
- Pre-commit hooks
- Comprehensive test suite
- Development Docker setup
- Contribution guidelines

Documentation includes:
- User guides for all interfaces
- Architecture deep-dives
- Runtime configuration
- Troubleshooting guides
- Benchmark results
- Research papers

**Key Difference**: Both have good DX; Platform has more extensive documentation and tooling.

---

## 11. Architecture Comparison

### agent-sdk Architecture
```
Application Code
    ↓
openhands-sdk
    ├── Agent (generic)
    ├── LocalConversation
    ├── LLM (via LiteLLM)
    ├── Tools (4 core tools)
    ├── LocalWorkspace
    └── Event callbacks
    ↓
openhands-tools
    ├── BashTool
    ├── FileEditorTool
    ├── TaskTrackerTool
    └── BrowserToolSet
```

Simple, linear architecture focused on core agent loop.

### OpenHands Platform Architecture
```
User Interface (GUI/CLI/API)
    ↓
Server Layer
    ├── FastAPI Server
    ├── Session Manager
    ├── WebSocket Handler
    └── Authentication
    ↓
Controller Layer
    ├── AgentController
    ├── State Management
    └── EventStream (central hub)
    ↓
Agent Layer
    ├── CodeActAgent
    ├── BrowsingAgent
    ├── LOCAgent
    ├── ReadOnlyAgent
    └── Multi-agent Delegation
    ↓
Runtime Layer
    ├── Docker Runtime
    ├── Kubernetes Runtime
    ├── Modal Runtime
    ├── E2B Runtime
    └── Action Execution Server
    ↓
Tool/Plugin Layer
    ├── Bash/IPython
    ├── File Operations
    ├── Browser Environment
    ├── Jupyter Plugin
    └── Custom Plugins
```

Complex, layered architecture with EventStream as the communication backbone.

**Key Difference**: SDK is a library; Platform is a multi-layered application.

---

## 12. Use Case Scenarios

### When to Use agent-sdk

**Scenario 1: Custom Agent Application**
You're building a specialized coding assistant for your company's internal tools. You need agent capabilities but want full control over the UI and workflow.

**Scenario 2: Embedded Agent**
You have an existing application and want to add AI agent capabilities without running a separate service.

**Scenario 3: Research and Experimentation**
You're researching new agent architectures and need a clean, minimal foundation to build upon.

**Scenario 4: Lightweight Deployment**
You need agent capabilities in a resource-constrained environment where the full platform is too heavy.

**Scenario 5: Custom Tool Development**
You're building domain-specific tools and want to integrate them with a basic agent framework.

### When to Use OpenHands Platform

**Scenario 1: Ready-to-Use Coding Agent**
You want to start using an AI coding assistant immediately without building anything.

**Scenario 2: Team Collaboration**
Your team needs a shared environment for AI-assisted development with a GUI.

**Scenario 3: GitHub Integration**
You want automated issue resolution and PR creation from your repository.

**Scenario 4: Benchmarking and Evaluation**
You need to evaluate agent performance on standard benchmarks like SWE-bench.

**Scenario 5: Production Deployment**
You need a production-ready system with sandboxing, monitoring, and scalability.

**Scenario 6: Multi-Agent Workflows**
You need specialized agents working together (browsing + coding + verification).

---

## 13. Migration Path

### From SDK to Platform
If you start with the SDK and later need Platform features:

**Easy Migration**:
- Core concepts are the same (Agent, LLM, Tools, Events)
- SDK code can often be adapted to Platform with minimal changes
- Platform includes the SDK concepts as a foundation

**Challenges**:
- Platform uses EventStream instead of callbacks
- Different action/observation types
- Runtime abstraction is different
- State management is more complex

### From Platform to SDK
If you want to extract Platform functionality into a custom app:

**Possible but Challenging**:
- Platform has many interdependencies
- EventStream is deeply integrated
- Runtime system is complex
- Better to use SDK from the start for custom apps

**Recommendation**: Use SDK if you plan to build custom; use Platform if you want ready-made.

---

## 14. Performance Characteristics

### agent-sdk
- **Startup Time**: Fast (< 1 second)
- **Memory Footprint**: Small (~100-200 MB)
- **Dependencies**: Minimal
- **Overhead**: Low
- **Scalability**: Depends on your implementation

### OpenHands Platform
- **Startup Time**: Moderate (5-10 seconds with Docker)
- **Memory Footprint**: Larger (~500 MB - 2 GB with containers)
- **Dependencies**: Extensive
- **Overhead**: Higher due to sandboxing
- **Scalability**: Good with proper infrastructure

**Key Difference**: SDK is lightweight; Platform trades performance for features and safety.

---

## 15. Cost Considerations

### agent-sdk
**Development Costs**:
- Lower initial cost (just the SDK)
- Higher development time (build your own UI/features)
- Ongoing maintenance of custom code

**Runtime Costs**:
- Minimal infrastructure (just your app)
- LLM API costs only
- No additional services needed

### OpenHands Platform
**Development Costs**:
- Higher initial cost (more complex setup)
- Lower development time (features included)
- Less custom code to maintain

**Runtime Costs**:
- Docker/container infrastructure
- Database if using persistence
- LLM API costs
- Potential cloud hosting costs
- OpenHands Cloud option available

**Key Difference**: SDK has lower runtime costs but higher development costs; Platform is the opposite.

---

## 16. Community and Support

### agent-sdk
- Part of the OpenHands ecosystem
- Smaller, focused community
- Documentation at docs.openhands.dev/sdk
- GitHub issues and discussions
- Slack community

### OpenHands Platform
- Large, active community
- Extensive documentation
- Regular updates and releases
- Research papers and benchmarks
- Commercial support available
- Design partner program
- Slack community with more activity

**Key Difference**: Platform has larger community and more resources.

---

## 17. Future Roadmap

### agent-sdk
Focus areas:
- Stability and API refinement
- Core agent capabilities
- Tool ecosystem expansion
- Performance optimization
- Better remote conversation support

### OpenHands Platform
Focus areas:
- More specialized agents
- Enhanced multi-agent coordination
- Better evaluation frameworks
- Enterprise features
- Cloud platform expansion
- More integrations
- Improved UI/UX

**Key Difference**: SDK focuses on core; Platform expands features.

---

## Summary Decision Matrix

| Factor | Choose SDK | Choose Platform |
|--------|-----------|-----------------|
| **Need GUI** | No | Yes |
| **Custom Application** | Yes | No |
| **Quick Start** | No | Yes |
| **Minimal Dependencies** | Yes | No |
| **Sandboxed Execution** | No | Yes |
| **Multiple Agents** | No | Yes |
| **Benchmarking** | No | Yes |
| **GitHub Integration** | No | Yes |
| **Embed in Existing App** | Yes | No |
| **Production Ready** | Build it | Yes |
| **Resource Constrained** | Yes | No |
| **Team Collaboration** | Build it | Yes |

---

## Conclusion

The **OpenHands agent-sdk** and **OpenHands Platform** are complementary tools in the AI agent ecosystem:

**agent-sdk** is perfect for developers who want to:
- Build custom agent applications
- Integrate agents into existing systems
- Have full control over the architecture
- Keep dependencies minimal
- Create specialized agent solutions

**OpenHands Platform** is ideal for users who want to:
- Use a ready-made coding agent immediately
- Leverage specialized agents for different tasks
- Have a complete UI and deployment solution
- Benefit from extensive integrations
- Run agents in isolated, secure environments

The SDK provides the engine; the Platform provides the complete vehicle. Choose based on whether you want to build or drive.

---

**Document Version**: 1.0
**Last Updated**: November 4, 2025
**Author**: AI Assistant Analysis
