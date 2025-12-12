# RayAI Agent Project

A template for building and running agents with Ray Serve using the RayAI CLI.

## Quick Start

1. **Create a new project:**
   ```bash
   rayai init <project_name>
   cd <project_name>
   ```

   Note: The project is automatically installed in editable mode (`pip install -e .`).

2. **Set up environment (optional):**
   ```bash
   # Create .env file with your API keys and configuration
   ```

3. **Create your first agent:**
   ```bash
   rayai create-agent <agent_name> --framework <framework_name>
   ```

4. **Implement your agent logic:**
   ```bash
   # Edit agents/<agent_name>/agent.py
   # - Add initialization code in __init__()
   # - Implement your logic in run()
   ```

5. **Run your agents:**
   ```bash
   rayai serve
   ```

6. **Test your agent:**
   ```bash
   curl -X POST http://localhost:8000/agents/<agent_name>/chat \
     -H "Content-Type: application/json" \
     -d '{"data": {"input": "test"}, "session_id": "test"}'
   ```

## Available Commands

- **`rayai create-agent <name> --framework <agent_framework>`** - Create a new agent
- **`rayai serve`** - Run all agents
- **`rayai serve --agents agent1,agent2`** - Run specific agents
- **`rayai serve --port=9000`** - Run on custom port

## API Endpoints

After running `rayai serve`, each agent gets its own endpoint:

- **POST /agents/{agent_name}/chat** - Main agent endpoint
- **GET /docs** - Interactive API documentation
- **Ray Dashboard:** http://localhost:8265

## Project Structure

```
my-project/
├── pyproject.toml          # Project config and dependencies
├── .env                    # Optional API keys
└── agents/                 # All your agents
    ├── agent1/
    │   ├── __init__.py
    │   └── agent.py        # Agent1 class
    ├── agent2/
    │   ├── __init__.py
    │   └── agent.py        # Agent2 class
    └── ...
```

## Agent Implementation

The agent class should use the `@agent` decorator. It should implement a `run()` method that takes a `data: dict` argument in OpenAI Chat API Format and returns a `dict` with `response` key containing the agent's output.

```python
from ray_agents import agent

@agent
class MyAgent:
    def __init__(self):
        # Add your initialization code here
        # - Load models
        # - Initialize clients
        # - Set up databases

    def run(self, data: dict) -> dict:
        # Implement your agent logic here
        # Called for every request to /agents/my-agent/chat
        # - Process the input data
        # - Return results as a dictionary
        return {"response": "Hello!"}
```

## Tool System

Agents can use distributed tools that execute as Ray remote functions across your cluster.

### Defining and Organizing Tools

Define tools inline or in a separate `tools.py` file:

```python
# agents/my-agent/tools.py
from ray_agents import tool

@tool(desc="Search knowledge base", num_cpus=1, memory="512MB")
def search_kb(query: str) -> dict:
    return {"results": [...]}

@tool(desc="Analyze sentiment", num_cpus=2, memory="1GB")
def analyze_sentiment(text: str) -> dict:
    return {"sentiment": "positive", "confidence": 0.95}
```

### Using Tools

```python
# agents/my-agent/agent.py
from ray_agents import agent, execute_tools
from .tools import search_kb, analyze_sentiment

@agent(num_cpus=1, memory="2GB")
class MyAgent:
    def run(self, data: dict) -> dict:
        # Execute tools in parallel (fastest)
        results = execute_tools([
            (search_kb, {"query": data["query"]}),
            (analyze_sentiment, {"text": data["text"]}),
        ], parallel=True)

        return {"search": results[0], "sentiment": results[1]}
```

### Parallel vs Sequential

- **`parallel=True`** - All tools run simultaneously, distributed across the cluster (faster)
- **`parallel=False`** - Tools run one after another (use for dependent steps)

### Key Points

- Tools always execute as distributed Ray remote functions
- Specify resources per tool: `@tool(desc="...", num_cpus=4, memory="8GB", num_gpus=1)`
- Tool resources are separate from agent resources

## Resource Configuration (Optional)

Specify CPU, GPU, and memory requirements for your agent actor in the `@agent` decorator.

```python
from ray_agents import agent

@agent(num_cpus=2, num_gpus=1, memory="4GB", num_replicas=2)
class MyAgent:
    def run(self, data: dict) -> dict:
        return {"response": "Hello!"}
```

Available resource options:
- `num_cpus` - Number of CPUs per replica (default: 1)
- `num_gpus` - Number of GPUs per replica (default: 0)
- `memory` - Memory per replica (default: "2GB", supports "4GB", "512MB", etc.)
- `num_replicas` - Number of replicas for load balancing (default: 1)

## Development Workflow

1. **Create agent:** `rayai create-agent my-agent`
2. **Edit logic:** Modify `agents/my-agent/agent.py`
3. **Test locally:** `rayai serve`
4. **Make requests:** `POST /agents/my-agent/chat`
5. **Iterate:** Edit code, restart serve, test