"""Module for editing files in the workspace."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from ..core import AsyncOperation


@dataclass
class EditFileOperation(AsyncOperation):
    """Class to edit a file in the workspace by replacing lines between start and end with new text."""

    name = "edit_file"

    def _edit_file(self, path: str, start_line: int, end_line: int, text: str) -> None:
        """Edit a file by replacing lines between start and end with new text.

        Args:
            path: Path to the file to edit
            start_line: Line number to start replacing from (1-based)
            end_line: Line number to end replacing at (1-based, inclusive)
            text: Text to insert between start_line and end_line

        Raises:
            FileNotFoundError: If the path does not exist
            ValueError: If start_line or end_line is invalid
            IsADirectoryError: If the path is a directory

        """
        # Validate that the path is within the root directory
        root_path = self._root_path
        abs_path = self._validate_path_in_root(root_path, path)

        # Check if path exists
        file_path = Path(abs_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Check if path is a file
        if file_path.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {path}")

        # Validate line numbers
        if start_line < 1:
            raise ValueError(f"Start line must be at least 1, got {start_line}")
        if end_line < start_line:
            raise ValueError(f"End line must be greater than or equal to start line, got {end_line} < {start_line}")

        # Read the file
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Validate line numbers against file length
        if start_line > len(lines) + 1:
            raise ValueError(f"Start line {start_line} is beyond the end of the file ({len(lines)} lines)")
        if end_line > len(lines):
            end_line = len(lines)  # Adjust end_line if it's beyond the file length

        # Prepare the new content
        # Convert text to lines with newline characters
        new_lines = text.splitlines(True)
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] += "\n"  # Ensure the last line ends with a newline

        # Replace the lines
        new_content = lines[: start_line - 1] + new_lines + lines[end_line:]

        # Write the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_content)

    async def __call__(self, path: str, start_line: int, end_line: int, text: str) -> Dict[str, Any]:
        """Edit a file by replacing lines between start and end with new text.

        Args:
            path: Path to the file to edit
            start_line: Line number to start replacing from (1-based)
            end_line: Line number to end replacing at (1-based, inclusive)
            text: Text to insert between start_line and end_line

        Returns:
            A dictionary containing the status and details of the edit operation

        """
        self._edit_file(path, start_line, end_line, text)
        return {
            "status": "success",
            "message": f"Successfully edited file: {path}",
            "path": path,
            "start_line": start_line,
            "end_line": end_line,
            "text_length": len(text),
        }
