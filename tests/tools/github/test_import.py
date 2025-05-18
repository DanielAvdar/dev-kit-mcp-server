"""Tests for the GitHub tools import behavior."""

import sys
from unittest.mock import patch

import pytest


def test_github_import_not_available():
    """Test that GitHub tools are not available when PyGithub is not installed."""
    # Mock sys.modules to simulate PyGithub not being installed
    with patch.dict(sys.modules, {"github": None}):
        # Import the tools module
        import importlib

        # Reload the github module first to ensure it picks up the mocked import
        if "dev_kit_mcp_server.tools.github" in sys.modules:
            importlib.reload(sys.modules["dev_kit_mcp_server.tools.github"])
        # Then reload the tools module
        importlib.reload(sys.modules["dev_kit_mcp_server.tools"])
        from dev_kit_mcp_server.tools import __all__ as tools_all

        # Check that GitHub tools are not in __all__
        assert "GitHubRepoOperation" not in tools_all
        assert "GitHubIssueOperation" not in tools_all
        assert "GitHubPROperation" not in tools_all


def test_github_import_available():
    """Test that GitHub tools are available when PyGithub is installed."""
    # Import the tools module
    import importlib

    # Check if PyGithub is available
    if importlib.util.find_spec("github") is None:
        # Skip the test if PyGithub is not installed
        pytest.skip("PyGithub is not installed")

    # Reload the github module first to ensure it's properly initialized
    if "dev_kit_mcp_server.tools.github" in sys.modules:
        importlib.reload(sys.modules["dev_kit_mcp_server.tools.github"])
    # Then reload the tools module
    importlib.reload(sys.modules["dev_kit_mcp_server.tools"])
    from dev_kit_mcp_server.tools import __all__ as tools_all

    # If PyGithub is installed, GitHub tools should be in __all__
    assert "GitHubRepoOperation" in tools_all
    assert "GitHubIssueOperation" in tools_all
    assert "GitHubPROperation" in tools_all
