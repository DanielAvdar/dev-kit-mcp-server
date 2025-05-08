"""Example of using the ToolFactory to create MCP tools at runtime."""

import ast
import logging
import os
import time
from typing import Any, Dict, Optional

from fastmcp import Context, FastMCP

from ..analyzer import CodeAnalyzer
from ..tools.tool_factory import ToolFactory


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


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create the FastMCP server
mcp = FastMCP(
    name="ToolFactory Example",
    instructions="This example demonstrates how to use the ToolFactory to create MCP tools at runtime.",
)

# Create the ToolFactory with our MCP instance
tool_factory = ToolFactory(mcp)


# Define some pre and post hooks for our tools
def log_execution_time(result: Any, *args: Any, **kwargs: Any) -> None:
    """Log the execution time of a function (post-hook)."""
    execution_time = kwargs.get("_start_time")
    if execution_time:
        elapsed = time.time() - execution_time
        logger.info(f"Function executed in {elapsed:.4f} seconds")


def start_timer(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Start a timer for the function execution (pre-hook).

    Returns:
        Dictionary with start time information

    """
    return {"_start_time": time.time()}


def log_input_params(*args: Any, **kwargs: Any) -> None:
    """Log the input parameters of a function (pre-hook)."""
    logger.info(f"Function called with args: {args}, kwargs: {kwargs}")


# Define some analysis functions that we want to convert to tools
@tool_factory
def analyze_code_complexity(
    repo_root: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze Python code complexity.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)

    Returns:
        Analysis results including complexity metrics

    """
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

    ast_analysis = CodeAnalyzer.parse_ast(code)

    # Basic complexity metrics
    complexity = {
        "function_count": len(ast_analysis.get("functions", [])),
        "class_count": len(ast_analysis.get("classes", [])),
        "line_count": code.count("\n") + 1,
        "character_count": len(code),
        "complexity_score": len(ast_analysis.get("functions", [])) + 2 * len(ast_analysis.get("classes", [])),
    }

    return complexity


@tool_factory
def get_code_summary(
    repo_root: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None
) -> Dict[str, Any]:
    """Generate a summary of the Python code.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)

    Returns:
        Summary information about the code

    """
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

    ast_analysis = CodeAnalyzer.parse_ast(code)
    token_analysis = CodeAnalyzer.tokenize_code(code)

    summary = {
        "functions": [f["name"] for f in ast_analysis.get("functions", [])],
        "classes": [c["name"] for c in ast_analysis.get("classes", [])],
        "imports": [i["name"] for i in ast_analysis.get("imports", [])],
        "token_count": len(token_analysis),
        "line_count": code.count("\n") + 1,
    }

    return summary


@tool_factory
async def validate_code(
    repo_root: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None, ctx: Context = None
) -> Dict[str, Any]:
    """Validate Python code by attempting to parse it.

    Args:
        repo_root: Path to the root of the repository
        file_path: Path to the file or package to analyze, relative to repo_root
        code: Code string to analyze (if provided, repo_root and file_path are ignored)
        ctx: MCP context

    Returns:
        Validation results

    """
    try:
        # Handle case where code is passed as first positional argument
        if repo_root is not None and code is None and file_path is None and not isinstance(repo_root, Context):
            code = repo_root
            repo_root = None

        # Handle case where code and ctx are passed as positional arguments
        if repo_root is not None and isinstance(file_path, Context) and code is None:
            code = repo_root
            ctx = file_path
            repo_root = None
            file_path = None

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

        # Try to parse the code
        CodeAnalyzer.parse_ast(code)
        if ctx:
            await ctx.info("Code validation successful")
        return {"valid": True, "errors": None}
    except Exception as e:
        if ctx:
            await ctx.error(f"Code validation failed: {str(e)}")
        return {"valid": False, "errors": str(e)}


# Define class with methods to expose as tools
class CodeMetricsAnalyzer:
    """Analyzer for code metrics."""

    def count_statements(
        self, repo_root: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Count the number of statements in the Python code.

        Args:
            repo_root: Path to the root of the repository
            file_path: Path to the file or package to analyze, relative to repo_root
            code: Code string to analyze (if provided, repo_root and file_path are ignored)

        Returns:
            Count of different statement types

        """
        # Parse the AST
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

            tree = CodeAnalyzer.parse_raw_ast(code)

            # Count different types of statements
            statements = {"assignments": 0, "calls": 0, "conditionals": 0, "loops": 0, "returns": 0}

            # Simple visitor to count statement types
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    statements["assignments"] += 1
                elif isinstance(node, ast.Call):
                    statements["calls"] += 1
                elif isinstance(node, (ast.If, ast.IfExp)):
                    statements["conditionals"] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    statements["loops"] += 1
                elif isinstance(node, ast.Return):
                    statements["returns"] += 1

            return statements
        except Exception as e:
            return {"error": str(e)}

    def measure_complexity(
        self, repo_root: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Measure the cyclomatic complexity of the code.

        Args:
            repo_root: Path to the root of the repository
            file_path: Path to the file or package to analyze, relative to repo_root
            code: Code string to analyze (if provided, repo_root and file_path are ignored)

        Returns:
            Complexity metrics

        """
        # Basic implementation - could be expanded with actual cyclomatic complexity
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

            tree = CodeAnalyzer.parse_raw_ast(code)

            # Count branch points that increase complexity
            branches = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While, ast.Try)):
                    branches += 1

            return {
                "cyclomatic_complexity": 1 + branches,  # Base complexity of 1 plus branches
                "branch_points": branches,
            }
        except Exception as e:
            return {"error": str(e)}


# Initialize the main application
def init_application() -> None:
    """Initialize the application and register all tools."""
    # Add hooks to the tool factory
    tool_factory.add_pre_hook(start_timer)
    tool_factory.add_pre_hook(log_input_params)
    tool_factory.add_post_hook(log_execution_time)

    # Functions are already decorated with @tool_factory
    # No need to call create_tools()

    # Decorate all methods in the CodeMetricsAnalyzer class
    tool_factory(CodeMetricsAnalyzer)

    logger.info("All tools have been registered successfully")


# Start the server
def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the MCP server with the ToolFactory example.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    # Initialize the application
    init_application()

    # Start the server
    logger.info(f"Starting ToolFactory example server on {host}:{port}")
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    # If run directly, start the server
    start_server()
