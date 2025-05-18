"""Module for removing files and directories in the workspace."""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict

from pydantic import Field

from ..core import FileOperation
from ..core.models import BaseToolParams


class RemoveFileParams(BaseToolParams):
    """Parameters for removing a file or directory."""

    path: str = Field(
        ...,
        description="Path to the file or folder to remove",
    )


@dataclass
class RemoveFileOperation(FileOperation):
    """Class to Remove a file or folder."""

    name = "remove_file"
    model_class = RemoveFileParams

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

    def __call__(self, model_or_path: RemoveFileParams | str) -> Dict[str, Any]:
        """Remove a file or folder.

        Args:
            model_or_path: Parameters for removing a file or directory or a path string

        Returns:
            A dictionary containing the status and path of the removed file or folder

        """
        # Handle both model and direct path input for backward compatibility
        if isinstance(model_or_path, str):
            path = model_or_path
        else:
            path = model_or_path.path

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

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        def self_wrapper(
            path: str,
        ) -> Dict[str, Any]:
            """Remove a file or folder.

            Args:
                path: Path to the file or folder to remove

            Returns:
                A dictionary containing the status and path of the removed file or folder

            """
            # Create a model with the parameter
            model = self.model_class(path=path)
            return self.__call__(model)

        self_wrapper.__name__ = self.name

        return self_wrapper
