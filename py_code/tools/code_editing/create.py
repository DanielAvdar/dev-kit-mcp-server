from dataclasses import dataclass
from typing import Any, Dict

from py_code.tools.code_editing.file_ops import FileOperation


@dataclass
class CreateDirOperation(FileOperation):
    """Class to create a  folder in the workspace."""

    def __call__(self, path: str) -> Dict[str, Any]:
        """Create a file or folder in the workspace.

        Args:
            path: (str) to the folder to create
        Returns:
            A dictionary containing the status and path of the created file or folder.

        """
        try:
            self._create_folder(path)  # todo: implement the function
        except Exception as e:
            return {
                "error": f"Error creating file or folder: {str(e)}",
                "path": path,
            }
