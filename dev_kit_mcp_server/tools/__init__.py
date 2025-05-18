"""Tools subpackage for MCP server implementations."""

import importlib.util

from .core import FileOperation
from .file_sys.create import CreateDirOperation
from .file_sys.move import MoveDirOperation
from .file_sys.remove import RemoveFileOperation
from .file_sys.rename import RenameOperation
from .git.add import GitAddOperation
from .git.checkout import GitCheckoutOperation
from .git.commit import GitCommitOperation
from .git.pull import GitPullOperation
from .git.push import GitPushOperation
from .git.status import GitStatusOperation

# Check if PyGithub is available
GITHUB_AVAILABLE = importlib.util.find_spec("github") is not None

__all__ = [
    "CreateDirOperation",
    "RemoveFileOperation",
    "MoveDirOperation",
    "RenameOperation",
    "FileOperation",
    "GitStatusOperation",
    "GitCommitOperation",
    "GitPushOperation",
    "GitAddOperation",
    "GitPullOperation",
    "GitCheckoutOperation",
    "GitHubIssueOperation",
    "GitHubPROperation",
    "GitHubRepoOperation",
]

# Add GitHub tools to __all__ if available
if GITHUB_AVAILABLE:
    # Import GitHub operations only if PyGithub is available
    from .github.issue import GitHubIssueOperation
    from .github.pr import GitHubPROperation
    from .github.repo import GitHubRepoOperation

    __all__.extend([
        "GitHubRepoOperation",
        "GitHubIssueOperation",
        "GitHubPROperation",
    ])
