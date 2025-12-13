# CLAUDE.md

## Purpose of This Directory
This directory contains the command-line interface (CLI) for Agentic Ray. The CLI provides commands for:
- Initializing new agent projects
- Creating agent templates
- Serving agents with Ray Serve
- Managing agent deployments

The CLI is the primary user-facing tool for interacting with the Agentic Ray runtime.

## Directory Structure
- `cli.py` - Main CLI entry point and command group
- `commands/` - Individual command implementations
  - `init.py` - Initialize new project
  - `create_agent.py` - Create agent from template
  - `serve.py` - Serve agent with Ray Serve
- `templates/` - Project and agent templates
  - `agent/` - Agent template structure

## Key Concepts an AI Should Know
- CLI uses Click framework for command-line parsing
- Entry point is `rayai` (defined in `pyproject.toml`)
- Commands are modular and live in `commands/` subdirectory
- Templates are copied from `templates/agent/` directory (not Jinja2, simple file copy with string replacement)
- `serve` command discovers agents by scanning `agents/` directory for `@agent` decorated classes
- Agent discovery looks for `agents/<name>/agent.py` files with classes decorated with `@agent`
- `create_agent` generates framework-specific templates (python, langchain, pydantic)
- Commands should be self-contained and handle errors gracefully

## Command Overview

### `rayai init <project_name>`
Initializes a new agent project with boilerplate structure from templates. Creates project directory with `agents/` subdirectory, `pyproject.toml`, and `README.md`. Installs project in editable mode.

### `rayai create-agent <agent_name> [--framework=<framework>]`
Creates a new agent in the `agents/<agent_name>/` directory. Supports multiple frameworks:
- `python` (default): Pure Python agent template
- `langchain`: LangChain/LangGraph agent template
- `pydantic`: Pydantic AI agent template

Each template includes framework-specific boilerplate with `@agent` decorator and example tools.

### `rayai serve [--port=<port>] [--agents=<comma-separated>]`
Discovers and serves agents from the `agents/` directory using Ray Serve. 
- Automatically finds all `@agent` decorated classes in `agents/*/agent.py`
- Creates FastAPI endpoints at `/agents/<agent_name>/chat`
- Supports serving specific agents via `--agents` flag
- Each agent runs with resource configuration from `@agent` decorator

## Key Files
- `cli.py`: Main CLI group and entry point, registers all commands
- `commands/init.py`: Project initialization from templates, handles `pyproject.toml` and `README.md` variable substitution
- `commands/create_agent.py`: Agent creation with framework-specific templates (python/langchain/pydantic)
- `commands/serve.py`: Agent discovery from `agents/` directory, Ray Serve deployment, FastAPI endpoint creation
- `templates/agent/`: Project template structure (agents/, pyproject.toml, README.md)

## Do / Don't

### ✅ Do:
- Add new commands as separate modules in `commands/`
- Follow Click patterns for command definition
- Provide clear error messages and help text
- Validate inputs before processing
- Use templates for code generation to maintain consistency
- Handle Ray initialization and cleanup properly

### ❌ Don't:
- Create commands that modify core runtime code
- Add commands that require root/admin privileges
- Hardcode paths or assume specific directory structures
- Create commands that break existing workflows
- Add heavyweight dependencies to CLI
- Skip input validation or error handling

## Adding a New Command

1. Create new file in `commands/` (e.g., `commands/mycommand.py`)
2. Define Click command function with proper decorators
3. Add command to CLI group in `cli.py`: `cli.add_command(mycommand.mycommand)`
4. Add help text and option documentation
5. Test command with various inputs and error cases
6. Update main README if command is user-facing

## Related Modules
- `src/ray_agents/deployment.py` - Ray Serve deployment utilities used by `serve` command (supports streaming via `run_stream`/`run_stream_events`)
- `src/ray_agents/base.py` - AgentProtocol used for validation
- `src/ray_agents/decorators.py` - `@agent` decorator used for agent discovery
- `src/ray_agents/resource_loader.py` - Memory parsing used by deployment
- `examples/` - Example agents that can be served
- Templates reference core runtime APIs

