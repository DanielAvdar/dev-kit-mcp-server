"""Module for creating and starting the FastMCP server with file operation tools."""

import argparse
import os
from pathlib import Path

from dev_kit_mcp_server.custom_fastmcp import RepoFastMCPServerError as FastMCP
from dev_kit_mcp_server.tool_factory import ToolFactory


def start_server(root_dir: str = None, copilot_mode: bool = False, commands_toml: str = None) -> FastMCP:
    """Start the FastMCP server.

    Args:
        root_dir: Root directory for file operations (default: current working directory)
        copilot_mode: Run in copilot mode with limited tools (default: False)
        commands_toml: Path to a custom TOML file for predefined commands (default: None)

    Returns:
        A FastMCP instance configured with file operation tools

    """
    # Parse command line arguments
    args = arg_parse()
    root_dir = root_dir or args.root_dir
    copilot_mode = copilot_mode or args.copilot_mode
    commands_toml = commands_toml or args.commands_toml

    fastmcp = server_init(root_dir, commands_toml)
    return fastmcp


def server_init(root_dir: str, commands_toml: str = None) -> FastMCP:
    """Initialize the FastMCP server with the specified configuration.

    Args:
        root_dir: Root directory for file operations
        copilot_mode: Whether to run in copilot mode with limited tools
        commands_toml: Path to a custom TOML file for predefined commands (default: None)

    Returns:
        A configured FastMCP instance ready to be run

    """
    # Create a FastMCP instance
    fastmcp: FastMCP = FastMCP(
        name="Dev-Kit MCP Server",
        instructions="This server provides tools for file operations"
        f" and running authorized makefile commands in root directory: {root_dir}",
    )
    # Register all tools
    tool_factory = ToolFactory(fastmcp)
    tool_factory(["dev_kit_mcp_server.tools"], root_dir=root_dir, commands_toml=commands_toml)
    return fastmcp


def arg_parse() -> argparse.Namespace:
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
    parser.add_argument(
        "--copilot-mode",
        action="store_true",
        default=False,
        help="Run in copilot mode with limited tools (default: False)",
    )
    parser.add_argument(
        "--commands-toml",
        type=str,
        default=None,
        help="Path to a custom TOML file for predefined commands (default: None)",
    )
    args = parser.parse_args()
    # Validate root directory
    root_dir = args.root_dir
    root_path = Path(root_dir)
    if not root_path.exists():
        raise ValueError(f"Root directory does not exist: {root_dir}")
    if not root_path.is_dir():
        raise ValueError(f"Root directory is not a directory: {root_dir}")

    return args
