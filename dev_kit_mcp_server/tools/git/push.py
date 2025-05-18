"""Module for pushing changes to a remote git repository."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from ..core import AsyncOperation


@dataclass
class GitPushOperation(AsyncOperation):
    """Class to push changes to a remote git repository."""

    name = "git_push"

    async def __call__(
        self,
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
            return await self.__call__(remote, branch, force)

        self_wrapper.__name__ = self.name

        return self_wrapper
