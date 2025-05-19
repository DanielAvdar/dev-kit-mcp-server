"""Module for creating and checking out a new branch from a source branch in a git repository."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core import AsyncOperation


@dataclass
class GitCreateBranchOperation(AsyncOperation):
    """Class to create and checkout a new branch from a source branch in a git repository."""

    name = "git_create_branch"

    async def __call__(
        self,
        new_branch: str,
        source_branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new branch from a source branch and checkout the new branch.

        Args:
            new_branch: Name of the new branch to create
            source_branch: Name of the source branch to create from (default: current branch)

        Returns:
            A dictionary containing the status of the create branch operation

        Raises:
            ValueError: If new_branch is not provided
            Exception: If the branch already exists or the source branch doesn't exist

        """
        # Validate input
        if not new_branch:
            raise ValueError("New branch name must be provided")

        # Get the repository
        repo = self._repo

        # Get the current branch if source_branch is not provided
        if not source_branch:
            source_branch = repo.active_branch.name

        # Check if the new branch already exists
        branch_exists = new_branch in [b.name for b in repo.branches]
        if branch_exists:
            raise Exception(f"Branch '{new_branch}' already exists.")

        # Check if the source branch exists
        source_exists = source_branch in [b.name for b in repo.branches]
        if not source_exists:
            raise Exception(f"Source branch '{source_branch}' does not exist.")

        # Create a new branch from the source branch
        # First, checkout the source branch
        repo.git.checkout(source_branch)
        # Then create and checkout the new branch
        repo.git.checkout("-b", new_branch)

        return {
            "status": "success",
            "message": f"Successfully created and checked out branch '{new_branch}' from '{source_branch}'",
            "new_branch": new_branch,
            "source_branch": source_branch,
        }
