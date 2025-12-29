# CLAUDE.md

## Purpose of This Directory
This directory contains the command-line interface (CLI) for Agentic Ray. The CLI provides commands for:
- Initializing new agent projects
- Creating agent templates
- Running agents with Ray Serve via `rayai up`
- Managing analytics settings

The CLI is the primary user-facing tool for interacting with the Agentic Ray runtime.

## Directory Structure
- `cli.py` - Main CLI entry point and command group, wires up all subcommands
- `analytics.py` - Shared helpers for anonymous CLI usage analytics (PostHog)
- `commands/` - Individual command implementations
  - `init.py` - Initialize new project from templates
  - `create_agent.py` - Create agent from template (python/langchain/pydantic)
  - `up.py` - Run all agents with `rayai up`
  - `analytics.py` - `rayai analytics` subcommands (on/off/status)
- `templates/` - Project and agent templates
  - `agent/` - Agent template structure

## Key Concepts an AI Should Know
- CLI uses Click framework for command-line parsing
- Entry point is `rayai` (defined in `pyproject.toml`)
- Commands are modular and live in `commands/` subdirectory
- Templates are copied from `templates/agent/` directory
- `up` command imports `agents/*/agent.py` files that call `rayai.serve()`
- Agent discovery uses the `rayai.serve()` registration pattern
- `create_agent` generates framework-specific templates (python, langchain, pydantic)
- `analytics` commands manage opt-in/opt-out for anonymous CLI usage analytics
- Commands should be self-contained and handle errors gracefully

## Command Overview

### `rayai init <project_name>`
Initializes a new agent project with boilerplate structure from templates. Creates project directory with `agents/` subdirectory, `pyproject.toml`, and `README.md`.

### `rayai create-agent <agent_name> [--framework=<framework>]`
Creates a new agent in the `agents/<agent_name>/` directory. Supports multiple frameworks:
- `python` (default): Custom agent using `rayai.Agent` base class
- `langchain`: LangChain/LangGraph agent template
- `pydantic`: Pydantic AI agent template

Each template uses `rayai.tool` for tools and `rayai.serve()` for deployment.

### `rayai up [--port=<port>] [--agents=<comma-separated>]`
Imports all `agents/*/agent.py` files, collects `rayai.serve()` registrations, and starts all agents with Ray Serve.
- Automatically finds all agent modules in `agents/` directory
- Supports filtering specific agents via `--agents` flag
- Each agent's resources come from `rayai.serve()` call

### `rayai analytics [on|off|status]`
Manage anonymous CLI usage analytics settings.

## Key Files
- `cli.py`: Main CLI group and entry point, registers all commands
- `analytics.py`: Low-level analytics helpers (`track`, anonymous ID, DO_NOT_TRACK env vars)
- `commands/init.py`: Project initialization from templates
- `commands/create_agent.py`: Agent creation with framework-specific templates
- `commands/up.py`: Import agent modules and start Ray Serve
- `commands/analytics.py`: User-facing `rayai analytics` command group
- `templates/agent/`: Project template structure

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
- `src/rayai/serve.py` - `rayai.serve()` registration used by `up` command
- `src/rayai/deployment.py` - Ray Serve deployment utilities
- `src/rayai/decorators.py` - `@rayai.tool` decorator
- `examples/` - Example agents that can be served
- Templates reference core runtime APIs
