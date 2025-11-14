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

"""Read file tool wrapper for filesystem MCP server."""

from typing import Any

from ..mcp_client import call_mcp_tool


async def read_file(path: str) -> dict[str, Any]:
    """Read the complete contents of a file from the file system.

    Args:
        path: Path to the file to read

    Returns:
        Dictionary containing:
        - content: The file contents (if successful)
        - error: Error message (if failed)

    Example:
        >>> result = await read_file("data/example.txt")
        >>> if "content" in result:
        ...     print(result["content"])
    """
    return await call_mcp_tool("filesystem", "read_file", {"path": path})
