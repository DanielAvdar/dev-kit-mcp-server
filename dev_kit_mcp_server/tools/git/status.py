"""Module for getting the status of a git repository."""

from dataclasses import dataclass
from typing import Any, Callable, Dict

from ..core import AsyncOperation


@dataclass
class GitStatusOperation(AsyncOperation):
    """Class to get the status of a git repository."""

    name = "git_status"

    async def __call__(self) -> Dict[str, Any]:
        """Get the status of the git repository.

        Returns:
            A dictionary containing the status of the git repository

        """
        try:
            # Get the status of the repository
            repo = self._repo

            # Get the current branch
            try:
                branch = repo.active_branch.name
            except TypeError:
                branch = "DETACHED_HEAD"

            # Get the status
            changed_files = []
            for item in repo.index.diff(None):
                changed_files.append({
                    "path": item.a_path,
                    "change_type": item.change_type,
                })

            # Get untracked files
            untracked_files = repo.untracked_files

            # Get staged files
            staged_files = []
            for item in repo.index.diff("HEAD"):
                staged_files.append({
                    "path": item.a_path,
                    "change_type": item.change_type,
                })

            return {
                "status": "success",
                "branch": branch,
                "changed_files": changed_files,
                "untracked_files": untracked_files,
                "staged_files": staged_files,
            }
        except Exception as e:
            return {
                "error": f"Error getting git status: {str(e)}",
            }

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        async def self_wrapper() -> Dict[str, Any]:
            """Get the status of the git repository.

            Returns:
                A dictionary containing the status of the git repository

            """
            return await self.__call__()

        self_wrapper.__name__ = self.name

        return self_wrapper
