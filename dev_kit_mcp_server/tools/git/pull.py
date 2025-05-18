"""Module for pulling changes from a remote git repository."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from pydantic import Field

from ..core import AsyncOperation
from ..core.models import BaseToolParams


class GitPullParams(BaseToolParams):
    """Parameters for pulling changes from a remote git repository."""

    remote: str = Field(
        "origin",
        description="The name of the remote repository",
    )
    branch: Optional[str] = Field(
        None,
        description="The name of the branch to pull (default: None, which means the current branch)",
    )
    rebase: bool = Field(
        False,
        description="Whether to rebase instead of merge",
    )


@dataclass
class GitPullOperation(AsyncOperation):
    """Class to pull changes from a remote git repository."""

    name = "git_pull"
    model_class = GitPullParams

    async def __call__(
        self,
        model_or_remote: GitPullParams | str = "origin",
        branch: Optional[str] = None,
        rebase: bool = False,
    ) -> Dict[str, Any]:
        """Pull changes from a remote git repository.

        Args:
            model_or_remote: Parameters for pulling changes or the name of the remote repository
            branch: The name of the branch to pull (only used if model_or_remote is a string)
            rebase: Whether to rebase instead of merge (only used if model_or_remote is a string)

        Returns:
            A dictionary containing the status of the pull operation

        """
        # Handle both model and direct parameter input for backward compatibility
        if isinstance(model_or_remote, str):
            remote = model_or_remote
        else:
            remote = model_or_remote.remote
            branch = model_or_remote.branch
            rebase = model_or_remote.rebase

        try:
            # Get the repository
            repo = self._repo

            # Get the current branch if not specified
            if branch is None:
                try:
                    branch = repo.active_branch.name
                except TypeError:
                    return {
                        "error": "Cannot pull in detached HEAD state. Please specify a branch.",
                    }

            # Check if the remote exists
            try:
                repo.remote(remote)
            except ValueError:
                return {
                    "error": f"Remote '{remote}' does not exist",
                    "remote": remote,
                    "branch": branch,
                }

            # Pull the changes
            pull_options = []
            if rebase:
                pull_options.append("--rebase")

            pull_info = repo.git.pull(remote, branch, *pull_options)

            return {
                "status": "success",
                "message": f"Successfully pulled changes from {remote}/{branch}",
                "pull_info": pull_info,
                "remote": remote,
                "branch": branch,
            }
        except Exception as e:
            return {
                "error": f"Error pulling changes: {str(e)}",
                "remote": remote,
                "branch": branch,
                "rebase": rebase,
            }

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        async def self_wrapper(
            remote: str = "origin",
            branch: Optional[str] = None,
            rebase: bool = False,
        ) -> Dict[str, Any]:
            """Pull changes from a remote git repository.

            Args:
                remote: The name of the remote repository (default: "origin")
                branch: The name of the branch to pull (default: None, which means the current branch)
                rebase: Whether to rebase instead of merge (default: False)

            Returns:
                A dictionary containing the status of the pull operation

            """
            # Create a model with the parameters
            model = self.model_class(remote=remote, branch=branch, rebase=rebase)
            return await self.__call__(model)

        self_wrapper.__name__ = self.name

        return self_wrapper
