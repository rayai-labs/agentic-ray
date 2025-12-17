"""Agentic-Ray"""

import importlib.metadata

from rayai.base import AgentProtocol
from rayai.batch import BatchTool, BatchToolInput, BatchToolOutput
from rayai.decorators import agent, tool
from rayai.utils import execute_tools

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__all__ = [
    "AgentProtocol",
    "BatchTool",
    "BatchToolInput",
    "BatchToolOutput",
    "agent",
    "execute_tools",
    "tool",
    "__version__",
]
