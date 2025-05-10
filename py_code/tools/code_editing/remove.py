import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from py_code.tools.code_editing.file_ops import FileOperation


@dataclass
class RemoveFileOperation(FileOperation):
    """Class to Remove a file or folder."""

    name = "remove_file_tool"

    def _remove_folder(self, path: str) -> None:
        """Remove a file or folder at the specified path.

        Args:
            path: Path to the file or folder to remove

        Raises:
            ValueError: If the path is not within the root directory
            FileNotFoundError: If the path does not exist
            OSError: If there's an error removing the file or folder

        """
        # Validate that the path is within the root directory
        abs_path = self._validate_path_in_root(path)

        # Check if path exists
        file_path = Path(abs_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Remove the file or folder
        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()

    def __call__(self, path: str) -> Dict[str, Any]:
        """Remove a file or folder.

        Args:
            path: (str) Path to the file or folder to remove
        Returns:
            A dictionary containing the status and path of the removed file or folder.

        """
        try:
            self._remove_folder(path)
            return {
                "status": "success",
                "message": f"Successfully removed: {path}",
                "path": path,
            }
        except Exception as e:
            return {
                "error": f"Error removing file or folder: {str(e)}",
                "path": path,
            }
