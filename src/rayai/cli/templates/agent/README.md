# {{PROJECT_NAME}}

Built with [Agentic Ray](https://github.com/rayai-labs/agentic-ray).

## Quick Start

1. **Install:**
   ```bash
   pip install rayai
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
   rayai up
   ```

## API Endpoints

After running `rayai up`, your agents are available at:

- **POST** `/{agent_name}/` - Call your agent

### Example Request

```bash
curl -X POST http://localhost:8000/my_agent/ \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello!"}'
```
