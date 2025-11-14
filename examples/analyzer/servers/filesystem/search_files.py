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

"""Search files tool wrapper for filesystem MCP server."""

from typing import Any

from ..mcp_client import call_mcp_tool


async def search_files(path: str, pattern: str) -> dict[str, Any]:
    """Search for files matching a pattern.

    Args:
        path: Directory to search in
        pattern: Glob pattern to match (e.g., '*.py', '**/*.txt')

    Returns:
        Dictionary containing:
        - matches: List of matching files, each with:
            - path: Full path to the file
            - type: 'file' or 'directory'
        - count: Number of matches
        - error: Error message (if failed)

    Example:
        >>> result = await search_files("./src", "**/*.py")
        >>> if "matches" in result:
        ...     print(f"Found {result['count']} Python files")
        ...     for match in result["matches"]:
        ...         print(match["path"])
    """
    return await call_mcp_tool(
        "filesystem", "search_files", {"path": path, "pattern": pattern}
    )
