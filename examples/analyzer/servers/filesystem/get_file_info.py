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

"""Get file info tool wrapper for filesystem MCP server."""

from typing import Any

from ..mcp_client import call_mcp_tool


async def get_file_info(path: str) -> dict[str, Any]:
    """Get metadata information about a file or directory.

    Args:
        path: Path to get info about

    Returns:
        Dictionary containing:
        - path: Full path
        - name: File/directory name
        - type: 'file' or 'directory'
        - size: Size in bytes
        - created: Creation timestamp
        - modified: Modification timestamp
        - accessed: Last access timestamp
        - error: Error message (if failed)

    Example:
        >>> result = await get_file_info("data.csv")
        >>> if "size" in result:
        ...     print(f"File size: {result['size']} bytes")
        ...     print(f"Last modified: {result['modified']}")
    """
    return await call_mcp_tool("filesystem", "get_file_info", {"path": path})
