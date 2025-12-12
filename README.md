<div align="center">

<a href="https://rayai.com">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-color.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/logo-color.svg">
    <img alt="Agentic Ray" src="assets/logo-color.svg" width="300">
  </picture>
</a>

<br/>

[www.rayai.com](https://rayai.com)

<!-- [![PyPI version](https://img.shields.io/pypi/v/agentic-ray?color=blue)](https://pypi.org/project/agentic-ray/) -->
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/rayai-labs/agentic-ray/blob/main/LICENSE)
<!-- [![Build Status](https://img.shields.io/github/actions/workflow/status/rayai-labs/agentic-ray/ci.yml)](https://github.com/rayai-labs/agentic-ray/actions) -->
<!-- [![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/YOUR_INVITE) -->

Scalable runtime for Agents, MCP Servers, and coding sandboxes, orchestrated with [Ray](https://github.com/ray-project/ray).

</div>

## Requirements

- Python 3.12+

## Quick Start

1. **Install:**
   ```bash
   pip install agentic-ray
   ```

2. **Create a new project:**
   ```bash
   rayai init my_project
   cd my_project
   ```

3. **Create an agent:**
   ```bash
   rayai create-agent my_agent
   ```

4. **Run your agent:**
   ```bash
   rayai serve
   ```

## API Endpoints

After running `rayai serve`, your agents are available at:

- **POST** `/agents/{agent_name}/chat` - Call your agent

### Example Request

```bash
curl -X POST http://localhost:8000/agents/my_agent/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'
```

## Parallel Tool Execution

Define tools and execute them in parallel on Ray:

```python
from ray_agents import tool, execute_tools

@tool(desc="Tool 1 description")
def tool_1(x: str) -> str:
    return process_1(x)

@tool(desc="Tool 2 description")
def tool_2(x: str) -> dict:
    return process_2(x)

# Execute both tools in parallel on Ray
results = execute_tools([
    (tool_1, {"x": "input_1"}),
    (tool_2, {"x": "input_2"})
], parallel=True)
```

## Features
- Distributed resource-aware tool execution on Ray clusters
- Framework-agnostic tool adapters (LangChain, Pydantic)
- Secure gVisor-sandboxed environments for AI generated code execution

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) to get started.

---

If you find this project helpful, please consider giving it a ⭐
