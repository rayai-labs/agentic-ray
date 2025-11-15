from typing import Any

from ..mcp_client import call_mcp_tool


def import_dataset(name: str) -> dict[str, Any]:
    return call_mcp_tool("datasets", "import_dataset", {"name": name})
