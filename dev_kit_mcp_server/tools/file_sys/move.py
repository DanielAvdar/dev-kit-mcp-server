"""Module for moving files and directories in the workspace."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ...core import AsyncOperation


@dataclass(unsafe_hash=True, slots=True)
class MoveDirOperation(AsyncOperation):
    """Class to move a file or folder in the workspace."""

    name = "move_dir"

    def _move_folder(self, path1: str, path2: str) -> None:
        """Move a file or folder from path1 to path2.

        Args:
            path1: Source path
            path2: Destination path

        Raises:
            FileNotFoundError: If the source path does not exist
            FileExistsError: If the destination path already exists

        """
        root_path = self._root_path
        abs_path1 = self._validate_path_in_root(root_path, path1)
        abs_path2 = self._validate_path_in_root(root_path, path2)

        # Check if source exists
        source_path = Path(abs_path1)
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {path1}")

        # Check if destination exists
        dest_path = Path(abs_path2)
        if dest_path.exists():
            raise FileExistsError(f"Destination path already exists: {path2}")

        # Create parent directories of destination if they don't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Move the file or folder
        shutil.move(str(source_path), str(dest_path))

    async def __call__(self, path1: str = None, path2: str = None) -> Dict[str, Any]:
        """Move a file or folder from path1 to path2.

        Args:
            path1: Source path of the file or folder to move
            path2: Destination path where the file or folder will be moved to

        Returns:
            A dictionary containing the status and paths of the moved file or folder

        """
        # Handle both model and direct path input for backward compatibility

        self._move_folder(path1, path2)
        return {
            "status": "success",
            "message": f"Successfully moved from {path1} to {path2}",
            "path1": path1,
            "path2": path2,
        }
