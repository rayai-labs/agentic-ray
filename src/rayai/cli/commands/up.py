"""Run all agents in the agents/ directory with Ray Serve.

The `rayai up` command discovers and serves all agents defined in the
agents/ directory. Each agent file should call `rayai.serve()` which
registers the agent for deployment.

Usage:
    rayai up                    # Serve all agents on port 8000
    rayai up --port 8080        # Serve on custom port
    rayai up --agents a,b       # Serve specific agents only

Example agent file (agents/myagent/agent.py):
    import rayai
    from pydantic_ai import Agent

    @rayai.tool
    def search(query: str) -> str:
        return f"Results for {query}"

    agent = Agent("gpt-4", tools=[search])
    rayai.serve(agent, name="myagent")
"""

import importlib.util
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from rayai.cli.analytics import track


@click.command()
@click.argument("project_path", default=".")
@click.option("--port", default=8000, help="Port to serve on")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--agents", help="Serve specific agents only (comma-separated)")
def up(project_path: str, port: int, host: str, agents: str | None):
    """Run all agents in the agents/ directory.

    Discovers agent.py files in agents/*/ and serves them with Ray Serve.
    Each agent file should call rayai.serve() to register the agent.

    Examples:
        rayai up                    # Serve all agents
        rayai up --port 8080        # Custom port
        rayai up --agents a,b       # Specific agents only
    """
    project_dir = Path(project_path).resolve()

    # Load environment variables from .env file
    env_file = project_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        click.echo(f"Loaded environment from {env_file}")

    if not project_dir.exists():
        click.echo(f"Error: Project directory not found: {project_dir}")
        sys.exit(1)

    agents_dir = project_dir / "agents"
    if not agents_dir.exists():
        click.echo(f"Error: agents/ directory not found in {project_dir}")
        click.echo("Create agents/ directory with agent.py files")
        sys.exit(1)

    # Ensure dependencies
    if not _ensure_dependencies():
        sys.exit(1)

    # Set rayai up mode before importing agents
    from rayai.serve import (
        clear_registered_agents,
        get_registered_agents,
        run,
        set_rayai_up_mode,
    )

    set_rayai_up_mode(True)
    clear_registered_agents()

    # Discover and import agent modules
    agent_filter = {a.strip() for a in agents.split(",")} if agents else None
    imported_count = _import_agent_modules(agents_dir, agent_filter)

    if imported_count == 0:
        click.echo("Error: No agent modules found")
        click.echo("Create agents/<name>/agent.py files that call rayai.serve()")
        sys.exit(1)

    # Get registered agents
    registered = get_registered_agents()

    if not registered:
        click.echo("Error: No agents registered")
        click.echo("Ensure agent.py files call rayai.serve(agent, name='...')")
        sys.exit(1)

    track("cli_up", {"agent_count": len(registered)})

    click.echo(f"\nFound {len(registered)} agent(s):")
    for config in registered:
        click.echo(f"  • {config.name}")

    # Start serving
    try:
        run(port=port, host=host)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
    except Exception as e:
        click.echo(f"Error: {e}")
        sys.exit(1)


def _ensure_dependencies() -> bool:
    """Ensure Ray Serve dependencies are available."""
    try:
        import ray  # noqa: F401
        from fastapi import FastAPI  # noqa: F401
        from ray import serve  # noqa: F401

        return True
    except ImportError as e:
        click.echo(f"Missing dependency: {e}")
        click.echo("Install with: pip install 'rayai[serve]'")
        return False


def _import_agent_modules(agents_dir: Path, agent_filter: set[str] | None) -> int:
    """Import agent.py modules from agents/ subdirectories.

    Args:
        agents_dir: Path to agents/ directory.
        agent_filter: Set of agent names to include, or None for all.

    Returns:
        Number of modules successfully imported.
    """
    imported = 0

    # Add project root to path for imports
    project_dir = agents_dir.parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    for agent_folder in sorted(agents_dir.iterdir()):
        if not agent_folder.is_dir():
            continue
        if agent_folder.name.startswith("__"):
            continue

        agent_name = agent_folder.name

        # Filter if specified
        if agent_filter and agent_name not in agent_filter:
            continue

        agent_file = agent_folder / "agent.py"
        if not agent_file.exists():
            click.echo(f"Warning: No agent.py in {agent_name}/, skipping")
            continue

        # Import the module
        module_name = f"agents.{agent_name}.agent"
        try:
            click.echo(f"Loading {agent_name}...")
            _import_module_from_file(agent_file, module_name)
            imported += 1
        except Exception as e:
            click.echo(f"Error loading {agent_name}: {e}")
            continue

    return imported


def _import_module_from_file(file_path: Path, module_name: str):
    """Import a Python module from a file path.

    Args:
        file_path: Path to the .py file.
        module_name: Full module name (e.g., agents.myagent.agent).

    Raises:
        ImportError: If module cannot be imported.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create module spec for {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
