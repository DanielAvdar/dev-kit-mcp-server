"""Module for pulling changes from a remote git repository."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ...core import AsyncOperation


@dataclass
class GitPullOperation(AsyncOperation):
    """Class to pull changes from a remote git repository."""

    @property
    def _name(self) -> str:
        return "git_pull"

    async def __call__(
        self,
        remote: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pull changes from a remote git repository.

        Args:
            remote: Name of the remote to pull from (default: origin)
            branch: Name of the branch to pull (default: current branch)

        Returns:
            A dictionary containing the status of the pull operation

        """
        # Get the repository
        repo = self._repo

        # Get the remote (default to 'origin' if not specified)
        remote_name = remote or "origin"

        # Check if the remote exists - let the ValueError propagate
        repo_remote = repo.remote(remote_name)

        # Get the branch (default to current branch if not specified)
        branch_name = branch
        if not branch_name:
            # Let the TypeError propagate if HEAD is detached
            branch_name = repo.active_branch.name

        # Pull the changes
        pull_info = repo_remote.pull(branch_name)

        # Process the pull results
        results = []
        for info in pull_info:
            results.append({
                "ref": info.ref,
                "flags": info.flags,
                "note": info.note,
                "summary": str(info.commit),
            })

        return {
            "status": "success",
            "message": f"Successfully pulled from {remote_name}/{branch_name}",
            "remote": remote_name,
            "branch": branch_name,
            "results": results,
        }
