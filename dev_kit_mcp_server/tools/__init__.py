"""Tools subpackage for MCP server implementations."""

import importlib.util

from .commands import ExecMakeTarget
from .file_sys.create import CreateDirOperation
from .file_sys.edit import EditFileOperation
from .file_sys.move import MoveDirOperation
from .file_sys.remove import RemoveFileOperation
from .file_sys.rename import RenameOperation
from .git.add import GitAddOperation
from .git.checkout import GitCheckoutOperation
from .git.commit import GitCommitOperation
from .git.create_branch import GitCreateBranchOperation
from .git.diff import GitDiffOperation
from .git.pull import GitPullOperation
from .git.push import GitPushOperation
from .git.status import GitStatusOperation

# Check if PyGithub is available
GITHUB_AVAILABLE = importlib.util.find_spec("github") is not None

__all__ = [
    "CreateDirOperation",
    "EditFileOperation",
    "RemoveFileOperation",
    "MoveDirOperation",
    "RenameOperation",
    "GitStatusOperation",
    "GitCommitOperation",
    "GitPushOperation",
    "GitAddOperation",
    "GitPullOperation",
    "GitCheckoutOperation",
    "GitCreateBranchOperation",
    "GitDiffOperation",
    "ExecMakeTarget",
]
