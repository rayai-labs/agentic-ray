# CLAUDE.md

## Purpose of This Repository

This project provides a scalable runtime for agentic workloads, including AI agents, tool execution, MCP servers, and secure coding sandboxes. It uses Ray as the underlying distributed compute engine to schedule, parallelize, and isolate tool executions.

The goal is to make tool-heavy or multi-agent systems easy to scale across CPUs/GPUs while providing optional sandboxing (gVisor-like) for safe code execution.

## Architecture Overview

- **Ray-based Distribution**: Tool calls are executed as Ray tasks/actors, enabling automatic scaling and resource management
- **Framework Agnostic**: Works with any agent framework (Pydantic AI, LangChain, Agno) via unified `@rayai.tool` decorator
- **Sandbox Execution**: Secure code execution using Docker with gVisor runtime for isolation
- **MCP Integration**: Model Context Protocol support for structured tool communication
- **CLI Tools**: Command-line interface for agent creation, deployment, and management

## Core API

```python
import rayai
from pydantic_ai import Agent

# Unified tool decorator - works with any framework
@rayai.tool(num_cpus=1)
def search(query: str) -> str:
    """Search the web."""
    return f"Results for {query}"

# Create agent with your preferred framework
agent = Agent("openai:gpt-4", tools=[search])

# Serve via HTTP with Ray Serve
rayai.serve(agent, name="myagent", num_cpus=1, memory="2GB")
```

Run with `rayai up` or `python agents/myagent/agent.py`.

## Key Concepts an AI Should Know

- A "tool call" maps to a Ray task/actor, enabling distributed execution
- `@rayai.tool` works as both decorator and wrapper for framework tools (LangChain, Pydantic AI, Agno)
- Resource requirements can be specified via decorator args or docstring `ray:` blocks
- `rayai.serve()` auto-detects agent framework and creates HTTP endpoints
- Code execution happens inside controlled Docker sandboxes with gVisor for security isolation
- The repo is framework-agnostic; avoid coupling to any single agent architecture
- Sandbox executor manages Docker containers with resource limits, timeouts, and network isolation

## Project Structure Overview

- `src/rayai/` – core runtime, agents, tools, sandbox logic, adapters, CLI
- `examples/` – example uses of agents and tools on Ray (analyzer, finance_agent)
- `tests/` – unit tests for runtime execution, tool adapters, sandbox behavior
- `scripts/` – developer or cluster helper scripts (gVisor setup, Docker configuration)

## Technology Stack

- **Ray**: Distributed computing framework for task scheduling and resource management
- **Ray Serve**: Model serving and deployment
- **Docker + gVisor**: Container-based sandboxing with security isolation
- **FastAPI**: HTTP API layer for agent deployments
- **Pydantic AI**: Supported agent framework
- **LangChain/LangGraph**: Supported agent framework
- **Agno**: Supported agent framework

## Do / Don't for AI Modifying This Repo

### Do:

- Improve documentation comments and docstrings
- Refactor for clarity without breaking public APIs
- Add new adapters or sandbox capabilities behind clean interfaces
- Follow existing patterns for tool decoration and Ray integration
- Maintain security boundaries in sandbox execution
- Update examples when adding new features

### Don't:

- Create tight coupling to a specific agent framework
- Modify sandbox security boundaries without explicit review
- Introduce breaking API changes without updating examples/tests
- Add heavyweight dependencies to core runtime
- Bypass Ray's serialization requirements for tool execution
- Allow untrusted code to escape sandbox boundaries

## Related Modules

See subdirectory `CLAUDE.md` files for detailed directory purposes:

- `src/rayai/CLAUDE.md` - Core runtime implementation
- `src/rayai/cli/CLAUDE.md` - CLI tools
- `src/rayai/sandbox/CLAUDE.md` - Sandbox execution
- `examples/CLAUDE.md` - Example applications
- `tests/CLAUDE.md` - Test suite
