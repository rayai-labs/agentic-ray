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

"""Code executor MCP server tool wrappers.

This module provides a Python wrapper for executing code in a sandboxed environment.

Available tools:
- execute_code: Execute Python code with persistent variables

Example:
    from servers.code_executor import execute_code

    result = await execute_code("print('Hello world')")
    if "stdout" in result:
        print(result["stdout"])
"""

from .execute_code import execute_code

__all__ = ["execute_code"]
