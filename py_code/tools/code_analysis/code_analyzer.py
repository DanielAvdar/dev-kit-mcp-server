"""Code analysis tools for processing files and directories."""

import os
from typing import Any, Dict, Optional

from fastmcp import Context

from .analyzer import CodeAnalyzer
from .code_traversal import find_python_files, parse_gitignore, resolve_path_pattern


def parse_ast_files(
    pattern: str, root_dir: Optional[str] = None, ignore_gitignore: bool = False, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Parse Python files matching the pattern and return AST analysis.

    Args:
        pattern: Pattern to match files or directories
        root_dir: Root directory of codebase (defaults to current working directory)
        ignore_gitignore: Whether to ignore .gitignore file
        ctx: Optional MCP context

    Returns:
        Dictionary containing AST analysis for each file

    """
    # Set default root directory if not provided
    if root_dir is None:
        root_dir = os.getcwd()

    if ctx:
        ctx.info(f"Parsing AST for files matching pattern: {pattern}")

    # Parse .gitignore if needed
    ignore_patterns = []
    if not ignore_gitignore:
        gitignore_path = os.path.join(root_dir, ".gitignore")
        ignore_patterns = parse_gitignore(gitignore_path)
        if ctx and ignore_patterns:
            ctx.info(f"Found {len(ignore_patterns)} ignore patterns in .gitignore")

    # Resolve the pattern to actual paths
    paths = resolve_path_pattern(pattern, root_dir)
    if not paths:
        return {"error": f"No files found matching pattern: {pattern}", "pattern": pattern, "root_dir": root_dir}

    # Find all Python files in the paths
    python_files = []
    for path in paths:
        python_files.extend(find_python_files(path, root_dir, ignore_patterns))

    if not python_files:
        return {"error": f"No Python files found matching pattern: {pattern}", "pattern": pattern, "root_dir": root_dir}

    # Sort files for consistent output
    python_files.sort()

    # Limit the number of files for performance
    max_files = 100
    if len(python_files) > max_files:
        if ctx:
            ctx.warning(f"Too many files found ({len(python_files)}), limiting to {max_files}")
        python_files = python_files[:max_files]

    # Parse each file
    results = {}
    errors = []

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Process the file with the analyzer
            ast_result = CodeAnalyzer.parse_ast(code)

            # Add to results with relative path as key
            rel_path = os.path.relpath(file_path, root_dir)
            results[rel_path] = ast_result

        except Exception as e:
            rel_path = os.path.relpath(file_path, root_dir)
            error_msg = f"Error parsing {rel_path}: {str(e)}"
            errors.append(error_msg)
            if ctx:
                ctx.warning(error_msg)

    # Build the final result
    summary = {
        "total_files": len(results),
        "total_functions": sum(len(result.get("functions", [])) for result in results.values()),
        "total_classes": sum(len(result.get("classes", [])) for result in results.values()),
        "total_imports": sum(len(result.get("imports", [])) for result in results.values()),
        "total_variables": sum(len(result.get("variables", [])) for result in results.values()),
    }

    return {
        "pattern": pattern,
        "root_dir": root_dir,
        "file_count": len(results),
        "files": results,
        "summary": summary,
        "errors": errors,
    }


def analyze_code_files(
    pattern: str,
    root_dir: Optional[str] = None,
    ignore_gitignore: bool = False,
    include_tokens: bool = True,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Analyze Python files matching the pattern using AST and tokenize modules.

    Args:
        pattern: Pattern to match files or directories
        root_dir: Root directory of codebase (defaults to current working directory)
        ignore_gitignore: Whether to ignore .gitignore file
        include_tokens: Whether to include token analysis in the results
        ctx: Optional MCP context

    Returns:
        Dictionary containing full analysis for each file

    """
    # Set default root directory if not provided
    if root_dir is None:
        root_dir = os.getcwd()

    if ctx:
        ctx.info(f"Analyzing code for files matching pattern: {pattern}")

    # Parse .gitignore if needed
    ignore_patterns = []
    if not ignore_gitignore:
        gitignore_path = os.path.join(root_dir, ".gitignore")
        ignore_patterns = parse_gitignore(gitignore_path)
        if ctx and ignore_patterns:
            ctx.info(f"Found {len(ignore_patterns)} ignore patterns in .gitignore")

    # Resolve the pattern to actual paths
    paths = resolve_path_pattern(pattern, root_dir)
    if not paths:
        return {"error": f"No files found matching pattern: {pattern}", "pattern": pattern, "root_dir": root_dir}

    # Find all Python files in the paths
    python_files = []
    for path in paths:
        python_files.extend(find_python_files(path, root_dir, ignore_patterns))

    if not python_files:
        return {"error": f"No Python files found matching pattern: {pattern}", "pattern": pattern, "root_dir": root_dir}

    # Sort files for consistent output
    python_files.sort()

    # Limit the number of files for performance
    max_files = 50  # Lower than parse_ast because this is more intensive
    if len(python_files) > max_files:
        if ctx:
            ctx.warning(f"Too many files found ({len(python_files)}), limiting to {max_files}")
        python_files = python_files[:max_files]

    # Analyze each file
    results = {}
    errors = []

    for file_path in python_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            # Process the file with the analyzer
            if include_tokens:
                analysis_result = CodeAnalyzer.analyze(code)
            else:
                ast_result = CodeAnalyzer.parse_ast(code)
                analysis_result = {"ast_analysis": ast_result}

            # Add to results with relative path as key
            rel_path = os.path.relpath(file_path, root_dir)
            results[rel_path] = analysis_result

        except Exception as e:
            rel_path = os.path.relpath(file_path, root_dir)
            error_msg = f"Error analyzing {rel_path}: {str(e)}"
            errors.append(error_msg)
            if ctx:
                ctx.warning(error_msg)

    # Build the final result
    summary = {
        "total_files": len(results),
        "total_functions": sum(len(result.get("ast_analysis", {}).get("functions", [])) for result in results.values()),
        "total_classes": sum(len(result.get("ast_analysis", {}).get("classes", [])) for result in results.values()),
        "total_imports": sum(len(result.get("ast_analysis", {}).get("imports", [])) for result in results.values()),
        "total_variables": sum(len(result.get("ast_analysis", {}).get("variables", [])) for result in results.values()),
    }

    return {
        "pattern": pattern,
        "root_dir": root_dir,
        "file_count": len(results),
        "files": results,
        "summary": summary,
        "errors": errors,
    }
