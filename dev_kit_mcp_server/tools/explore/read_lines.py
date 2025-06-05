"""Module for reading specific lines or ranges from files."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from ...core import AsyncOperation


@dataclass
class ReadLinesOperation(AsyncOperation):
    """Class to read specific lines or a range from a file."""

    name = "read_lines"

    def _read_lines(
        self,
        file_path: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Read specific lines or a range from a file.

        Args:
            file_path: Path to the file to read
            start: Starting line number (1-based, optional)
            end: Ending line number (1-based, inclusive, optional)
            max_chars: Maximum characters to return in output

        Returns:
            Dictionary with file content and metadata

        Raises:
            ValueError: If line numbers are invalid or file path is invalid
            FileNotFoundError: If file does not exist
            IsADirectoryError: If path is a directory

        """
        # Validate file path
        abs_path = self._validate_path_in_root(self._root_path, file_path)
        file_obj = Path(abs_path)

        if not file_obj.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        if file_obj.is_dir():
            raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")

        # Read the file
        try:
            with open(file_obj, "r", encoding="utf-8", errors="ignore") as f:
                all_lines = f.readlines()
        except (OSError, PermissionError) as e:
            raise ValueError(f"Cannot read file {file_path}: {e}") from e

        total_lines = len(all_lines)

        # Determine line range
        if start is None:
            start = 1
        if end is None:
            end = total_lines

        # Validate line numbers
        if start < 1:
            raise ValueError(f"Start line must be at least 1, got {start}")
        if end < start:
            raise ValueError(f"End line must be greater than or equal to start line, got {end} < {start}")

        # Adjust line numbers to be within file bounds
        actual_start = max(1, min(start, total_lines + 1))
        actual_end = max(actual_start, min(end, total_lines))

        # Extract the requested lines (convert to 0-based indexing)
        if actual_start > total_lines:
            selected_lines = []
        else:
            start_idx = actual_start - 1
            end_idx = actual_end
            selected_lines = all_lines[start_idx:end_idx]

        # Prepare output
        content_lines = []

        # Add file header
        try:
            relative_path = file_obj.relative_to(self._root_path)
        except ValueError:
            relative_path = file_obj

        if selected_lines:
            content_lines.append(f"=== {relative_path} (lines {actual_start}-{actual_end} of {total_lines}) ===")
            content_lines.append("")

            # Add line numbers and content
            for i, line in enumerate(selected_lines):
                line_num = actual_start + i
                content_lines.append(f"{line_num:4d}: {line.rstrip()}")
        else:
            content_lines.append(f"=== {relative_path} ===")
            content_lines.append("")
            content_lines.append(f"No lines to display (requested lines {start}-{end}, file has {total_lines} lines)")

        content = "\n".join(content_lines)
        total_chars = len(content)
        truncated = total_chars > max_chars

        if truncated:
            content = content[:max_chars]

        return {
            "content": content,
            "total_chars": total_chars,
            "truncated": truncated,
            "file_path": str(relative_path),
            "total_lines_in_file": total_lines,
            "requested_start": start,
            "requested_end": end,
            "actual_start": actual_start,
            "actual_end": actual_end,
            "lines_returned": len(selected_lines),
        }

    async def __call__(
        self,
        file_path: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Read specific lines or a range from a file.

        Args:
            file_path: Path to the file to read (required)
            start: Starting line number (1-based, optional, defaults to 1)
            end: Ending line number (1-based, inclusive, optional, defaults to end of file)
            max_chars: Maximum characters to return in output (optional, default 2000)

        Returns:
            A dictionary containing the file content and metadata

        """
        try:
            result = self._read_lines(file_path, start, end, max_chars)
            return {
                "status": "success",
                "message": f"Successfully read {result['lines_returned']} lines from {result['file_path']}",
                **result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to read lines from file: {str(e)}",
                "error": str(e),
                "file_path": file_path,
                "start": start,
                "end": end,
            }
