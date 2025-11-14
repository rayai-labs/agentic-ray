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

"""
Ray Code Interpreter - Execute Python code securely in Docker containers

Basic usage:
    from ray_agents.code_interpreter import execute_code

    result = ray.get(execute_code.remote("print('Hello!')"))
    print(result["stdout"])  # "Hello!"

With sessions:
    # Session 1
    ray.get(execute_code.remote("x = 5", session_id="user-123"))
    result = ray.get(execute_code.remote("print(x)", session_id="user-123"))
    # Output: 5 (state persisted)

With custom environments:
    dockerfile = '''
    FROM python:3.11-slim
    RUN pip install numpy pandas
    '''
    result = ray.get(execute_code.remote(
        "import pandas; print(pandas.__version__)",
        dockerfile=dockerfile,
        session_id="custom-env"
    ))
"""

from .tools import (
    cleanup_session,
    execute_code,
    get_session_stats,
    install_package,
    upload_file,
)
from .types import (
    CleanupError,
    CleanupResult,
    ExecutionError,
    ExecutionResult,
    InstallError,
    InstallResult,
    SessionStats,
    UploadError,
    UploadResult,
)

__all__ = [
    # Tools
    "execute_code",
    "install_package",
    "upload_file",
    "get_session_stats",
    "cleanup_session",
    # Types
    "ExecutionResult",
    "ExecutionError",
    "InstallResult",
    "InstallError",
    "UploadResult",
    "UploadError",
    "SessionStats",
    "CleanupResult",
    "CleanupError",
]
