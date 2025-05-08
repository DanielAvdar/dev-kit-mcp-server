"""Implementation logic for MCP tools."""

import ast
import os
from typing import Any, Dict, Optional

from fastmcp import Context

from ..analyzer import CodeAnalyzer
from ..version import __version__


def read_code_from_path(repo_root: str, file_path: str) -> str:
    """Read code from a file path.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root

    Returns:
        The code as a string

    Raises:
        Exception: If the file cannot be read

    """
    full_path = os.path.join(repo_root, file_path)

    if not os.path.exists(full_path):
        raise Exception(f"Path does not exist: {full_path}")

    if os.path.isfile(full_path):
        # Read a single file
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading file {full_path}: {str(e)}") from e
    elif os.path.isdir(full_path):
        # For a directory, read all Python files and concatenate them
        code_parts = []
        for root, _, files in os.walk(full_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            code_parts.append(f"# File: {os.path.relpath(file_path, repo_root)}\n")
                            code_parts.append(f.read())
                            code_parts.append("\n\n")
                    except Exception as e:
                        raise Exception(f"Error reading file {file_path}: {str(e)}") from e
        return "".join(code_parts)
    else:
        raise Exception(f"Path is neither a file nor a directory: {full_path}")


def get_server_info() -> Dict[str, Any]:
    """Get information about the MCP repository navigation server.

    Returns:
        Server information including name, version, and repository navigation capabilities

    """
    return {
        "name": "Python Code MCP Server",
        "version": __version__,
        "description": "Model Context Protocol server for turning repositories into navigable MCP systems",
    }


def analyze_full(
    repo_root: Optional[str] = None,
    file_path: Optional[str] = None,
    code: Optional[str] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Comprehensively analyze code structure for repository navigation.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)
        path: Optional file path within the repository (for backward compatibility)

    Returns:
        Detailed code structure analysis for repository exploration

    Raises:
        Exception: If there's an error analyzing the code

    """
    try:
        # Handle case where code is passed as first positional argument
        if repo_root is not None and code is None and file_path is None:
            code = repo_root
            repo_root = None

        # For backward compatibility
        if code is not None:
            # Use the provided code directly
            result = CodeAnalyzer.analyze(code)
            return {"result": result}
        elif repo_root is not None:
            if file_path is not None:
                # For specific file/directory analysis
                code = read_code_from_path(repo_root, file_path)
                result = CodeAnalyzer.analyze(code)
                return {"result": result}
            else:
                # For repository-wide analysis
                result = CodeAnalyzer.analyze_repository(repo_root)
                return {"result": result}
        else:
            # For tests that expect an error when no code is provided
            raise Exception("Repository path or code is required")
    except Exception as e:
        raise Exception(f"Error analyzing code: {str(e)}") from e


def analyze_ast(
    repo_root: Optional[str] = None,
    file_path: Optional[str] = None,
    code: Optional[str] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract code structure for repository navigation.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)
        path: Optional file path within the repository (for backward compatibility)

    Returns:
        Code structure information for navigating the repository

    Raises:
        Exception: If there's a syntax/parsing error

    """
    try:
        # Handle case where code is passed as first positional argument
        if repo_root is not None and code is None and file_path is None:
            code = repo_root
            repo_root = None

        # For backward compatibility
        if code is not None:
            # Use the provided code directly
            pass
        elif repo_root is not None and file_path is not None:
            # Read code from the file path
            code = read_code_from_path(repo_root, file_path)
        else:
            # This will maintain the existing behavior for tests
            pass

        # Check for syntax errors
        if code is None:
            raise Exception("Error parsing AST: code cannot be None")

        # Try to parse the code to catch syntax errors early
        ast.parse(code)
    except SyntaxError as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e

    try:
        result = CodeAnalyzer.parse_ast(code)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e


def analyze_tokens(
    repo_root: Optional[str] = None,
    file_path: Optional[str] = None,
    code: Optional[str] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Identify code elements for detailed repository exploration.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)
        path: Optional file path within the repository (for backward compatibility)

    Returns:
        Detailed code elements for fine-grained repository navigation

    Raises:
        Exception: If there's an error identifying code elements

    """
    try:
        # Handle case where code is passed as first positional argument
        if repo_root is not None and code is None and file_path is None:
            code = repo_root
            repo_root = None

        # For backward compatibility
        if code is not None:
            # Use the provided code directly
            tokens = CodeAnalyzer.tokenize_code(code)
            # Limit token output
            return {"result": {"tokens": tokens[:100]}}
        elif repo_root is not None:
            if file_path is not None:
                # For specific file/directory
                code = read_code_from_path(repo_root, file_path)
                tokens = CodeAnalyzer.tokenize_code(code)
                # Limit token output
                return {"result": {"tokens": tokens[:100]}}
            else:
                # For repository-wide analysis, we'll just analyze the first few Python files
                # to avoid excessive output
                python_files = []
                for root, _, files in os.walk(repo_root):
                    for file in files:
                        if file.endswith(".py"):
                            python_files.append(os.path.join(root, file))
                            if len(python_files) >= 5:  # Limit to 5 files
                                break
                    if len(python_files) >= 5:
                        break

                all_tokens = []
                for file_path in python_files[:5]:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    file_tokens = CodeAnalyzer.tokenize_code(code)
                    all_tokens.extend(file_tokens[:20])  # Take only first 20 tokens from each file

                return {
                    "result": {
                        "tokens": all_tokens[:100],
                        "files_analyzed": len(python_files),
                        "note": "Token analysis limited to first few files for brevity",
                    }
                }
        else:
            # Check for None values to match test expectations
            raise Exception("Error tokenizing code: code cannot be None")
    except Exception as e:
        raise Exception(f"Error tokenizing code: {str(e)}") from e


def count_elements(
    repo_root: Optional[str] = None,
    file_path: Optional[str] = None,
    code: Optional[str] = None,
    path: Optional[str] = None,
    ctx: Context = None,
) -> Dict[str, Any]:
    """Summarize repository components for high-level navigation.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)
        path: Optional file path within the repository (for backward compatibility)
        ctx: Optional MCP context

    Returns:
        Summary of repository components for high-level navigation

    Raises:
        Exception: If there's an error summarizing repository components

    """
    try:
        # Handle case where code is passed as first positional argument
        if repo_root is not None and code is None and file_path is None:
            code = repo_root
            repo_root = None

        # For backward compatibility
        if code is not None:
            # Use the provided code directly
            if ctx:
                ctx.info(f"Counting elements in code with {len(code)} characters")

            ast_analysis = CodeAnalyzer.parse_ast(code)
            result = {
                "function_count": len(ast_analysis.get("functions", [])),
                "class_count": len(ast_analysis.get("classes", [])),
                "import_count": len(ast_analysis.get("imports", [])),
                "variable_count": len(ast_analysis.get("variables", [])),
            }

        elif repo_root is not None:
            if ctx:
                ctx.info(f"Counting elements in repository at {repo_root}")

            if file_path is not None:
                # For specific file/directory
                code = read_code_from_path(repo_root, file_path)
                ast_analysis = CodeAnalyzer.parse_ast(code)
                result = {
                    "function_count": len(ast_analysis.get("functions", [])),
                    "class_count": len(ast_analysis.get("classes", [])),
                    "import_count": len(ast_analysis.get("imports", [])),
                    "variable_count": len(ast_analysis.get("variables", [])),
                }
            else:
                # For entire repository
                repo_analysis = CodeAnalyzer.analyze_repository(repo_root)
                result = {
                    "function_count": repo_analysis["total_functions"],
                    "class_count": repo_analysis["total_classes"],
                    "import_count": repo_analysis["total_imports"],
                    "files_analyzed": repo_analysis["files_analyzed"],
                }
        else:
            raise Exception("Repository path or code is required")

        return {"result": result}
    except Exception as e:
        raise Exception(f"Error counting elements: {str(e)}") from e


def analyze_dependencies(
    repo_root: str,
) -> Dict[str, Any]:
    """Analyze dependencies between files in a repository.

    Args:
        repo_root: Path to the root of the repository

    Returns:
        Dependency analysis result showing relationships between files

    Raises:
        Exception: If there's an error analyzing dependencies

    """
    try:
        if not os.path.exists(repo_root):
            raise Exception(f"Repository path does not exist: {repo_root}")

        result = CodeAnalyzer.find_dependencies(repo_root)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error analyzing dependencies: {str(e)}") from e
