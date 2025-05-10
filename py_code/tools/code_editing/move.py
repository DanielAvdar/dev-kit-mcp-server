from dataclasses import dataclass
from typing import Any, Dict

from py_code.tools.code_editing.file_ops import FileOperation


@dataclass
class MoveDirOperation(FileOperation):
    """Class to create a  folder in the workspace."""

    def __call__(self, path1: str, path2: str) -> Dict[str, Any]:
        """Remove a file or folder.

        Args:
            path: (str) to the folder to create
        Returns:
            A dictionary containing the status and path of the created file or folder.

        """
        try:
            self._move_folder(path1, path2)  # todo: implement the function
        except Exception as e:
            return {
                "error": f"Error removing file or folder: {str(e)}",
                "path1": path1,
                "path2": path2,
            }
