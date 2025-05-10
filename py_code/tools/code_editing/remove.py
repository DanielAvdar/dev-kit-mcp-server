from dataclasses import dataclass
from typing import Any, Dict

from py_code.tools.code_editing.file_ops import FileOperation


@dataclass
class RemoveFileOperation(FileOperation):
    """Class to Remove a file or folder."""

    def __call__(self, path: str) -> Dict[str, Any]:
        """Remove a file or folder.

        Args:
            path: (str) to the folder to create
        Returns:
            A dictionary containing the status and path of the created file or folder.

        """
        try:
            self._remove_folder(path)  # todo: implement the function
        except Exception as e:
            return {
                "error": f"Error removing file or folder: {str(e)}",
                "path": path,
            }
