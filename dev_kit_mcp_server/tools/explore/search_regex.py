"""Module for targeted regex pattern searching in specific files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from ...core import AsyncOperation


@dataclass
class SearchRegexOperation(AsyncOperation):
    """Class to search for regex patterns in specified files only."""

    name = "search_regex"

    def _search_regex(
        self,
        pattern: str,
        files: List[str],
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Search for regex patterns in specified files.

        Args:
            pattern: Regex pattern to match against file content
            files: List of file paths to search (required)
            max_chars: Maximum characters to return in output

        Returns:
            Dictionary with search results

        Raises:
            ValueError: If pattern is invalid regex, file paths are invalid, or files list is empty

        """
        if not files:
            raise ValueError("Files list cannot be empty. Please specify at least one file to search.")

        # Validate regex pattern
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}. Error: {e}") from e

        # Validate and collect specified files
        search_files: List[Path] = []
        for file_str in files:
            abs_path = self._validate_path_in_root(self._root_path, file_str)
            file_path = Path(abs_path)
            if not file_path.exists():
                raise ValueError(f"File does not exist: {file_str}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_str}")
            search_files.append(file_path)

        # Search for matches
        matches: List[Dict[str, Any]] = []
        total_files_searched = 0
        total_lines_searched = 0

        for file_path in search_files:
            total_files_searched += 1
            try:
                # Try to read as text file
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()

                total_lines_searched += len(lines)

                # Find matching lines
                for line_num, line in enumerate(lines, 1):
                    if compiled_pattern.search(line):
                        # Get relative path from project root
                        try:
                            relative_path = file_path.relative_to(self._root_path)
                        except ValueError:
                            relative_path = file_path

                        match_data = {
                            "file": str(relative_path),
                            "line_number": line_num,
                            "line": line.rstrip("\n\r"),
                        }

                        matches.append(match_data)

            except (UnicodeDecodeError, OSError, PermissionError) as e:
                raise ValueError(f"Failed to read file {file_path}: {str(e)}") from e

        # Prepare output
        files_list = ", ".join(files)
        content_lines = [f"Regex search results for pattern '{pattern}' in files: {files_list}", ""]

        if not matches:
            content_lines.append("No matches found")
        else:
            for match in matches:
                # Simple format: file_path:line_number: line_content
                content_lines.append(f"{match['file']}:{match['line_number']}: {match['line']}")

        content = "\n".join(content_lines)
        total_chars = len(content)
        truncated = total_chars > max_chars

        if truncated:
            content = content[:max_chars]

        return {
            "content": content,
            "total_chars": total_chars,
            "truncated": truncated,
            "matches_found": len(matches),
            "files_searched": total_files_searched,
            "lines_searched": total_lines_searched,
            "pattern": pattern,
            "files": files,
        }

    async def __call__(
        self,
        pattern: str,
        files: List[str],
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Search for regex patterns in specified files.

        Args:
            pattern: Regex pattern to match against file content (required)
            files: List of file paths to search (required, cannot be empty)
            max_chars: Maximum characters to return in output (optional, default 2000)

        Returns:
            A dictionary containing the search results and metadata

        """
        try:
            result = self._search_regex(pattern, files, max_chars)
            return {
                "status": "success",
                "message": (
                    f"Regex search completed. Found {result['matches_found']} matches "
                    f"in {result['files_searched']} file(s)."
                ),
                **result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Regex search failed: {str(e)}",
                "error": str(e),
                "pattern": pattern,
                "files": files,
            }
