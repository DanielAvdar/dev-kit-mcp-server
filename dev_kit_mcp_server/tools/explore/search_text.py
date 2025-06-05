"""Module for searching text content in files."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import git

from ...core import AsyncOperation


@dataclass
class SearchTextOperation(AsyncOperation):
    """Class to search for lines in files matching a given pattern."""

    name = "search_text"

    def _search_text(
        self,
        pattern: str,
        files: Optional[List[str]] = None,
        context: Optional[int] = None,
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Search for lines in files matching a regex pattern.

        Args:
            pattern: Regex pattern to match against file content
            files: List of file paths to search (optional, searches all text files if None)
            context: Number of context lines to include before/after matches (optional)
            max_chars: Maximum characters to return in output

        Returns:
            Dictionary with search results

        Raises:
            ValueError: If pattern is invalid regex or file paths are invalid

        """
        # Validate regex pattern
        try:
            compiled_pattern = re.compile(pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {pattern}. Error: {e}") from e

        # Determine files to search
        search_files: List[Path] = []
        if files is None:
            # Search all files except those ignored by .gitignore
            try:
                repo = git.Repo(self._root_path)
                for file_path in self._root_path.rglob("*"):
                    if file_path.is_file():
                        # Get relative path for gitignore check
                        try:
                            relative_path = file_path.relative_to(self._root_path)
                            # Check if file is ignored by gitignore
                            if not repo.ignored(str(relative_path)):
                                search_files.append(file_path)
                        except ValueError:
                            # File is outside root directory, skip it
                            continue
            except (git.InvalidGitRepositoryError, OSError, PermissionError):
                # If not a git repo or git error, fall back to all files except hidden
                for file_path in self._root_path.rglob("*"):
                    if file_path.is_file() and not any(
                        part.startswith(".") for part in file_path.parts[len(self._root_path.parts) :]
                    ):
                        search_files.append(file_path)
        else:
            # Validate and collect specified files
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

                        # Add context lines if requested
                        if context is not None and context > 0:
                            start_line = max(0, line_num - 1 - context)
                            end_line = min(len(lines), line_num + context)

                            context_lines = []
                            for i in range(start_line, end_line):
                                context_lines.append({
                                    "line_number": i + 1,
                                    "line": lines[i].rstrip("\n\r"),
                                    "is_match": i == line_num - 1,
                                })
                            match_data["context"] = context_lines

                        matches.append(match_data)

            except (UnicodeDecodeError, OSError, PermissionError):
                # Skip binary files or files with access issues
                continue

        # Prepare output
        content_lines = [f"Text search results for pattern '{pattern}':", ""]

        if not matches:
            content_lines.append("No matches found")
        else:
            for match in matches:
                if context is not None and "context" in match:
                    content_lines.append(f"=== {match['file']} ===")
                    for ctx in match["context"]:
                        prefix = ">>> " if ctx["is_match"] else "    "
                        content_lines.append(f"{prefix}{ctx['line_number']:4d}:")
                    content_lines.append("")
                else:
                    # Simple format: file_path:line_number:
                    content_lines.append(f"{match['file']}:{match['line_number']}:")

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
            "context": context,
        }

    async def __call__(
        self,
        pattern: str,
        files: Optional[List[str]] = None,
        context: Optional[int] = None,
        max_chars: int = 2000,
    ) -> Dict[str, Any]:
        """Search for lines in files matching a given pattern.

        Args:
            pattern: Regex pattern to match against file content (required)
            files: List of file paths to search (optional, searches all text files if None)
            context: Number of context lines to include before/after matches (optional)
            max_chars: Maximum characters to return in output (optional, default 2000)

        Returns:
            A dictionary containing the search results and metadata

        """
        try:
            result = self._search_text(pattern, files, context, max_chars)
            return {
                "status": "success",
                "message": (
                    f"Text search completed. Found {result['matches_found']} matches "
                    f"in {result['files_searched']} files."
                ),
                **result,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Text search failed: {str(e)}",
                "error": str(e),
                "pattern": pattern,
                "files": files,
                "context": context,
            }
