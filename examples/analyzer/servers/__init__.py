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

"""MCP Servers for Ray Agents examples.

This package provides wrappers for MCP servers following the pattern described
in Anthropic's MCP code execution blog post. Tools are organized by server,
with each tool available as a separate Python function.

Available servers:
- filesystem: File and directory operations
- code_executor: Execute Python code in sandboxed environment

Example:
    from servers.filesystem import read_file, list_directory
    from servers.code_executor import execute_code

    files = await list_directory("./data")
    content = await read_file("data/example.txt")
    result = await execute_code("print('Hello')")
"""
