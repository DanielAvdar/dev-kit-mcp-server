"""Tool for reading the contents of a file."""

import os
from typing import Any, Dict, Optional

from fastmcp import Context

from ..utils.file_utils import normalize_path


def read_file(
    file_path: str,
    start_line_number_base_zero: int = 0,
    end_line_number_base_zero: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Read the contents of a file.

    Args:
        file_path: The path to the file to read
        start_line_number_base_zero: The line number to start reading from (0-based)
        end_line_number_base_zero: The line number to end reading at (0-based)
        ctx: Optional MCP context

    Returns:
        Dictionary containing file contents

    """
    if ctx:
        ctx.info(
            f"Reading file: {file_path} from line {start_line_number_base_zero} "
            + f"to line {end_line_number_base_zero if end_line_number_base_zero is not None else 'end'}"
        )

    # Normalize path and handle both absolute and relative paths
    if not os.path.isabs(file_path):
        workspace_root = os.getcwd()
        file_path = os.path.join(workspace_root, file_path)

    file_path = normalize_path(file_path)

    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}", "file_path": file_path}

    if not os.path.isfile(file_path):
        return {"error": f"Not a file: {file_path}", "file_path": file_path}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()

        file_stats = os.stat(file_path)

        # Adjust end line if not specified
        if end_line_number_base_zero is None:
            end_line_number_base_zero = len(all_lines) - 1

        # Ensure indices are within bounds
        start_line_number_base_zero = max(0, min(start_line_number_base_zero, len(all_lines) - 1))
        end_line_number_base_zero = max(start_line_number_base_zero, min(end_line_number_base_zero, len(all_lines) - 1))

        # Get the requested lines
        lines = all_lines[start_line_number_base_zero : end_line_number_base_zero + 1]
        content = "".join(lines)

        # Generate file outline
        outline = []
        if len(all_lines) > (end_line_number_base_zero - start_line_number_base_zero + 1):
            # Only generate outline if we're not reading the entire file
            line_count = len(all_lines)
            if line_count <= 100:
                # For small files, show all line numbers
                outline = [f"Line {i + 1}" for i in range(line_count)]
            else:
                # For larger files, show structure with line ranges
                step = line_count // 10
                for i in range(0, line_count, step):
                    outline.append(f"Lines {i + 1}-{min(i + step, line_count)}")

        return {
            "file_path": file_path,
            "content": content,
            "start_line": start_line_number_base_zero + 1,  # Convert to 1-based for display
            "end_line": end_line_number_base_zero + 1,  # Convert to 1-based for display
            "total_lines": len(all_lines),
            "size_bytes": file_stats.st_size,
            "outline": outline if outline else None,
        }
    except UnicodeDecodeError:
        # Try with a different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                all_lines = f.readlines()

            # Same logic as above
            if end_line_number_base_zero is None:
                end_line_number_base_zero = len(all_lines) - 1

            start_line_number_base_zero = max(0, min(start_line_number_base_zero, len(all_lines) - 1))
            end_line_number_base_zero = max(
                start_line_number_base_zero, min(end_line_number_base_zero, len(all_lines) - 1)
            )

            lines = all_lines[start_line_number_base_zero : end_line_number_base_zero + 1]
            content = "".join(lines)

            return {
                "file_path": file_path,
                "content": content,
                "start_line": start_line_number_base_zero + 1,
                "end_line": end_line_number_base_zero + 1,
                "total_lines": len(all_lines),
                "size_bytes": os.stat(file_path).st_size,
                "encoding": "latin-1",  # Note the different encoding
            }
        except Exception as e:
            return {"error": f"Failed to read file with alternative encoding: {str(e)}", "file_path": file_path}
    except Exception as e:
        return {"error": f"Error reading file: {str(e)}", "file_path": file_path}
