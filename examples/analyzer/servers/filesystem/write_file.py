# Copyright (c) 2025 Ray AI Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Write file tool wrapper for filesystem MCP server."""

from typing import Any

from ..mcp_client import call_mcp_tool


async def write_file(path: str, content: str) -> dict[str, Any]:
    """Write content to a file, creating it if it doesn't exist.

    Args:
        path: Path to the file to write
        content: Content to write to the file

    Returns:
        Dictionary containing:
        - success: True if successful
        - message: Success message
        - error: Error message (if failed)

    Example:
        >>> result = await write_file("output.txt", "Hello, world!")
        >>> if result.get("success"):
        ...     print(result["message"])
    """
    return await call_mcp_tool(
        "filesystem", "write_file", {"path": path, "content": content}
    )
