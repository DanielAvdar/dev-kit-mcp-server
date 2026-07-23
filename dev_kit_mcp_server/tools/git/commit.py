"""Module for committing changes to a git repository."""

from dataclasses import dataclass
from typing import Any, Dict

from ...core import AsyncOperation


@dataclass
class GitCommitOperation(AsyncOperation):
    """Class to commit changes to a git repository."""

    _name = "git_commit"

    async def __call__(
        self,
        message: str,
    ) -> Dict[str, Any]:
        """Commit changes to the git repository.

        Args:
            message: Parameters for committing changes or a commit message


        Returns:
            A dictionary containing the status of the commit operation

        """
        # Handle both model and direct parameter input for backward compatibility

        # Get the repository
        repo = self._repo

        # Commit the changes
        if not message:
            return {
                "error": "Commit message cannot be empty",
            }

        # Commit the changes
        commit = repo.git.commit(m=message)

        return {
            "status": "success",
            "message": f"Successfully committed changes: {message}",
            "commit": commit,
        }
