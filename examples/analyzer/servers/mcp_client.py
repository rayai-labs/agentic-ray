"""MCP Client for communicating with MCP servers via HTTP."""

import json
import urllib.error
import urllib.request
from typing import Any


class MCPClient:
    """Client for communicating with MCP servers via HTTP."""

    def __init__(self, http_endpoint: str):
        """Initialize MCP client.

        Args:
            http_endpoint: HTTP endpoint for MCP server
        """
        self.http_endpoint = http_endpoint

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool on the MCP server via HTTP.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Result from the tool execution

        Raises:
            RuntimeError: If communication fails
        """
        request_data = {
            "tool": tool_name,
            "arguments": arguments,
        }

        try:
            data = json.dumps(request_data).encode("utf-8")
            req = urllib.request.Request(
                f"{self.http_endpoint}/tools/call",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"HTTP error {e.code}: {error_body}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool via HTTP: {str(e)}") from e


_datasets_client: MCPClient | None = None


def get_datasets_client(http_endpoint: str | None = None) -> MCPClient:
    """Get or create the datasets MCP client.

    Args:
        http_endpoint: HTTP endpoint for MCP server (e.g., 'http://localhost:8265/mcp')
                      If None, will try to detect Ray Serve endpoint

    Returns:
        MCPClient instance for the datasets server
    """
    global _datasets_client
    if _datasets_client is None:
        if http_endpoint is None:
            import os

            in_docker = os.path.exists("/.dockerenv")

            if not in_docker and os.path.exists("/proc/1/cgroup"):
                try:
                    with open("/proc/1/cgroup") as f:
                        in_docker = "docker" in f.read()
                except Exception:
                    pass

            if in_docker:
                http_endpoint = "http://host.docker.internal:8265/mcp"
            else:
                http_endpoint = "http://localhost:8265/mcp"

        _datasets_client = MCPClient(http_endpoint=http_endpoint)

    return _datasets_client


def call_mcp_tool(
    server: str, tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Call an MCP tool on the specified server.

    This is the central function that all tool wrappers use to communicate
    with MCP servers.

    Args:
        server: Name of the MCP server (e.g., 'datasets')
        tool_name: Name of the tool to call
        arguments: Arguments for the tool

    Returns:
        Result from the tool execution
    """
    if server == "datasets":
        client = get_datasets_client()
        return client.call_tool(tool_name, arguments)
    else:
        raise ValueError(f"Unknown MCP server: {server}")
