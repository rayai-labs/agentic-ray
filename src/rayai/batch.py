"""Generic batch tool for parallel execution of any registered tool.

This module provides a flexible BatchTool that allows LLMs to call any
registered tool by name with multiple inputs in parallel using Ray.
"""

from collections.abc import Callable
from typing import Any

import ray
from pydantic import BaseModel, Field


class BatchToolInput(BaseModel):
    """Input schema for BatchTool - exposed to LLMs."""

    tool_name: str = Field(description="Name of the tool to execute")
    tool_inputs: list[dict[str, Any]] = Field(
        description="List of input dictionaries, one per tool invocation"
    )


class BatchToolOutput(BaseModel):
    """Output schema for BatchTool results."""

    results: list[Any] = Field(
        description="Results from each tool invocation (None if error occurred)"
    )
    errors: list[str | None] = Field(
        description="Error messages for each invocation (None if success)"
    )
    tool_name: str = Field(description="Name of the tool that was executed")
    count: int = Field(description="Number of inputs processed")


class BatchTool:
    """Generic batch tool for parallel execution of any registered tool.

    BatchTool is itself a tool that can be used with any agent framework.
    When called by an LLM, it:
    1. Resolves the tool by name
    2. Executes all inputs in parallel on Ray
    3. Returns structured output with results and per-item errors

    Example:
        >>> batch_tool = BatchTool(tools=[search_tool, fetch_tool])
        >>> result = batch_tool(
        ...     tool_name="search",
        ...     tool_inputs=[{"query": "a"}, {"query": "b"}, {"query": "c"}]
        ... )
    """

    def __init__(
        self,
        tools: list[Callable] | None = None,
        description: str | None = None,
        name: str = "batch",
    ):
        """Initialize BatchTool.

        Args:
            tools: List of tools to register (names inferred from __name__)
            description: Custom description for the batch tool
            name: Name for the batch tool (default: "batch")
        """
        self._tools: dict[str, Callable] = {}
        self._remote_funcs: dict[str, Any] = {}
        self._name = name
        self._description = description or self._default_description()

        if tools:
            for tool in tools:
                self._register(tool)

        self._setup_tool_metadata()

    def _default_description(self) -> str:
        return (
            "Execute multiple calls to any registered tool in parallel. "
            "Provide the tool name and a list of input dictionaries. "
            "Returns results and any errors for each input."
        )

    def _setup_tool_metadata(self) -> None:
        """Set up metadata so BatchTool can be used as a tool itself."""
        self.__name__ = self._name
        self.__qualname__ = self._name
        self.__doc__ = self._description

        self.__annotations__ = {
            "tool_name": str,
            "tool_inputs": list[dict[str, Any]],
            "return": dict[str, Any],
        }

        self.args_schema = BatchToolInput

        self._tool_metadata = {
            "description": self._description,
            "is_batch_tool": True,
        }

    def _register(self, tool: Callable, name: str | None = None) -> None:
        """Register a tool."""
        if name is None:
            # Get name from the tool
            if hasattr(tool, "_original_func"):
                name = tool._original_func.__name__
            elif hasattr(tool, "__name__"):
                name = tool.__name__
            else:
                raise ValueError("Cannot infer tool name, provide explicitly")

        self._tools[name] = tool

        # Get or create the ray remote function
        if hasattr(tool, "_remote_func"):
            # Already a @rayai.tool decorated function
            self._remote_funcs[name] = tool._remote_func
        else:
            # Plain callable - wrap with ray.remote
            self._remote_funcs[name] = ray.remote(tool)

    def _list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    @property
    def name(self) -> str:
        """Tool name."""
        return self._name

    @property
    def description(self) -> str:
        """Tool description."""
        return self._description

    def __call__(
        self,
        tool_name: str,
        tool_inputs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute batch tool calls.

        Args:
            tool_name: Name of tool to execute
            tool_inputs: List of input dicts for each invocation

        Returns:
            Dict with results, errors, tool_name, count
        """
        if not tool_inputs:
            return BatchToolOutput(
                results=[],
                errors=[],
                tool_name=tool_name,
                count=0,
            ).model_dump()

        if tool_name not in self._remote_funcs:
            available = self._list_tools()
            error_msg = f"Tool '{tool_name}' not found. Available: {available}"
            return BatchToolOutput(
                results=[None] * len(tool_inputs),
                errors=[error_msg] * len(tool_inputs),
                tool_name=tool_name,
                count=len(tool_inputs),
            ).model_dump()

        results, errors = self._execute_parallel(tool_name, tool_inputs)

        return BatchToolOutput(
            results=results,
            errors=errors,
            tool_name=tool_name,
            count=len(tool_inputs),
        ).model_dump()

    def _execute_parallel(
        self,
        tool_name: str,
        inputs: list[dict[str, Any]],
    ) -> tuple[list[Any], list[str | None]]:
        """Execute inputs in parallel on Ray."""
        remote_func = self._remote_funcs[tool_name]

        # Dispatch all calls in parallel
        refs = [remote_func.remote(**inp) for inp in inputs]

        results: list[Any] = []
        errors: list[str | None] = []

        for i, ref in enumerate(refs):
            try:
                result = ray.get(ref)
                results.append(result)
                errors.append(None)
            except Exception as e:
                results.append(None)
                errors.append(f"Execution error for input {i}: {str(e)}")

        return results, errors


__all__ = ["BatchTool", "BatchToolInput", "BatchToolOutput"]
