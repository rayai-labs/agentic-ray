# Building production-ready AI Agents: From 98% token savings to scalable infrastructure

Anthropic recently published a [compelling piece](https://www.anthropic.com/engineering/code-execution-with-mcp) on code execution with the Model Context Protocol (MCP). By having agents write code instead of making direct tool calls, they reduced token usage from 150,000 to 2,000 tokens—a **98.7% reduction**.

They acknowledged the complexity, but the question remains: *How do you actually deploy this in production?*

## The Token Efficiency Breakthrough

The traditional approach to agent tool use has a fatal flaw. When you connect an agent to dozens or hundreds of tools via MCP, two things happen:

1. **Context window overload**: Every tool definition eats into your context budget
2. **Token waste**: Intermediate results pass through the model repeatedly, consuming thousands of tokens

Anthropic's solution is elegant: instead of tool calls, agents write Python code to interact with MCP servers. The agent discovers available tools by exploring a filesystem structure, loads only what it needs, and processes data in the execution environment before returning results to the model.

The impact is dramatic. Rather than sending a 100KB CSV through the model three times, the agent writes code once:

```python
import sys
sys.path.append('/mnt')

async def main():
    from servers.filesystem import read_file
    import pandas as pd
    import io

    # Load data once in the sandbox
    content = await read_file("/mnt/datasets/sales.csv")
    df = pd.read_csv(io.StringIO(content))

    # Process and return only the summary
    print(df.describe())

import asyncio
asyncio.run(main())
```

The model sees only the summary statistics—not the raw data. Token usage drops by over 98%.

## Seeing It In Action

We built a token-efficient agent to demonstrate this approach. Here's a real interaction:

```
You: What datasets are available?

Agent: I'll check for you.

[Executing code]
```python
import sys
sys.path.append('/mnt')

async def main():
    from servers.filesystem import list_directory
    result = await list_directory("/mnt/datasets")
    for entry in result['entries']:
        print(f"{entry['name']}")

import asyncio
asyncio.run(main())
```

Output:
car_price_prediction.csv

You: Load it and show me summary statistics

Agent: [Generates code that loads the CSV and computes stats]
```

Notice what happens: the agent discovers the MCP filesystem tools, uses them to find datasets, then analyzes the data—all in a sandboxed environment. Variables persist across turns, so `df` is available for follow-up questions without reloading.

The architecture looks like this:

```
Agent (Host)
  ↓ Generates Python code
  ↓
Sandbox (gVisor Container)
  ├── /mnt/datasets    (volume mount)
  ├── /mnt/servers     (MCP tools as Python modules)
  └── Persistent Python session
```

You can try it yourself—it's open source in our [ray-agents repository](https://github.com/your-org/ray-agents/tree/main/examples/analyzer/token_efficient_agent).

## The Infrastructure Problem

Here's where things get hard.

Anthropic's blog post focuses on the *technique*—and it's brilliant. But they gloss over the operational complexity:

> "Code execution requires secure sandboxing, resource limits, and monitoring—adding operational overhead that direct tool calls avoid."

That one sentence hides a mountain of engineering work:

- **Sandboxing**: You need gVisor or similar isolation to safely execute untrusted code
- **Session management**: Maintaining persistent Python environments across user turns
- **Volume mounts**: Securely exposing datasets and MCP servers to the sandbox
- **Resource limits**: CPU, memory, and timeout enforcement
- **MCP server deployment**: Running and scaling filesystem, database, and custom MCP servers
- **Monitoring**: Tracking execution failures, token usage, and performance
- **Container orchestration**: Building, caching, and distributing Docker images

And this is just for *one* agent. What if you're building a platform? What if you have multiple agents, each with different tool requirements? What if you need to deploy custom MCP servers for your users?

The infrastructure gap is real.

## Infrastructure for Agent Builders

This is what we're building at [Your Company]: **production-grade infrastructure for deploying AI agents, MCP servers, and code sandboxes**.

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

### 2. MCP Server Deployment

Ship MCP servers that your agents can discover and use:

```python
# Your custom MCP server
from servers.database import query_db

async def get_customer_data(customer_id: str):
    return await query_db(f"SELECT * FROM customers WHERE id = {customer_id}")
```

Mount it into the sandbox, and your agents can import and use it like any Python module.

### 3. Distributed Execution

Ray's distributed runtime means your agents scale automatically:

```python
@ray.remote
class Agent:
    def chat(self, message: str):
        # Agent logic here
        result = execute_code.remote(...)
        return ray.get(result)

# Deploy 10 agents across your cluster
agents = [Agent.remote() for _ in range(10)]
```

No Kubernetes manifests. No container orchestration nightmares. Just Python.

## The Vision

We believe the future of AI is agentic. Agents will write code, use tools, and interact with data on behalf of users. But today, building production-ready agents requires deep infrastructure expertise.

Our mission is to change that.

We're building the platform that lets you focus on agent *behavior*—not sandboxing, session management, or MCP server deployment. We handle the infrastructure. You build the intelligence.

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
