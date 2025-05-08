"""File content utility functions for MCP tools."""

from typing import Optional


def get_file_contents(file_path: str) -> str:
    """Get the contents of a file as a string.

    Args:
        file_path: Path to the file to read

    Returns:
        The contents of the file as a string or an error message

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try with a different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            return f"Error: Could not read file {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


def get_lines_from_file(file_path: str, start_line: int = 0, end_line: Optional[int] = None) -> str:
    """Get specific lines from a file.

    Args:
        file_path: Path to the file to read
        start_line: Line number to start reading from (0-based)
        end_line: Line number to end reading at (0-based, inclusive)

    Returns:
        The requested lines from the file as a single string or an error message

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if end_line is None:
            end_line = len(lines)

        return "".join(lines[start_line:end_line])
    except Exception as e:
        return f"Error: {str(e)}"
