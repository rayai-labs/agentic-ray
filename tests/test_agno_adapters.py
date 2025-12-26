"""Unit tests for Agno adapters and tool wrappers.

These tests focus on detecting Agno tools and converting them to Ray-executed
callables without requiring any external model APIs.
"""

from collections.abc import Callable

import pytest
import ray

from rayai.adapters.agno.tools import from_agno_tool
from rayai.adapters.core import SourceFramework, detect_framework

try:  # Agno 2.3.x+ may not expose Tool at agno.tools.Tool
    from agno.tools import Tool as AgnoTool  # type: ignore[import-not-found]

    HAS_AGNO_TOOL = True
except Exception:  # pragma: no cover - version-specific behavior
    AgnoTool = None  # type: ignore[assignment]
    HAS_AGNO_TOOL = False


@pytest.fixture
def ray_start():
    """Local Ray cluster for these tests (scoped here to avoid cross-talk)."""

    ray.init(ignore_reinit_error=True, num_cpus=2)
    yield
    ray.shutdown()


class TestAgnoDetectionAndConversion:
    """Tests for detecting and converting Agno tools.

    NOTE: These tests require the optional ``agno`` dependency. They
    are effectively guarded by ``pytest.importorskip("agno")`` inside
    each test, so they will be skipped when Agno is not installed.
    """

    def test_detect_framework_agno_tool(self, ray_start):
        """Detect Agno tools or fall back to callable on newer Agno versions.

        On older Agno versions that expose ``agno.tools.Tool``, we expect
        Agno tools to be classified as ``SourceFramework.AGNO``.

        On newer Agno versions where ``Tool`` is no longer available, the
        adapter cannot distinguish Agno tools by type and should fall back
        to treating plain callables as ``SourceFramework.CALLABLE``.
        """
        pytest.importorskip("agno")

        def add(x: int, y: int) -> int:
            return x + y

        if HAS_AGNO_TOOL:
            agno_tool = AgnoTool(add, name="add", description="Add two numbers")  # type: ignore[call-arg]
            assert detect_framework(agno_tool) == SourceFramework.AGNO
        else:
            # Without Agno Tool class, we fall back to callable detection.
            assert detect_framework(add) == SourceFramework.CALLABLE

    def test_from_agno_tool_wraps_and_executes_on_ray(self, ray_start):
        """from_agno_tool should wrap tools or fail clearly when Tool is missing.

        - When Agno exposes ``Tool``, we expect a Ray-backed callable that
          executes successfully.
        - When ``Tool`` is not available (newer Agno), we expect an
          ``ImportError`` explaining that Agno tool conversion requires the
          Tool class, rather than a silent failure.
        """
        pytest.importorskip("agno")

        def multiply(x: int, y: int) -> int:
            return x * y

        if HAS_AGNO_TOOL:
            agno_tool = AgnoTool(
                multiply,
                name="multiply",
                description="Multiply numbers",
            )  # type: ignore[call-arg]

            wrapped = from_agno_tool(agno_tool, num_cpus=1)

            assert isinstance(wrapped, Callable)
            assert wrapped.__name__ == "multiply"

            # Executes on Ray but should behave like a normal function
            result = wrapped(x=3, y=4)
            assert result == 12
        else:
            # Without Tool class, from_agno_tool cannot import Tool and
            # should raise ImportError to signal missing Agno tool support.
            with pytest.raises(
                ImportError, match="Agno tool conversion requires 'agno'"
            ):
                from_agno_tool(multiply, num_cpus=1)

    def test_from_agno_tool_rejects_non_agno_tool(self, ray_start):
        """Non-Agno objects should fail with a clear error.

        - When ``Tool`` exists, passing a non-Tool should raise ``ValueError``.
        - When ``Tool`` is absent, attempting conversion should raise
          ``ImportError`` because the adapter cannot even import the Tool
          class, which is an equally clear failure mode.
        """
        pytest.importorskip("agno")

        def plain_func(x: int) -> int:
            return x

        if HAS_AGNO_TOOL:
            with pytest.raises(ValueError, match="Expected Agno Tool"):
                _ = from_agno_tool(plain_func)  # type: ignore[arg-type]
        else:
            with pytest.raises(
                ImportError, match="Agno tool conversion requires 'agno'"
            ):
                from_agno_tool(plain_func)
