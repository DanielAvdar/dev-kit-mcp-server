import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .file_ops import FileOperation


@dataclass(unsafe_hash=True, slots=True)
class MoveDirOperation(FileOperation):
    # __slots__ = ("_root_path",)
    """Class to move a file or folder in the workspace."""

    name = "move_dir_tool"

    def _move_folder(self, path1: str, path2: str) -> None:
        """Move a file or folder from path1 to path2.

        Args:
            path1: Source path
            path2: Destination path

        Raises:
            ValueError: If either path is not within the root directory
            FileNotFoundError: If the source path does not exist
            FileExistsError: If the destination path already exists
            OSError: If there's an error moving the file or folder

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

    def __call__(self, path1: str, path2: str) -> Dict[str, Any]:
        """Move a file or folder from path1 to path2.

        Args:
            path1: (str) Source path
            path2: (str) Destination path
        Returns:
            A dictionary containing the status and paths of the moved file or folder.

        """
        try:
            self._move_folder(path1, path2)
            return {
                "status": "success",
                "message": f"Successfully moved from {path1} to {path2}",
                "path1": path1,
                "path2": path2,
            }
        except Exception as e:
            return {
                "error": f"Error moving file or folder: {str(e)}",
                "path1": path1,
                "path2": path2,
            }
