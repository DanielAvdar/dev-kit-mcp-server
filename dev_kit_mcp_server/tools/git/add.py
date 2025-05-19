"""Module for adding files to the git index."""

from dataclasses import dataclass
from typing import Any, Dict, List

from ...core import AsyncOperation


@dataclass
class GitAddOperation(AsyncOperation):
    """Class to add files to the git index."""

    name = "git_add"

    async def __call__(
        self,
        paths: List[str],
    ) -> Dict[str, Any]:
        """Add files to the git index.

        Args:
            paths: List of file paths to add to the git index

        Returns:
            A dictionary containing the status of the add operation

        Raises:
            ValueError: If paths is not a list

        """
        # Validate input
        if not isinstance(paths, list):
            raise ValueError("Expected a list of file paths as the argument")

        # Get the repository
        repo = self._repo

        # Add the files to the index
        added_files = []
        for path in paths:
            # Validate that the path is within the root directory
            abs_path = self._validate_path_in_root(self._root_path, path)

            # Add the file to the index
            repo.git.add(abs_path)
            added_files.append(path)

        return {
            "status": "success",
            "message": f"Successfully added {len(added_files)} files to the index",
            "added_files": added_files,
        }
