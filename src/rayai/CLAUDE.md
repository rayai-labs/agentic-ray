# CLAUDE.md

## Purpose of This Directory

This directory contains the core implementation of the Agentic Ray (RayAI) runtime: tool execution logic, distributed scheduling behavior, agent serving, sandbox integration, CLI tools, batch tools, and deployment utilities.

It is the heart of the system and provides the foundational abstractions for building distributed agentic applications.

## Directory Structure

- `base.py` - Core protocols and interfaces (`AgentProtocol`)
- `decorators.py` - Unified `@tool` decorator for Ray-distributed tool execution
- `serve.py` - `rayai.serve()` function for serving agents via HTTP
- `agent_base.py` - `rayai.Agent` base class for custom agents
- `batch.py` - Generic `BatchTool` for parallel execution of any registered tool
- `cli/` - Command-line interface for agent management (init, create-agent, up, analytics)
- `sandbox/` - Secure code execution with Docker/gVisor
- `deployment.py` - Ray Serve deployment utilities with streaming support
- `resource_loader.py` - Memory parsing utilities (`_parse_memory`)
- `utils.py` - `execute_tools()` for parallel/sequential tool execution

## Core API

### `@rayai.tool` - Unified Tool Decorator
```python
import rayai

# As decorator for custom functions
@rayai.tool
def search(query: str) -> str:
    """Search the web."""
    return results

# As decorator with explicit resources
@rayai.tool(num_cpus=2, memory="4GB")
def expensive_task(data: str) -> str:
    return process(data)

# As wrapper for framework tools
from langchain_community.tools import DuckDuckGoSearchRun
lc_search = rayai.tool(DuckDuckGoSearchRun())
```

### `rayai.serve()` - Agent Serving
```python
import rayai
from pydantic_ai import Agent

agent = Agent("openai:gpt-4", tools=[search])
rayai.serve(agent, name="myagent", num_cpus=1, memory="2GB")
```

### `rayai.Agent` - Base Class for Custom Agents
```python
from rayai import Agent

class MyAgent(Agent):
    tools = [search, analyze]

    async def run(self, query: str) -> str:
        result = await self.call_tool("search", query=query)
        return f"Found: {result}"
```

## Key Concepts an AI Should Know

- All external-facing abstractions should remain stable
- Tool execution must remain serializable because Ray will ship tasks to workers
- Sandbox execution must stay isolated; do not allow host-level operations unless explicitly whitelisted
- This layer should be lightweight and dependency-minimal
- **`@rayai.tool`**: Unified decorator/wrapper that works as both decorator and framework tool wrapper
- **Async-first tools**: Tools return awaitables for non-blocking parallel execution via `asyncio.gather()`
- **`rayai.serve()`**: Hybrid serve/register - blocks in main, registers when imported by `rayai up`
- **`rayai.Agent`**: Base class for custom agents without frameworks
- **`BatchTool`**: Lets LLMs call any registered tool by name with many inputs in parallel
- Tools decorated with `@tool` have `_rayai_tool`, `_remote_func`, `_tool_metadata`, and `_original_func` attributes

## How Code Here Is Intended to Be Used

- Agents call tools → tools become Ray tasks/actors
- Sandbox module executes untrusted code safely in isolated containers
- The `@rayai.tool` decorator works directly with any agent framework (Pydantic AI, LangChain, Agno)
- CLI provides commands for initializing projects, creating agents, and running with `rayai up`
- Deployment utilities create Ray Serve endpoints for agent serving

## Do / Don't

### ✅ Do:

- Add new capabilities behind clean interfaces
- Maintain clarity in serialization and Ray task signatures
- Expand sandbox capabilities cautiously with security in mind
- Keep dependencies minimal in core modules
- Use `rayai.serve()` for agent deployment

### ❌ Don't:

- Add heavyweight dependencies to core runtime
- Let untrusted code escape sandbox boundaries
- Create framework-specific code in the core runtime
- Modify security-critical sandbox code without review
- Introduce non-serializable objects in tool signatures

## Related Modules

- `examples/` for usage patterns and demonstrations
- `tests/` for validated expected behavior
- See subdirectory `CLAUDE.md` files for CLI and sandbox details
