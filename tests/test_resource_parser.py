"""Tests for docstring resource parsing."""

from rayai.resource_parser import (
    parse_all_ray_resources,
    parse_inline_ray_resources,
    parse_ray_resources,
)


class TestParseRayResources:
    """Tests for parse_ray_resources (block format)."""

    def test_empty_docstring(self):
        """Empty docstring returns empty dict."""
        assert parse_ray_resources(None) == {}
        assert parse_ray_resources("") == {}

    def test_no_ray_section(self):
        """Docstring without ray section returns empty dict."""
        doc = """This is a function.

        Args:
            x: An argument.
        """
        assert parse_ray_resources(doc) == {}

    def test_basic_resources(self):
        """Parse basic resources from docstring."""
        doc = """My function.

        ray:
            num_cpus: 2
            num_gpus: 1
            memory: 4GB
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 2, "num_gpus": 1, "memory": "4GB"}

    def test_partial_resources(self):
        """Parse partial resources."""
        doc = """My function.

        ray:
            num_cpus: 4
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 4}

    def test_fractional_cpus(self):
        """Parse fractional CPU resources."""
        doc = """My function.

        ray:
            num_cpus: 0.5
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 0.5}

    def test_memory_formats(self):
        """Parse different memory formats."""
        doc = """My function.

        ray:
            memory: 512MB
        """
        result = parse_ray_resources(doc)
        assert result == {"memory": "512MB"}

    def test_case_insensitive(self):
        """Ray section is case insensitive."""
        doc = """My function.

        Ray:
            num_cpus: 2
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 2}

    def test_extra_whitespace(self):
        """Handles extra whitespace."""
        doc = """My function.

        ray  :
            num_cpus:    2
            memory:  4GB
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 2, "memory": "4GB"}

    def test_stops_at_next_section(self):
        """Stops parsing at next non-indented line."""
        doc = """My function.

        ray:
            num_cpus: 2

        Args:
            x: An argument.
        """
        result = parse_ray_resources(doc)
        assert result == {"num_cpus": 2}


class TestParseInlineRayResources:
    """Tests for parse_inline_ray_resources (inline format)."""

    def test_empty_docstring(self):
        """Empty docstring returns empty dict."""
        assert parse_inline_ray_resources(None) == {}
        assert parse_inline_ray_resources("") == {}

    def test_no_inline_section(self):
        """Docstring without inline ray returns empty dict."""
        doc = "This is a function."
        assert parse_inline_ray_resources(doc) == {}

    def test_basic_inline(self):
        """Parse basic inline format."""
        doc = "My function. ray: num_cpus=2, memory=4GB"
        result = parse_inline_ray_resources(doc)
        assert result == {"num_cpus": 2, "memory": "4GB"}

    def test_single_value(self):
        """Parse single inline value."""
        doc = "My function. ray: num_cpus=4"
        result = parse_inline_ray_resources(doc)
        assert result == {"num_cpus": 4}


class TestParseAllRayResources:
    """Tests for parse_all_ray_resources (tries both formats)."""

    def test_prefers_block_format(self):
        """Block format takes precedence."""
        doc = """My function. ray: num_cpus=1

        ray:
            num_cpus: 4
        """
        result = parse_all_ray_resources(doc)
        assert result == {"num_cpus": 4}

    def test_falls_back_to_inline(self):
        """Falls back to inline when no block."""
        doc = "My function. ray: num_cpus=2"
        result = parse_all_ray_resources(doc)
        assert result == {"num_cpus": 2}

    def test_empty_returns_empty(self):
        """Empty when neither format found."""
        doc = "Just a function."
        result = parse_all_ray_resources(doc)
        assert result == {}
