# OpenHands SDK vs Platform: Comprehensive Comparison

## Quick Reference

| Aspect | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| **Type** | Embeddable Library | Complete Application |
| **Primary Use** | Build custom agents | Use ready-made agent |
| **Complexity** | Simple | Complex |
| **Dependencies** | Minimal | Extensive |
| **Setup Time** | Minutes | 5-10 minutes |
| **Learning Curve** | Moderate | Steep |
| **Customization** | High | Medium |

---

## 1. Core Agent Capabilities

| Feature | agent-sdk | OpenHands Platform | Winner |
|---------|-----------|-------------------|--------|
| Agent Execution Loop | ✅ Basic | ✅ Advanced state machine | Platform |
| LLM Integration | ✅ LiteLLM | ✅ LiteLLM | Tie |
| Number of Agent Types | 1 (Generic) | 7+ (Specialized) | Platform |
| Multi-turn Conversations | ✅ Yes | ✅ Yes | Tie |
| Context Management | ✅ Condenser | ✅ Advanced condenser | Platform |
| Event System | ✅ Callbacks | ✅ EventStream | Platform |
| State Persistence | ✅ Local files | ✅ Database + Files | Platform |
| Multi-agent Delegation | ❌ No | ✅ Yes | Platform |
| Stuck Detection | ✅ Basic | ✅ Advanced | Platform |

**Summary**: Platform has more sophisticated agent capabilities with multiple specialized agents.

---

## 2. Agent Implementations

| Agent Type | agent-sdk | OpenHands Platform | Description |
|------------|-----------|-------------------|-------------|
| Generic Agent | ✅ `Agent` | ✅ Base `Agent` | Configurable general-purpose agent |
| CodeAct Agent | ❌ | ✅ | Advanced coding with action-based approach |
| Browsing Agent | ❌ | ✅ | Web browsing specialist |
| LOC Agent | ❌ | ✅ | Lines-of-code focused agent |
| ReadOnly Agent | ❌ | ✅ | Safe exploration without modifications |
| Visual Browsing Agent | ❌ | ✅ | Visual web interaction |
| Dummy Agent | ❌ | ✅ | Testing and development |
| **Total** | **1** | **7+** | |

---

## 3. Runtime Environments

| Runtime Type | agent-sdk | OpenHands Platform | Isolation Level | Use Case |
|--------------|-----------|-------------------|-----------------|----------|
| Local Workspace | ✅ | ✅ | None | Development |
| Docker | ❌ | ✅ | Full | Production |
| Kubernetes | ❌ | ✅ | Full | Scale |
| Modal | ❌ | ✅ | Full | Serverless |
| E2B | ❌ | ✅ | Full | Cloud |
| Runloop | ❌ | ✅ | Full | API-based |
| Remote | ⚠️ Basic | ✅ Advanced | Varies | Distributed |
| **Total Options** | **2** | **7+** | | |

### Runtime Features Comparison

| Feature | agent-sdk | OpenHands Platform |
|---------|-----------|-------------------|
| Sandboxing | ❌ | ✅ |
| Action Execution Server | ❌ | ✅ |
| Plugin System | ❌ | ✅ (Jupyter, AgentSkills) |
| Browser Environment | ⚠️ Basic | ✅ BrowserGym |
| Environment Variables | ✅ | ✅ |
| Resource Limits | ❌ | ✅ |
| Network Isolation | ❌ | ✅ |

---

## 4. Tools and Actions

### SDK Tools (4 total)

| Tool | Purpose | Capabilities |
|------|---------|--------------|
| BashTool | Execute commands | Run bash commands |
| FileEditorTool | File operations | Read/write files |
| TaskTrackerTool | Task management | Track subtasks |
| BrowserToolSet | Web browsing | Basic web access |

### Platform Actions (10+ total)

| Action | Purpose | Additional Features |
|--------|---------|-------------------|
| CmdRunAction | Execute bash | Sandbox isolation |
| IPythonRunCellAction | Python execution | Jupyter integration |
| FileReadAction | Read files | Permission checks |
| FileWriteAction | Write files | Backup support |
| BrowseURLAction | Fetch web content | Advanced parsing |
| BrowseInteractiveAction | Interactive browsing | BrowserGym integration |
| AddTaskAction | Add subtasks | Plan management |
| ModifyTaskAction | Update tasks | Status tracking |
| AgentFinishAction | Complete task | Result reporting |
| AgentRejectAction | Reject task | Error handling |
| MessageAction | Send messages | Rich content |
| AgentDelegateAction | Delegate to agent | Multi-agent coordination |

### Tool Comparison Summary

| Metric | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| Total Tools/Actions | 4 | 10+ |
| Custom Tool Support | ✅ | ✅ |
| Sandbox Integration | ❌ | ✅ |
| Error Handling | Basic | Advanced |
| Observation Types | 4 | 7+ |

---

## 5. User Interfaces

| Interface Type | agent-sdk | OpenHands Platform | Target Users |
|----------------|-----------|-------------------|--------------|
| Python API | ✅ | ✅ | Developers |
| REST API | ✅ (agent-server) | ✅ | Integrators |
| WebSocket | ✅ (agent-server) | ✅ | Real-time apps |
| Web GUI | ❌ | ✅ | End users |
| CLI | ❌* | ✅ | Terminal users |
| VSCode Extension | ❌ | ✅ | IDE users |
| GitHub Action | ❌ | ✅ | CI/CD |
| **Total** | **3** | **7** | |

*Note: openhands-cli (separate package) uses the SDK to provide CLI

### Interface Features

| Feature | agent-sdk | OpenHands Platform |
|---------|-----------|-------------------|
| Real-time Updates | ✅ WebSocket | ✅ WebSocket + GUI |
| Authentication | ⚠️ Basic API key | ✅ Full auth system |
| Session Management | ⚠️ Basic | ✅ Advanced |
| Multi-user Support | ❌ | ⚠️ Limited |
| Interactive UI | ❌ | ✅ |

---

## 6. Security Features

| Security Feature | agent-sdk | OpenHands Platform | Impact |
|------------------|-----------|-------------------|--------|
| Confirmation Policies | ✅ 3 types | ✅ 3 types | High |
| Security Analyzer | ✅ LLM-based | ✅ LLM-based | High |
| Risk Assessment | ✅ 3 levels | ✅ 3 levels | High |
| Secret Management | ✅ SecretRegistry | ✅ Enhanced | Medium |
| Container Isolation | ❌ | ✅ Docker | Critical |
| Network Isolation | ❌ | ✅ | High |
| File System Restrictions | ❌ | ✅ | High |
| Resource Limits | ❌ | ✅ | Medium |

### Confirmation Policies

| Policy | Behavior | agent-sdk | OpenHands Platform |
|--------|----------|-----------|-------------------|
| NeverConfirm | Auto-approve all | ✅ | ✅ |
| AlwaysConfirm | Ask for every action | ✅ | ✅ |
| ConfirmRisky | Ask only for HIGH risk | ✅ | ✅ |

### Risk Levels

| Risk Level | Examples | Both Support |
|------------|----------|--------------|
| LOW | Read files, list directories | ✅ |
| MEDIUM | Write files, install packages | ✅ |
| HIGH | Delete files, system commands | ✅ |

---

## 7. Evaluation and Benchmarking

| Benchmark | agent-sdk | OpenHands Platform | Domain |
|-----------|-----------|-------------------|--------|
| SWE-bench | ❌ | ✅ | Software Engineering |
| WebArena | ❌ | ✅ | Web Navigation |
| MiniWoB | ❌ | ✅ | Web Interaction |
| VisualWebArena | ❌ | ✅ | Visual Web Tasks |
| Commit0 | ❌ | ✅ | Code Generation |
| Multi-SWE-bench | ❌ | ✅ | Extended SE Tasks |
| Custom Benchmarks | ⚠️ DIY | ✅ Framework | |

### Evaluation Infrastructure

| Component | agent-sdk | OpenHands Platform |
|-----------|-----------|-------------------|
| Experiment Manager | ❌ | ✅ |
| Evaluation Scripts | ❌ | ✅ |
| Result Analysis | ❌ | ✅ |
| Metrics Collection | ⚠️ Basic | ✅ Comprehensive |
| Benchmark Integration | ❌ | ✅ |
| Performance Tracking | ❌ | ✅ |

---

## 8. Integrations

| Integration | agent-sdk | OpenHands Platform | Purpose |
|-------------|-----------|-------------------|---------|
| MCP (Model Context Protocol) | ✅ | ✅ | Tool extensions |
| GitHub | ❌ | ✅ | Issue resolution, PRs |
| VSCode | ❌ | ✅ | IDE integration |
| Google Sheets | ❌ | ✅ | Data access |
| Slack | ❌ | ✅ | Notifications |
| Jupyter | ❌ | ✅ | Interactive Python |
| Redis | ❌ | ✅ | Caching |
| PostgreSQL | ❌ | ✅ | Persistence |
| Docker | ❌ | ✅ | Containerization |
| Kubernetes | ❌ | ✅ | Orchestration |
| **Total** | **1** | **10+** | |

### Integration Depth

| Integration | agent-sdk | OpenHands Platform | Depth |
|-------------|-----------|-------------------|-------|
| LiteLLM | ✅ Core | ✅ Core | Deep |
| MCP | ✅ Full | ✅ Full | Deep |
| GitHub | ❌ | ✅ Full | Deep |
| VSCode | ❌ | ✅ Extension | Deep |
| Others | ❌ | ✅ Various | Medium |

---

## 9. Deployment Options

### Deployment Characteristics

| Characteristic | agent-sdk | OpenHands Platform |
|----------------|-----------|-------------------|
| Deployment Type | Embedded library | Standalone application |
| Process Model | Single process | Multi-service |
| Storage | File-based | Database + Files |
| Multi-tenancy | ❌ | ⚠️ Limited |
| Docker Images | ❌ | ✅ Pre-built |
| Cloud Hosting | ⚠️ DIY | ✅ OpenHands Cloud |
| Load Balancing | ⚠️ DIY | ⚠️ Custom setup |
| Auto-scaling | ❌ | ⚠️ With K8s |

### Infrastructure Requirements

| Component | agent-sdk | OpenHands Platform |
|-----------|-----------|-------------------|
| Python Runtime | ✅ Required | ✅ Required |
| Docker | ❌ Optional | ✅ Recommended |
| Database | ❌ | ⚠️ Optional |
| Redis | ❌ | ⚠️ Optional |
| Web Server | ⚠️ agent-server | ✅ Built-in |
| Reverse Proxy | ❌ | ⚠️ Production |

---

## 10. Advanced Features

| Feature | agent-sdk | OpenHands Platform | Complexity |
|---------|-----------|-------------------|------------|
| Microagents | ❌ | ✅ | High |
| Long-term Memory | ❌ | ✅ | High |
| Code Critic | ❌ | ✅ | Medium |
| Linter Integration | ❌ | ✅ | Low |
| Issue Resolver | ❌ | ✅ | High |
| Stuck Detection | ✅ Basic | ✅ Advanced | Medium |
| Visualization | ⚠️ Basic | ✅ Rich | Medium |
| Title Generation | ✅ | ✅ | Low |
| Traffic Control | ❌ | ✅ | Medium |
| Confirmation Mode | ✅ | ✅ | Medium |

### Microagent System (Platform Only)

| Microagent | Purpose | Specialization |
|------------|---------|----------------|
| RepoStudyAgent | Repository analysis | Code understanding |
| VerifierAgent | Task verification | Quality assurance |
| PlannerAgent | Task planning | Strategy |
| DebuggerAgent | Bug fixing | Error resolution |

---

## 11. Developer Experience

### Documentation

| Aspect | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| Getting Started | ✅ Good | ✅ Excellent |
| API Reference | ✅ Complete | ✅ Complete |
| Architecture Docs | ✅ Good | ✅ Extensive |
| Tutorials | ✅ Basic | ✅ Comprehensive |
| Examples | ✅ Yes | ✅ Many |
| Troubleshooting | ⚠️ Basic | ✅ Detailed |
| Video Tutorials | ❌ | ⚠️ Some |

### Development Tools

| Tool | agent-sdk | OpenHands Platform |
|------|-----------|-------------------|
| Type Hints | ✅ | ✅ |
| Logging | ✅ Basic | ✅ Advanced |
| Debugging | ⚠️ Basic | ✅ Visualizers |
| Testing | ✅ Basic | ✅ Comprehensive |
| Hot Reload | ✅ | ✅ |
| Pre-commit Hooks | ⚠️ | ✅ |
| CI/CD | ⚠️ | ✅ |

### Code Quality

| Metric | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| Test Coverage | ~70% | ~80% |
| Type Coverage | ~90% | ~85% |
| Documentation | Good | Excellent |
| Code Style | Black + Ruff | Black + Ruff |
| Linting | ✅ | ✅ |

---

## 12. Performance Characteristics

| Metric | agent-sdk | OpenHands Platform | Unit |
|--------|-----------|-------------------|------|
| Startup Time | < 1 | 5-10 | seconds |
| Memory Footprint | 100-200 | 500-2000 | MB |
| CPU Usage (idle) | Low | Medium | % |
| Disk Space | < 100 | 500-1000 | MB |
| Network Overhead | Minimal | Medium | |
| LLM API Latency | Same | Same | ms |

### Scalability

| Aspect | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| Concurrent Conversations | Depends on implementation | Good with proper setup |
| Horizontal Scaling | ⚠️ DIY | ⚠️ Possible with K8s |
| Vertical Scaling | ✅ Easy | ✅ Easy |
| Resource Efficiency | ✅ High | ⚠️ Medium |

---

## 13. Cost Analysis

### Development Costs

| Cost Factor | agent-sdk | OpenHands Platform |
|-------------|-----------|-------------------|
| Initial Setup | Low | Medium |
| Development Time | High (build features) | Low (use existing) |
| Maintenance | High (custom code) | Low (updates provided) |
| Training | Medium | High (more complex) |
| Documentation | DIY | Provided |

### Runtime Costs

| Cost Factor | agent-sdk | OpenHands Platform |
|-------------|-----------|-------------------|
| Infrastructure | Minimal | Medium-High |
| LLM API | Same | Same |
| Storage | Minimal | Medium |
| Compute | Low | Medium-High |
| Monitoring | DIY | Built-in |
| Support | Community | Community + Commercial |

### Total Cost of Ownership (Estimated)

| Scenario | agent-sdk | OpenHands Platform |
|----------|-----------|-------------------|
| Small Project (1-2 devs) | $ | $$ |
| Medium Project (3-10 devs) | $$ | $$$ |
| Large Project (10+ devs) | $$$ | $$$$ |
| Enterprise | $$$$ | $$$$$ |

*Note: $ = Low, $$ = Medium, $$$ = High, $$$$ = Very High, $$$$$ = Enterprise*

---

## 14. Use Case Matrix

### When to Use agent-sdk

| Use Case | Priority | Reason |
|----------|----------|--------|
| Custom agent app | ⭐⭐⭐⭐⭐ | Full control over architecture |
| Embedded in existing app | ⭐⭐⭐⭐⭐ | Lightweight integration |
| Research/experimentation | ⭐⭐⭐⭐ | Clean foundation |
| Resource-constrained | ⭐⭐⭐⭐ | Minimal footprint |
| Domain-specific tools | ⭐⭐⭐⭐ | Easy customization |
| Prototype | ⭐⭐⭐ | Quick start |
| Single-user tool | ⭐⭐⭐ | Simple deployment |

### When to Use OpenHands Platform

| Use Case | Priority | Reason |
|----------|----------|--------|
| Ready-to-use agent | ⭐⭐⭐⭐⭐ | No development needed |
| Team collaboration | ⭐⭐⭐⭐⭐ | GUI and multi-user |
| GitHub integration | ⭐⭐⭐⭐⭐ | Built-in support |
| Benchmarking | ⭐⭐⭐⭐⭐ | Evaluation framework |
| Production deployment | ⭐⭐⭐⭐ | Battle-tested |
| Multi-agent workflows | ⭐⭐⭐⭐ | Delegation system |
| Sandboxed execution | ⭐⭐⭐⭐ | Security critical |

---

## 15. Feature Parity Matrix

### Core Features

| Feature | agent-sdk | OpenHands Platform | Parity |
|---------|-----------|-------------------|--------|
| LLM Integration | ✅ | ✅ | ✅ |
| Basic Agent | ✅ | ✅ | ✅ |
| Tool Execution | ✅ | ✅ | ✅ |
| Event System | ✅ | ✅ | ⚠️ Different |
| State Management | ✅ | ✅ | ⚠️ Different |
| Confirmation | ✅ | ✅ | ✅ |
| Security Analysis | ✅ | ✅ | ✅ |

### Extended Features

| Feature | agent-sdk | OpenHands Platform | Gap |
|---------|-----------|-------------------|-----|
| Multiple Agents | ❌ | ✅ | Large |
| Sandboxing | ❌ | ✅ | Large |
| GUI | ❌ | ✅ | Large |
| Benchmarking | ❌ | ✅ | Large |
| Integrations | ⚠️ MCP only | ✅ Many | Large |
| Microagents | ❌ | ✅ | Medium |
| Memory System | ❌ | ✅ | Medium |

---

## 16. Migration Considerations

### SDK → Platform Migration

| Aspect | Difficulty | Notes |
|--------|-----------|-------|
| Concepts | Easy | Similar foundations |
| Code Adaptation | Medium | Different APIs |
| Event System | Hard | Callbacks → EventStream |
| Runtime | Hard | Different abstraction |
| State Management | Medium | More complex |
| Overall | Medium-Hard | Significant refactoring |

### Platform → SDK Migration

| Aspect | Difficulty | Notes |
|--------|-----------|-------|
| Feature Loss | Hard | Many features unavailable |
| Code Extraction | Very Hard | Deep dependencies |
| Runtime Replacement | Very Hard | Complex system |
| Recommendation | ❌ | Start with SDK instead |

---

## 17. Community and Ecosystem

### Community Size

| Metric | agent-sdk | OpenHands Platform |
|--------|-----------|-------------------|
| GitHub Stars | Part of main repo | 35,000+ |
| Contributors | Subset | 200+ |
| Slack Members | Shared | 5,000+ |
| Active Issues | ~50 | ~200 |
| Monthly Commits | ~50 | ~500 |

### Support Channels

| Channel | agent-sdk | OpenHands Platform |
|---------|-----------|-------------------|
| Documentation | ✅ | ✅ |
| GitHub Issues | ✅ | ✅ |
| Slack Community | ✅ | ✅ |
| Email Support | ❌ | ⚠️ Enterprise |
| Commercial Support | ❌ | ✅ Available |
| Design Partner Program | ❌ | ✅ |

---

## 18. Decision Tree

```
Do you need a GUI?
├─ Yes → OpenHands Platform
└─ No
   └─ Do you need sandboxed execution?
      ├─ Yes → OpenHands Platform
      └─ No
         └─ Do you need multiple specialized agents?
            ├─ Yes → OpenHands Platform
            └─ No
               └─ Do you want to embed in existing app?
                  ├─ Yes → agent-sdk
                  └─ No
                     └─ Do you need GitHub integration?
                        ├─ Yes → OpenHands Platform
                        └─ No
                           └─ Do you want minimal dependencies?
                              ├─ Yes → agent-sdk
                              └─ No → Either works, choose based on preference
```

---

## 19. Quick Comparison Summary

### agent-sdk in 3 Points
1. **Lightweight library** for embedding agent capabilities
2. **Single generic agent** with 4 core tools
3. **Minimal dependencies** and simple architecture

### OpenHands Platform in 3 Points
1. **Complete application** with GUI and multiple interfaces
2. **7+ specialized agents** with multi-agent delegation
3. **Production-ready** with sandboxing and extensive integrations

### The Bottom Line

| Question | Answer |
|----------|--------|
| Want to build? | Use **agent-sdk** |
| Want to use? | Use **OpenHands Platform** |
| Need control? | Use **agent-sdk** |
| Need features? | Use **OpenHands Platform** |
| Resource constrained? | Use **agent-sdk** |
| Production ready? | Use **OpenHands Platform** |

---

## 20. Version Information

| Component | Version | Release Date |
|-----------|---------|--------------|
| agent-sdk | Latest from main | Rolling |
| OpenHands Platform | 0.59 | October 2024 |
| This Document | 1.0 | November 4, 2025 |

---

**Document Type**: Technical Comparison
**Format**: Markdown with Tables
**Intended Audience**: Developers, Technical Decision Makers
**Maintenance**: Update quarterly or on major releases
