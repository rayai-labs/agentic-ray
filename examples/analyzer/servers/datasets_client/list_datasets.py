from typing import Any

from ..mcp_client import call_mcp_tool


def list_datasets() -> dict[str, Any]:
    return call_mcp_tool("datasets", "list_datasets", {})
