# Building production-ready AI Agents: From 98% token savings to scalable infrastructure

Anthropic recently published a [compelling piece](https://www.anthropic.com/engineering/code-execution-with-mcp) on code execution with the Model Context Protocol (MCP). By having agents write code instead of making direct tool calls, they observed a reduction in token usage from 150,000 to 2,000 tokens—a **98.7% reduction**.

## The Key Insight

The direct tool calling approach has a fundamental limitation. When you connect an agent to dozens or hundreds of tools, every tool definition consumes your context budget, and intermediate results pass through the model repeatedly.

Anthropic's solution is elegant: instead of tool calls, agents write Python code to interact with MCP servers. The agent discovers available tools by exploring a filesystem structure, loads only what it needs, and processes data in the execution environment before returning results to the model.

Rather than sending a 100KB CSV through the model three times, the agent writes code once to load the data, process it in a sandbox, and return only the summary. The model sees only the final results—not the raw data. Token usage drops by over 98%.

## The Real Challenge: Production Infrastructure

This technique works. But deploying it in production is where things get hard.

Code execution requires secure sandboxing, resource limits, and monitoring. You need:

- **Sandboxing**: gVisor isolation to safely execute untrusted code
- **Session management**: Maintaining persistent Python environments across user turns
- **Volume mounts**: Securely exposing datasets and MCP servers to the sandbox
- **Resource limits**: CPU, memory, and timeout enforcement
- **MCP server deployment**: Running and scaling MCP servers
- **Monitoring**: Tracking execution failures, token usage, and performance
- **Container orchestration**: Building, caching, and distributing Docker images

And this is just for *one* agent. What if you're building a platform? What if you have multiple agents, each with different tool requirements? What if you need to deploy custom MCP servers for your users?

The infrastructure gap is real.

## Infrastructure for Agent Builders

This is what we're building at RayAI: **production-grade infrastructure for deploying AI agents, MCP servers, and code sandboxes**.

Our platform runs on Ray, giving you:

### 1. Managed Code Sandboxes

Deploy secure, isolated execution environments with one function call:

```python
from ray_agents import execute_code
import ray

result = ray.get(execute_code.remote(
    code="""
    import pandas as pd
    df = pd.read_csv('/mnt/datasets/sales.csv')
    print(df.describe())
    """,
    session_id="user-123",
    volumes={
        "/path/to/datasets": {"bind": "/mnt/datasets", "mode": "ro"}
    },
    timeout=60
))
```

We handle:
- gVisor sandboxing
- Session persistence
- Volume mounting
- Resource limits
- Container lifecycle

### 2. Scalable MCP Servers

Deploy MCP servers as Ray Serve endpoints. Following Anthropic's approach, tools are exposed as a filesystem structure. Agents discover tools by navigating the filesystem and load only what they need:

**How it works:**
- MCP servers run as Ray Serve HTTP endpoints outside the sandbox
- Python wrappers are organized as a filesystem at `/mnt/servers/` (e.g., `servers/filesystem/list_directory.py`) inside the sandbox.
- Agents explore the filesystem to discover tools and write code to import and use the tools they need

**Example wrapper:**
```python
"""List datasets tool wrapper for datasets MCP server."""

from typing import Any
from ..mcp_client import call_mcp_tool

async def list_datasets() -> dict[str, Any]:
    """List available datasets.

    Returns:
        Dictionary containing:
        - datasets: List of dataset names (filenames only, no paths)
        - error: Error message (if failed)

    Example:
        >>> result = await list_datasets()
        >>> if "datasets" in result:
        ...     for name in result["datasets"]:
        ...         print(name)
    """
    return await call_mcp_tool("datasets", "list_datasets", {})
```

**Agent-generated code to discover the server filesystem:**
[Executing code]
```python
import os
print(os.listdir('/mnt/servers'))
```

### 3. Framework-Agnostic Agent Runtime

Our agent runtime integrates with any framework—LangGraph, CrewAI, AutoGen—through a simple adapter pattern. The key advantage: **agents become resource-aware**. When your agent calls a tool, Ray automatically routes it to nodes with the right resources (GPUs, CPUs, memory).

```python
import ray
from ray import serve
from ray_agents import AgentSession
from ray_agents.adapters import LangGraphAdapter

# Tools declare their resource requirements
@ray.remote(num_gpus=1)
def generate_image(prompt: str):
    """Generate an image using Stable Diffusion"""
    return "image.png"  # Executes on GPU node

@ray.remote(num_cpus=16)
def analyze_data(file: str):
    """Analyze large dataset"""
    return {"insights": "..."}  # Executes on high-CPU node

# Deploy as scalable HTTP service
@serve.deployment(num_replicas=2)
class AgentService:
    def __init__(self):
        adapter = LangGraphAdapter(model="gpt-4o-mini")
        self.session = AgentSession.remote("default", adapter)

    async def __call__(self, request):
        message = await request.json()
        result = await self.session.run.remote(
            message["query"],
            tools=[generate_image, analyze_data]
        )
        return result

serve.run(AgentService.bind())
```

Your framework controls the agent logic: which tools to call, when, and in what order. Ray handles the execution: routing tool calls to nodes with the right resources and scaling them automatically.

Bring your own framework by implementing the `AgentAdapter` interface. We're also developing a decorator-based API to make this even simpler.

Deploy with Ray Serve for autoscaling, load balancing, and HTTP routing. No Kubernetes manifests. No YAML files. No container orchestration complexity. Just Python code that turns sandboxes, MCP servers, and agents into production infrastructure.

## See It In Action

We built a token-efficient data analysis agent that demonstrates all three components working together. Here's what it does:

1. **Discovers tools** by exploring the `/mnt/servers` filesystem (MCP server wrappers)
2. **Executes code** in a persistent gVisor sandbox with volume-mounted datasets
3. **Maintains state** across conversation turns—no reloading data between questions

Real interaction:

```
You: What datasets do you have access to?

[Executing code]
```python
# Importing the list_datasets module to see what datasets are available
import sys
sys.path.append('/mnt')

from servers.datasets import list_datasets

# Since the functions are async, we need to run them using asyncio
import asyncio

datasets = asyncio.run(list_datasets())
print(datasets)
```
Output:
{'datasets': ['car_price_prediction_.csv']}

I have access to the following dataset: `car_price_prediction_.csv`. If you need any specific analysis or exploration of this dataset, let me know!
```

The agent imports only the MCP tools it needs (`list_directory`), processes data in the sandbox, and maintains Python state across turns. When you ask for a prediction, it can reference the same dataset without reloading—saving tokens and latency.

**Architecture:**

```
Agent (Host)
  ↓ Generates Python code
  ↓
Sandbox (gVisor Container)
  ├── /mnt/datasets    (volume mount with data)
  ├── /mnt/servers     (MCP server wrappers as Python modules)
  └── Persistent Python session
       ↓ HTTP calls to MCP servers
       ↓
MCP Filesystem Server (Ray Serve endpoint)
```

## Get Started

Our token-efficient agent example is open source and ready to run:

```bash
git clone https://github.com/your-org/ray-agents
cd ray-agents/examples/analyzer/token_efficient_agent
./build.sh
./run_cli.sh --image token-efficient-agent
```

Try it out. See 98%+ token savings in action. And when you're ready to deploy agents in production, we'll be here.

---

**Ready to build?** Check out our [documentation](https://your-docs-site.com) or join our [community](https://discord.gg/your-discord).

*Building the infrastructure for the next generation of AI agents.*
