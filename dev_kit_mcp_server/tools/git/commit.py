"""Module for committing changes to a git repository."""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from ..core import AsyncOperation


@dataclass
class GitCommitOperation(AsyncOperation):
    """Class to commit changes to a git repository."""

    name = "git_commit"

    async def __call__(
        self,
        message: str,
        files: List[str] = None,
        all_files: bool = False,
    ) -> Dict[str, Any]:
        """Commit changes to the git repository.

        Args:
            message: The commit message
            files: List of files to commit (default: None, which means all staged files)
            all_files: Whether to commit all changed files (default: False)

        Returns:
            A dictionary containing the status of the commit operation

        """
        try:
            # Get the repository
            repo = self._repo

            # Add files if specified
            if files:
                for file in files:
                    # Validate that the file is within the root directory
                    abs_path = self._validate_path_in_root(self._root_path, file)
                    repo.git.add(abs_path)
            elif all_files:
                repo.git.add(A=True)

            # Commit the changes
            if not message:
                return {
                    "error": "Commit message cannot be empty",
                }

            # Check if there are any changes to commit
            if not repo.is_dirty() and not files and not all_files:
                return {
                    "status": "warning",
                    "message": "No changes to commit",
                }

            # Commit the changes
            commit = repo.git.commit(m=message)

            return {
                "status": "success",
                "message": f"Successfully committed changes: {message}",
                "commit": commit,
            }
        except Exception as e:
            return {
                "error": f"Error committing changes: {str(e)}",
                "message": message,
                "files": files,
                "all_files": all_files,
            }

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        async def self_wrapper(
            message: str,
            files: List[str] = None,
            all_files: bool = False,
        ) -> Dict[str, Any]:
            """Commit changes to the git repository.

            Args:
                message: The commit message
                files: List of files to commit (default: None, which means all staged files)
                all_files: Whether to commit all changed files (default: False)

            Returns:
                A dictionary containing the status of the commit operation

            """
            return await self.__call__(message, files, all_files)

        self_wrapper.__name__ = self.name

        return self_wrapper
