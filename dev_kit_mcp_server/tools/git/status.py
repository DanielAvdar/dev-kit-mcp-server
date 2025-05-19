"""Module for getting the status of a git repository."""

from dataclasses import dataclass
from typing import Any, Dict

from ...core import AsyncOperation


@dataclass
class GitStatusOperation(AsyncOperation):
    """Class to get the status of a git repository."""

    name = "git_status"

    async def __call__(
        self,
    ) -> Dict[str, Any]:
        """Get the status of the git repository.

        Args:
            model: Parameters for getting the status (not used as this operation doesn't require any parameters)

        Returns:
            A dictionary containing the status of the git repository

        """
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
