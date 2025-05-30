"""Module for removing files and directories in the workspace."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ...core import AsyncOperation


@dataclass
class RemoveFileOperation(AsyncOperation):
    """Class to Remove a file or folder."""

    @property
    def _name(self) -> str:
        return "remove_file"

    def _remove_folder(self, path: str) -> None:
        """Remove a file or folder at the specified path.

        Args:
            path: Path to the file or folder to remove

        Raises:
            FileNotFoundError: If the path does not exist

        """
        # Validate that the path is within the root directory
        root_path = self._root_path
        abs_path = self._validate_path_in_root(root_path, path)

        # Check if path exists
        file_path = Path(abs_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Remove the file or folder
        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()

    async def __call__(self, path: str) -> Dict[str, Any]:
        """Remove a file or folder.

        Args:
            path: Path to the file or folder to remove

        Returns:
            A dictionary containing the status and path of the removed file or folder

        """
        # Handle both model and direct path input for backward compatibility

        self._remove_folder(path)
        return {
            "status": "success",
            "message": f"Successfully removed: {path}",
            "path": path,
        }
