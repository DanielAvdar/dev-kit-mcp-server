"""Common utilities for search and navigation tools."""

import os
from typing import List

def normalize_path(path: str) -> str:
    """Normalize a file path for consistent handling."""
    return os.path.normpath(path)

def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary (non-text)."""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except:
        return True

def filter_binary_files(file_paths: List[str]) -> List[str]:
    """Filter out binary files from a list of file paths."""
    return [path for path in file_paths if not is_binary_file(path)]

def get_file_contents(file_path: str) -> str:
    """Get the contents of a file as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try with a different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            return f"Error: Could not read file {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_lines_from_file(file_path: str, start_line: int = 0, end_line: int = None) -> str:
    """Get specific lines from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if end_line is None:
            end_line = len(lines)
            
        return ''.join(lines[start_line:end_line])
    except Exception as e:
        return f"Error: {str(e)}"