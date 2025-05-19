"""Tools subpackage for MCP server implementations."""

import importlib.util

from .commands_tool import ExecMakeTarget
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
    "GitStatusOperation",
    "GitCommitOperation",
    "GitPushOperation",
    "GitAddOperation",
    "GitPullOperation",
    "GitCheckoutOperation",
    "ExecMakeTarget",
    "FileOperation",
]
