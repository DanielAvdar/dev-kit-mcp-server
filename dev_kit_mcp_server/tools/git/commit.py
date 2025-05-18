"""Module for committing changes to a git repository."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import Field

from ..core import AsyncOperation
from ..core.models import BaseToolParams


class GitCommitParams(BaseToolParams):
    """Parameters for committing changes to a git repository."""

    message: str = Field(
        ...,
        description="The commit message",
    )
    files: Optional[List[str]] = Field(
        None,
        description="List of files to commit (default: None, which means all staged files)",
    )
    all_files: bool = Field(
        False,
        description="Whether to commit all changed files (default: False)",
    )


@dataclass
class GitCommitOperation(AsyncOperation):
    """Class to commit changes to a git repository."""

    name = "git_commit"
    model_class = GitCommitParams

    async def __call__(
        self,
        model_or_message: GitCommitParams | str,
        files: List[str] = None,
        all_files: bool = False,
    ) -> Dict[str, Any]:
        """Commit changes to the git repository.

        Args:
            model_or_message: Parameters for committing changes or a commit message
            files: List of files to commit (default: None, which means all staged files)
            all_files: Whether to commit all changed files (default: False)

        Returns:
            A dictionary containing the status of the commit operation

        """
        # Handle both model and direct parameter input for backward compatibility
        if isinstance(model_or_message, str):
            message = model_or_message
        else:
            message = model_or_message.message
            files = model_or_message.files
            all_files = model_or_message.all_files

        try:
            # Get the repository
            repo = self._repo

            # Add files if specified
            if files:
                for file in files:
                    # Validate that the file is within the root directory
                    abs_path = self._validate_path_in_root(self._root_path, file)
                    repo.git.add(abs_path)
            elif all_files:
                repo.git.add(A=True)

            # Commit the changes
            if not message:
                return {
                    "error": "Commit message cannot be empty",
                }

            # Check if there are any changes to commit
            if not repo.is_dirty() and not files and not all_files:
                return {
                    "status": "warning",
                    "message": "No changes to commit",
                }

            # Commit the changes
            commit = repo.git.commit(m=message)

            return {
                "status": "success",
                "message": f"Successfully committed changes: {message}",
                "commit": commit,
            }
        except Exception as e:
            return {
                "error": f"Error committing changes: {str(e)}",
                "message": message,
                "files": files,
                "all_files": all_files,
            }
