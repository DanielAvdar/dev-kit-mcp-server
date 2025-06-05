# Dev-Kit MCP Server

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dev-kit-mcp-server)](https://pypi.org/project/dev-kit-mcp-server/)
[![version](https://img.shields.io/pypi/v/dev-kit-mcp-server)](https://img.shields.io/pypi/v/dev-kit-mcp-server)
[![License](https://img.shields.io/:license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![OS](https://img.shields.io/badge/ubuntu-blue?logo=ubuntu)
![OS](https://img.shields.io/badge/win-blue?logo=windows)
![OS](https://img.shields.io/badge/mac-blue?logo=apple)
[![Tests](https://github.com/DanielAvdar/dev-kit-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/DanielAvdar/dev-kit-mcp-server/actions/workflows/ci.yml)
[![Code Checks](https://github.com/DanielAvdar/dev-kit-mcp-server/actions/workflows/code-checks.yml/badge.svg)](https://github.com/DanielAvdar/dev-kit-mcp-server/actions/workflows/code-checks.yml)
[![codecov](https://codecov.io/gh/DanielAvdar/dev-kit-mcp-server/graph/badge.svg?token=N0V9KANTG2)](https://codecov.io/gh/DanielAvdar/dev-kit-mcp-server)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Last Commit](https://img.shields.io/github/last-commit/DanielAvdar/dev-kit-mcp-server/main)

A Model Context Protocol (MCP) server targeted for agent development tools, providing scoped authorized operations in the root project directory. This package enables secure execution of operations such as running makefile commands, moving and deleting files, with future plans to include more tools for code editing. It serves as an excellent MCP server for VS-Code copilot and other AI-assisted development tools.

<a href="https://glama.ai/mcp/servers/@DanielAvdar/dev-kit-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@DanielAvdar/dev-kit-mcp-server/badge" alt="dev-kit-mcp-server MCP server" />
</a>

## Features

- 🔒 **Secure Operations**: Execute operations within a scoped, authorized root directory
- 🛠️ **Makefile Command Execution**: Run makefile commands securely within the project
- 📁 **File Operations**: Move, Create, Rename and Delete files within the authorized directory
- 🔄 **Git Operations**: Perform Git operations like status, add, commit, push, pull, and checkout
- 🔌 **MCP Integration**: Turn any codebase into an MCP-compliant system
- 🤖 **AI-Assisted Development**: Excellent integration with VS-Code copilot and other AI tools
- 🔄 **Extensible Framework**: Easily add new tools for code editing and other operations
- 🚀 **Fast Performance**: Built with FastMCP for high performance

## Installation

```bash
pip install dev-kit-mcp-server
```

## Usage

### Running the Server

```bash
# Recommended method (with root directory specified)
dev-kit-mcp-server --root-dir=workdir

# With custom TOML file for predefined commands
dev-kit-mcp-server --root-dir=workdir --commands-toml=custom_commands.toml

# Alternative methods
uv run python -m dev_kit_mcp_server.mcp_server --root-dir=workdir
python -m dev_kit_mcp_server.mcp_server --root-dir=workdir
```

The `--root-dir` parameter specifies the directory where file operations will be performed. This is important for security reasons, as it restricts file operations to this directory only.

The `--commands-toml` parameter allows you to specify a custom TOML file for predefined commands instead of using the default `pyproject.toml` file. This is useful when you want to define a separate set of commands for different purposes.

### Available Tools

The server provides the following tools:

#### File Operations
- **create_dir**: Create directories within the authorized root directory
- **edit_file**: Edit files by replacing lines between specified start and end lines with new text
- **move_dir**: Move files and directories within the authorized root directory
- **remove_file**: Delete files within the authorized root directory
- **rename_file**: Rename files and directories within the authorized root directory

#### Git Operations
- **git_status**: Get the status of the Git repository (changed files, untracked files, etc.)
- **git_add**: Add files to the Git index (staging area)
- **git_commit**: Commit changes to the Git repository
- **git_push**: Push changes to a remote Git repository
- **git_pull**: Pull changes from a remote Git repository
- **git_checkout**: Checkout or create a branch in the Git repository
- **git_diff**: Show diffs between commits, commit and working tree, etc.

#### Makefile Operations
- **exec_make_target**: Run makefile commands securely within the project

#### Exploration Operations
- **search_files**: Search for files by regex pattern in the project directory. Supports optional root directory and output length limits.
- **search_text**: Search for lines in files matching a given pattern. Supports file filtering, context lines, and output length limits.
- **read_lines**: Read specific lines or a range from a file. Supports line range selection and output length limits.

#### Predefined Commands
- **predefined_commands**: Execute predefined commands from a TOML file (default: pyproject.toml under [tool.dkmcp.commands] section)

The TOML file format for predefined commands is as follows:

```toml
[tool.dkmcp.commands]
test = "uv run pytest"
lint = "ruff check"
check = "uvx pre-commit run --all-files"
doctest = "make doctest"
```

Each command is defined as a key-value pair where the key is the command name and the value is the command to execute. For example, when you call the predefined command "test", it will execute "uv run pytest" in the root directory.

Here's a simple example of how to define commands in a custom TOML file:

```toml
# custom_commands.toml
[tool.dkmcp.commands]
# Basic commands
hello = "echo Hello, World!"
date = "date"

# Development commands
test = "pytest"
lint = "ruff check ."
build = "python setup.py build"
```

### Example Usage with MCP Client

```python
from fastmcp import Client
async def example():
    async with Client() as client:
        # List available tools
        tools = await client.list_tools()

        # File Operations
        # Create a directory
        result = await client.call_tool("create_dir", {"path": "new_directory"})

        # Move a file
        result = await client.call_tool("move_dir", {"path1": "source.txt", "path2": "destination.txt"})

        # Remove a file
        result = await client.call_tool("remove_file", {"path": "file_to_remove.txt"})

        # Rename a file
        result = await client.call_tool("rename_file", {"path": "old_name.txt", "new_name": "new_name.txt"})

        # Edit a file
        result = await client.call_tool("edit_file", {
            "path": "file_to_edit.txt",
            "start_line": 2,
            "end_line": 4,
            "text": "This text will replace lines 2-4"
        })

        # Git Operations
        # Get repository status
        result = await client.call_tool("git_status")

        # Add files to the index
        result = await client.call_tool("git_add", {"paths": ["file1.txt", "file2.txt"]})

        # Commit changes
        result = await client.call_tool("git_commit", {"message": "Add new files"})

        # Pull changes from remote
        result = await client.call_tool("git_pull", {"remote": "origin", "branch": "main"})

        # Push changes to remote
        result = await client.call_tool("git_push")

        # Checkout a branch
        result = await client.call_tool("git_checkout", {"branch": "feature-branch", "create": True})

        # Makefile Operations
        # Run a makefile command
        result = await client.call_tool("exec_make_target", {"commands": ["test"]})

        # Exploration Operations
        # Search for Python files
        result = await client.call_tool("search_files", {"pattern": ".*\\.py$"})

        # Search for files in a specific directory with output limit
        result = await client.call_tool("search_files", {
            "pattern": "test.*",
            "root": "tests",
            "max_chars": 1000
        })

        # Search for text patterns in files
        result = await client.call_tool("search_text", {"pattern": "def.*test"})

        # Search in specific files with context
        result = await client.call_tool("search_text", {
            "pattern": "import",
            "files": ["main.py", "utils.py"],
            "context": 2
        })

        # Read specific lines from a file
        result = await client.call_tool("read_lines", {"file_path": "README.md", "start": 1, "end": 10})

        # Read entire file with character limit
        result = await client.call_tool("read_lines", {
            "file_path": "config.json",
            "max_chars": 500
        })

        # Predefined Commands
        # Execute a predefined command
        result = await client.call_tool("predefined_commands", {"command": "test"})

        # Execute a predefined command with a parameter
        result = await client.call_tool("predefined_commands", {"command": "test", "param": "specific_test"})
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/DanielAvdar/dev-kit-mcp-server.git
cd dev-kit-mcp-server

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
