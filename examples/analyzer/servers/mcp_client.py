"""MCP Client for communicating with MCP servers via Unix socket."""

import json
import socket
from typing import Any


class MCPClient:
    """Client for communicating with MCP servers via Unix socket sidecar proxy."""

    def __init__(self, mcp_server_url: str, socket_path: str = "/tmp/mcp.sock"):
        """Initialize MCP client.

        Args:
            mcp_server_url: URL of the MCP server (e.g., 'http://localhost:8265/mcp')
            socket_path: Path to Unix socket for sidecar proxy
        """
        self.mcp_server_url = mcp_server_url
        self.socket_path = socket_path

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool on the MCP server via Unix socket.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Result from the tool execution

        Raises:
            RuntimeError: If communication fails
        """
        request_data = {
            "url": self.mcp_server_url,
            "tool": tool_name,
            "arguments": arguments,
        }

        try:
            # Connect to Unix socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)

            try:
                # Send request (length-prefixed JSON)
                request_bytes = json.dumps(request_data).encode("utf-8")
                length_bytes = len(request_bytes).to_bytes(4, byteorder="big")
                sock.sendall(length_bytes + request_bytes)

                # Receive response length
                length_bytes = sock.recv(4)
                if not length_bytes:
                    raise RuntimeError("No response from MCP proxy")

                response_length = int.from_bytes(length_bytes, byteorder="big")

                # Receive response data
                response_data = b""
                while len(response_data) < response_length:
                    chunk = sock.recv(min(4096, response_length - len(response_data)))
                    if not chunk:
                        break
                    response_data += chunk

                if len(response_data) != response_length:
                    raise RuntimeError("Incomplete response from MCP proxy")

                # Parse response
                response = json.loads(response_data.decode("utf-8"))

                # Check for errors
                if "error" in response:
                    raise RuntimeError(f"MCP proxy error: {response['error']}")

                return response.get("result", response)

            finally:
                sock.close()

        except OSError as e:
            raise RuntimeError(
                f"Failed to connect to MCP proxy at {self.socket_path}: {str(e)}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool: {str(e)}") from e


_datasets_client: MCPClient | None = None


def get_datasets_client(
    mcp_server_url: str = "http://host.docker.internal:8265/mcp",
    socket_path: str = "/tmp/mcp.sock",
) -> MCPClient:
    """Get or create the datasets MCP client.

    Args:
        mcp_server_url: URL of the MCP server (default: 'http://localhost:8265/mcp')
        socket_path: Path to Unix socket for sidecar proxy (default: '/tmp/mcp.sock')

    Returns:
        MCPClient instance for the datasets server
    """
    global _datasets_client
    if _datasets_client is None:
        _datasets_client = MCPClient(
            mcp_server_url=mcp_server_url, socket_path=socket_path
        )

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
