"""Module for pushing changes to a remote git repository."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from pydantic import Field

from ..core import AsyncOperation
from ..core.models import BaseToolParams


class GitPushParams(BaseToolParams):
    """Parameters for pushing changes to a remote git repository."""

    remote: str = Field(
        "origin",
        description="The name of the remote repository",
    )
    branch: Optional[str] = Field(
        None,
        description="The name of the branch to push (default: None, which means the current branch)",
    )
    force: bool = Field(
        False,
        description="Whether to force push",
    )


@dataclass
class GitPushOperation(AsyncOperation):
    """Class to push changes to a remote git repository."""

    name = "git_push"
    model_class = GitPushParams

    async def __call__(
        self,
        model_or_remote: GitPushParams | str = "origin",
        branch: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Push changes to a remote git repository.

        Args:
            model_or_remote: Parameters for pushing changes or the name of the remote repository
            branch: The name of the branch to push (only used if model_or_remote is a string)
            force: Whether to force push (only used if model_or_remote is a string)

        Returns:
            A dictionary containing the status of the push operation

        """
        # Handle both model and direct parameter input for backward compatibility
        if isinstance(model_or_remote, str):
            remote = model_or_remote
        else:
            remote = model_or_remote.remote
            branch = model_or_remote.branch
            force = model_or_remote.force

        try:
            # Get the repository
            repo = self._repo

            # Get the current branch if not specified
            if branch is None:
                try:
                    branch = repo.active_branch.name
                except TypeError:
                    return {
                        "error": "Cannot push from detached HEAD state. Please specify a branch.",
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

            # Push the changes
            push_options = []
            if force:
                push_options.append("--force")

            push_info = repo.git.push(remote, branch, *push_options)

            return {
                "status": "success",
                "message": f"Successfully pushed changes to {remote}/{branch}",
                "push_info": push_info,
                "remote": remote,
                "branch": branch,
            }
        except Exception as e:
            return {
                "error": f"Error pushing changes: {str(e)}",
                "remote": remote,
                "branch": branch,
                "force": force,
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
            force: bool = False,
        ) -> Dict[str, Any]:
            """Push changes to a remote git repository.

            Args:
                remote: The name of the remote repository (default: "origin")
                branch: The name of the branch to push (default: None, which means the current branch)
                force: Whether to force push (default: False)

            Returns:
                A dictionary containing the status of the push operation

            """
            # Create a model with the parameters
            model = self.model_class(remote=remote, branch=branch, force=force)
            return await self.__call__(model)

        self_wrapper.__name__ = self.name

        return self_wrapper
