"""Module for creating directories in the workspace."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ..core import AsyncOperation


@dataclass
class CreateDirOperation(AsyncOperation):
    """Class to create a folder in the workspace."""

    name = "create_dir"

    def _create_folder(self, path: str) -> None:
        """Create a folder at the specified path.

        Args:
            path: Path to the folder to create

        Raises:
            FileExistsError: If the path already exists

        """
        # Validate that the path is within the root directory
        root_path = self._root_path
        abs_path = self._validate_path_in_root(root_path, path)

        # Create the folder
        folder_path = Path(abs_path)
        if folder_path.exists():
            raise FileExistsError(f"Path already exists: {path}")

        # Create parent directories if they don't exist
        folder_path.mkdir(parents=True, exist_ok=False)

    async def __call__(self, path: str) -> Dict[str, Any]:
        """Create a file or folder in the workspace.

        Args:
            path: Path to the folder to create

        Returns:
            A dictionary containing the status and path of the created file or folder

        """
        # Handle both model and direct path input for backward compatibility

        self._create_folder(path)
        return {
            "status": "success",
            "message": f"Successfully created folder: {path}",
            "path": path,
        }
