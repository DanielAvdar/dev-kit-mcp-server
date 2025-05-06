"""Implementation logic for MCP tools."""

import ast
from typing import Any, Dict, Optional

from fastmcp import Context

from .analyzer import CodeAnalyzer


def get_server_info() -> Dict[str, Any]:
    """Get server information.

    Returns:
        Server information including name, version, and description

    """
    return {
        "name": "Python Code MCP Server",
        "version": "0.1.0",
        "description": "Model Context Protocol server for Python code analysis using AST and tokenize",
    }


def analyze_full(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Analyze Python code using AST and tokenize.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        Analysis results including AST and token information

    Raises:
        Exception: If there's an error analyzing the code

    """
    try:
        result = CodeAnalyzer.analyze(code)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error analyzing code: {str(e)}") from e


def analyze_ast(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Parse Python code and return AST analysis.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        AST analysis results

    Raises:
        Exception: If code is None or there's a syntax/parsing error

    """
    # First check for syntax errors
    if code is None:
        raise Exception("Error parsing AST: code cannot be None")

    try:
        # Try to parse the code to catch syntax errors early
        ast.parse(code)
    except SyntaxError as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e

    try:
        result = CodeAnalyzer.parse_ast(code)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e


def analyze_tokens(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Tokenize Python code.

    Args:
        code: Python code string to tokenize
        path: Optional file path for the code

    Returns:
        Tokenization results

    Raises:
        Exception: If code is None or there's an error tokenizing the code

    """
    # First check for None values to match test expectations
    if code is None:
        raise Exception("Error tokenizing code: code cannot be None")

    try:
        tokens = CodeAnalyzer.tokenize_code(code)
        # Limit token output
        return {"result": {"tokens": tokens[:100]}}
    except Exception as e:
        raise Exception(f"Error tokenizing code: {str(e)}") from e


def count_elements(code: str, path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """Count elements in Python code (functions, classes, imports).

    Args:
        code: Python code string to analyze
        path: Optional file path for the code
        ctx: Optional MCP context

    Returns:
        Count of code elements

    Raises:
        Exception: If there's an error counting elements in the code

    """
    try:
        if ctx:
            ctx.info(f"Counting elements in code with {len(code)} characters")

        ast_analysis = CodeAnalyzer.parse_ast(code)
        result = {
            "function_count": len(ast_analysis.get("functions", [])),
            "class_count": len(ast_analysis.get("classes", [])),
            "import_count": len(ast_analysis.get("imports", [])),
            "variable_count": len(ast_analysis.get("variables", [])),
        }
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error counting elements: {str(e)}") from e
