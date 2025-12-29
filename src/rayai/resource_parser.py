"""Parse Ray resource hints from function docstrings.

Supports parsing `ray:` blocks in docstrings for resource configuration:

    def my_tool(query: str) -> str:
        '''Search the web.

        ray:
            num_cpus: 2
            num_gpus: 1
            memory: 4GB
        '''
        return results
"""

from __future__ import annotations

import re
from typing import Any


def parse_ray_resources(docstring: str | None) -> dict[str, Any]:
    """Parse ray resource hints from a function docstring.

    Looks for a `ray:` block in the docstring and parses YAML-like
    key: value pairs for resource configuration.

    Args:
        docstring: The function's docstring, or None.

    Returns:
        Dictionary with parsed resources. Possible keys:
        - num_cpus: int
        - num_gpus: int
        - memory: str (e.g., "4GB", "512MB")

    Example:
        >>> doc = '''My function.
        ...
        ... ray:
        ...     num_cpus: 2
        ...     memory: 4GB
        ... '''
        >>> parse_ray_resources(doc)
        {'num_cpus': 2, 'memory': '4GB'}
    """
    if not docstring:
        return {}

    resources: dict[str, Any] = {}

    # Look for "ray:" section (case-insensitive)
    # Matches "ray:", "Ray:", "RAY:" with optional whitespace
    ray_section_pattern = re.compile(
        r"^\s*ray\s*:\s*$",
        re.MULTILINE | re.IGNORECASE,
    )

    match = ray_section_pattern.search(docstring)
    if not match:
        return {}

    # Get the text after "ray:" until the next section or end
    start_pos = match.end()
    remaining = docstring[start_pos:]

    # Parse indented key: value pairs
    # Stop at next non-indented line or end of string
    lines = remaining.split("\n")

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Stop if we hit a non-indented line (new section)
        if line and not line[0].isspace():
            break

        # Parse key: value
        kv_match = re.match(r"^\s+(\w+)\s*:\s*(.+?)\s*$", line)
        if kv_match:
            key = kv_match.group(1).lower()
            value = kv_match.group(2)

            # Parse value based on key
            if key in ("num_cpus", "num_gpus"):
                try:
                    resources[key] = int(value)
                except ValueError:
                    # Try float for fractional resources
                    try:
                        resources[key] = float(value)
                    except ValueError:
                        pass  # Skip invalid values
            elif key == "memory":
                # Keep memory as string (e.g., "4GB", "512MB")
                resources[key] = value

    return resources


def parse_inline_ray_resources(docstring: str | None) -> dict[str, Any]:
    """Parse inline ray resource hints from docstring.

    Supports compact format: `ray: num_cpus=2, memory=4GB`

    Args:
        docstring: The function's docstring, or None.

    Returns:
        Dictionary with parsed resources.

    Example:
        >>> doc = "My function. ray: num_cpus=2, memory=4GB"
        >>> parse_inline_ray_resources(doc)
        {'num_cpus': 2, 'memory': '4GB'}
    """
    if not docstring:
        return {}

    resources: dict[str, Any] = {}

    # Look for inline format: "ray: key=value, key=value"
    inline_pattern = re.compile(
        r"ray\s*:\s*([\w\s=,]+?)(?:\n|$)",
        re.IGNORECASE,
    )

    match = inline_pattern.search(docstring)
    if not match:
        return {}

    # Parse comma-separated key=value pairs
    pairs_str = match.group(1)
    pairs = re.findall(r"(\w+)\s*=\s*([^\s,]+)", pairs_str)

    for key, value in pairs:
        key = key.lower()
        if key in ("num_cpus", "num_gpus"):
            try:
                resources[key] = int(value)
            except ValueError:
                try:
                    resources[key] = float(value)
                except ValueError:
                    pass
        elif key == "memory":
            resources[key] = value

    return resources


def parse_all_ray_resources(docstring: str | None) -> dict[str, Any]:
    """Parse ray resources from docstring, trying both formats.

    Tries block format first, then inline format.

    Args:
        docstring: The function's docstring, or None.

    Returns:
        Dictionary with parsed resources.
    """
    # Try block format first
    resources = parse_ray_resources(docstring)
    if resources:
        return resources

    # Fall back to inline format
    return parse_inline_ray_resources(docstring)
