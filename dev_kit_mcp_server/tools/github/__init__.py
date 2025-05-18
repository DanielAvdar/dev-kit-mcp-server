"""GitHub tools for interacting with GitHub repositories.

This module provides tools for interacting with GitHub repositories.
It requires the PyGithub package to be installed, which is an optional dependency.
If PyGithub is not installed, the tools will not be available, but the rest of the
dev_kit_mcp_server package will still function normally.
"""

import importlib.util

# Check if PyGithub is available
GITHUB_AVAILABLE = importlib.util.find_spec("github") is not None

if GITHUB_AVAILABLE:
    from .issue import GitHubIssueOperation
    from .pr import GitHubPROperation
    from .repo import GitHubRepoOperation

    __all__ = [
        "GitHubRepoOperation",
        "GitHubIssueOperation",
        "GitHubPROperation",
    ]
else:
    __all__ = []
