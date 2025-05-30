"""Module for showing diffs in a git repository."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from ...core import AsyncOperation


@dataclass
class GitDiffOperation(AsyncOperation):
    """Class to show diffs in a git repository."""

    @property
    def _name(self) -> str:
        return "git_diff"

    async def __call__(
        self,
        path_or_commit: str,
        options: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Show diffs in the git repository.

        Args:
            path_or_commit: Path to the file to diff or commit to diff against
            options: Additional options to pass to git diff (default: None)

        Returns:
            A dictionary containing the diff output

        Raises:
            ValueError: If path_or_commit is not provided

        """
        # Validate input
        if not path_or_commit:
            raise ValueError("Path or commit must be provided")

        # Get the repository
        repo = self._repo

        # Prepare the diff command
        diff_args = []

        # Add options if provided
        if options:
            diff_args.extend(options.split())

        # Add the path or commit
        diff_args.append(path_or_commit)

        # Get the diff
        diff_output = repo.git.diff(*diff_args)

        return {
            "status": "success",
            "message": f"Successfully generated diff for '{path_or_commit}'",
            "diff": diff_output,
        }
