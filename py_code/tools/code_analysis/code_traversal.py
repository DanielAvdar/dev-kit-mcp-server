"""Utilities for code traversal and analysis."""

import fnmatch
import os
from typing import List


def parse_gitignore(gitignore_path: str) -> List[str]:
    """Parse .gitignore file and return patterns to ignore.

    Args:
        gitignore_path: Path to .gitignore file

    Returns:
        List of patterns to ignore

    """
    if not os.path.exists(gitignore_path):
        return []

    try:
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Process .gitignore patterns
        patterns = []
        for line in lines:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Handle negation (!)
            if line.startswith("!"):
                # Not implementing negation for simplicity
                continue
            # Handle directory-specific pattern
            if line.startswith("/"):
                line = line[1:]  # Remove leading slash
            # Normalize pattern
            patterns.append(line)

        return patterns
    except Exception:
        return []


def is_ignored(file_path: str, root_dir: str, ignore_patterns: List[str]) -> bool:
    """Check if a file should be ignored based on patterns.

    Args:
        file_path: Absolute path to file
        root_dir: Root directory of codebase
        ignore_patterns: List of patterns to ignore

    Returns:
        True if file should be ignored, False otherwise

    """
    # Get relative path for gitignore pattern matching
    rel_path = os.path.relpath(file_path, root_dir)

    # Always ignore these directories
    if any(
        part.startswith(".") or part == "__pycache__" or part == "venv" or part == ".venv"
        for part in rel_path.split(os.sep)
    ):
        return True

    # Check against gitignore patterns
    for pattern in ignore_patterns:
        # Handle directory-only pattern (ending with /)
        if pattern.endswith("/"):
            pattern = pattern[:-1]
            # Only check directories
            if os.path.isdir(file_path) and fnmatch.fnmatch(rel_path, pattern):
                return True
        # Regular pattern
        elif fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
            return True

    return False


def find_python_files(path: str, root_dir: str, ignore_patterns: List[str]) -> List[str]:
    """Find all Python files in the given path, respecting ignore patterns.

    Args:
        path: Path to file or directory
        root_dir: Root directory of codebase
        ignore_patterns: List of patterns to ignore

    Returns:
        List of Python file paths

    """
    python_files = []

    if os.path.isfile(path):
        if path.endswith(".py") and not is_ignored(path, root_dir, ignore_patterns):
            python_files.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), root_dir, ignore_patterns)]

            # Collect Python files
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    if not is_ignored(file_path, root_dir, ignore_patterns):
                        python_files.append(file_path)

    return python_files


def resolve_path_pattern(pattern: str, root_dir: str) -> List[str]:
    """Resolve a path pattern to actual files or directories.

    Args:
        pattern: Path pattern (can include glob patterns)
        root_dir: Root directory of codebase

    Returns:
        List of absolute paths matching the pattern

    """
    # Handle absolute path
    if os.path.isabs(pattern):
        if os.path.exists(pattern):
            return [pattern]
        # Try as glob pattern
        import glob

        return glob.glob(pattern)

    # Handle relative path
    abs_pattern = os.path.join(root_dir, pattern)
    if os.path.exists(abs_pattern):
        return [abs_pattern]

    # Try as glob pattern
    import glob

    return glob.glob(abs_pattern)
