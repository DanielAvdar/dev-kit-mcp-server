"""Module for creating directories in the workspace."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from pydantic import Field

from ..core import FileOperation
from ..core.models import BaseToolParams


class CreateDirParams(BaseToolParams):
    """Parameters for creating a directory."""

    path: str = Field(
        ...,
        description="Path to the folder to create",
    )


@dataclass
class CreateDirOperation(FileOperation):
    """Class to create a folder in the workspace."""

    name = "create_dir"
    model_class = CreateDirParams

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

    def __call__(self, model_or_path: CreateDirParams | str) -> Dict[str, Any]:
        """Create a file or folder in the workspace.

        Args:
            model_or_path: Parameters for creating a directory or a path string

        Returns:
            A dictionary containing the status and path of the created file or folder

        """
        # Handle both model and direct path input for backward compatibility
        if isinstance(model_or_path, str):
            path = model_or_path
        else:
            path = model_or_path.path

        try:
            self._create_folder(path)
            return {
                "status": "success",
                "message": f"Successfully created folder: {path}",
                "path": path,
            }
        except Exception as e:
            return {
                "error": f"Error creating file or folder: {str(e)}",
                "path": path,
            }
