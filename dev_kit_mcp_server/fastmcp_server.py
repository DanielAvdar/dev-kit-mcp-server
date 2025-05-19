"""MCP Server implementation using FastMCP."""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# from mcp.server.fastmcp import FastMCP  # type: ignore
# from fastmcp import FastMCP
from .tool_factory import RepoFastMCPServerError as FastMCP, ToolFactory
from .tools import (
    CreateDirOperation,
    GitAddOperation,
    GitCheckoutOperation,
    GitCommitOperation,
    GitPullOperation,
    GitPushOperation,
    GitStatusOperation,
    MoveDirOperation,
    RemoveFileOperation,
    RenameOperation,
)
from .tools.commands_tool import ExecMakeTarget


def start_server(root_dir: str = None) -> FastMCP:
    """Start the FastMCP server.

    Args:
        root_dir: Root directory for file operations (default: current working directory)

    Returns:
        A FastMCP instance configured with file operation tools

    """
    # Parse command line arguments
    root_dir = root_dir or method_name()

    # Create a FastMCP instance
    fastmcp: FastMCP = FastMCP(
        name="Dev-Kit MCP Server",
        instructions="This server provides tools for file operations"
        f" and running authorized makefile commands in root directory: {root_dir}",
    )

    # Create a list of tools to register
    tools = [
        # File system operations
        MoveDirOperation(root_dir=root_dir),
        CreateDirOperation(root_dir=root_dir),
        RemoveFileOperation(root_dir=root_dir),
        RenameOperation(root_dir=root_dir),
        # Git operations
        GitStatusOperation(root_dir=root_dir),
        GitCommitOperation(root_dir=root_dir),
        GitPushOperation(root_dir=root_dir),
        GitPullOperation(root_dir=root_dir),
        GitAddOperation(root_dir=root_dir),
        GitCheckoutOperation(root_dir=root_dir),
        # Make operations
        ExecMakeTarget(root_dir=root_dir),
    ]

    # Check if GitHub tools should be registered
    try:
        # Import GitHub operations only if PyGithub is available
        from .tools import GITHUB_AVAILABLE

        if GITHUB_AVAILABLE:
            # Import GitHub operations
            from .tools.github.repo import GitHubRepoOperation

            # Create a temporary operation to check for GitHub remote
            temp_op = GitHubRepoOperation(root_dir=root_dir, token=None)
            repo_info = temp_op.get_repo_info()

            # Only register GitHub tools if a GitHub remote is available
            if repo_info:
                from .tools.github.issue import GitHubIssueOperation
                from .tools.github.pr import GitHubPROperation

                # Add GitHub tools to the list
                tools.extend([
                    GitHubRepoOperation(root_dir=root_dir, token=None),
                    GitHubIssueOperation(root_dir=root_dir, token=None),
                    GitHubPROperation(root_dir=root_dir, token=None),
                ])
    except Exception:
        # If there's any error, skip GitHub tools
        pass

    # Register all tools
    tool_factory = ToolFactory(fastmcp)
    tool_factory(tools)
    return fastmcp


def method_name() -> str:
    """Parse command line arguments and validate the root directory.

    Returns:
        The validated root directory path as a string

    Raises:
        ValueError: If the root directory does not exist or is not a directory

    """
    parser = argparse.ArgumentParser(description="Start the FastMCP server")
    parser.add_argument(
        "--root-dir",
        type=str,
        default=os.getcwd(),
        help="Root directory for file operations (default: current working directory)",
    )
    args = parser.parse_args()
    # Validate root directory
    root_dir = args.root_dir
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"Root directory does not exist: {root_dir}")
    if not root_path.is_dir():
        raise ValueError(f"Root directory is not a directory: {root_dir}")
    return root_dir


def run_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server.

    Args:
        fastmcp: Optional FastMCP instance to run. If None, a new instance will be created.

    """
    fastmcp = fastmcp or start_server()
    try:
        fastmcp.run()
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)


def arun_server(fastmcp: FastMCP = None) -> None:
    """Run the FastMCP server asynchronously.

    Args:
        fastmcp: Optional FastMCP instance to run. If None, a new instance will be created.

    """
    fastmcp = fastmcp or start_server()
    try:
        asyncio.run(fastmcp.run_async())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
