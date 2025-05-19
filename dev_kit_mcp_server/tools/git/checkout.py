"""Module for checking out branches in a git repository."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ...core import AsyncOperation


@dataclass
class GitCheckoutOperation(AsyncOperation):
    """Class to checkout branches in a git repository."""

    name = "git_checkout"

    async def __call__(
        self,
        branch: str,
        create: Optional[bool] = False,
    ) -> Dict[str, Any]:
        """Checkout a branch in the git repository.

        Args:
            branch: Name of the branch to checkout
            create: Whether to create the branch if it doesn't exist (default: False)

        Returns:
            A dictionary containing the status of the checkout operation

        Raises:
            ValueError: If branch is not provided
            Exception: If the branch doesn't exist and create is False

        """
        # Validate input
        if not branch:
            raise ValueError("Branch name must be provided")

        # Get the repository
        repo = self._repo

        # Check if the branch exists
        branch_exists = branch in [b.name for b in repo.branches]

        # If the branch doesn't exist and create is False, raise an exception
        if not branch_exists and not create:
            raise Exception(f"Branch '{branch}' does not exist. Use create=True to create it.")

        # Checkout the branch
        if branch_exists:
            # Checkout existing branch
            repo.git.checkout(branch)
            message = f"Successfully checked out branch '{branch}'"
        else:
            # Create and checkout new branch
            repo.git.checkout("-b", branch)
            message = f"Successfully created and checked out branch '{branch}'"

        return {
            "status": "success",
            "message": message,
            "branch": branch,
            "created": not branch_exists and create,
        }
