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

# Alternative methods
uv run python -m dev_kit_mcp_server.mcp_server --root-dir=workdir
python -m dev_kit_mcp_server.mcp_server --root-dir=workdir
```

The `--root-dir` parameter specifies the directory where file operations will be performed. This is important for security reasons, as it restricts file operations to this directory only.

### Available Tools

The server provides the following tools:

- **exec_make_target**: Run makefile commands securely within the project
- **create_dir**: Create directories within the authorized root directory
- **move_dir**: Move files and directories within the authorized root directory
- **remove_file**: Delete files within the authorized root directory

### Example Usage with MCP Client

```python
from fastmcp import Client
async def example()
    async with Client() as client:
        # List available tools
        tools = await client.list_tools()

        # Run a makefile command
        result = await client.call_tool("exec_make_target", {"commands": ["test"]})

        # Create a directory
        result = await client.call_tool("create_dir", {"path": "new_directory"})

        # Move a file
        result = await client.call_tool("move_dir", {"path1": "source.txt", "path2": "destination.txt"})

        # Remove a file
        result = await client.call_tool("remove_file", {"path": "file_to_remove.txt"})

        # Rename a file
        result = await client.call_tool("rename_file", {"path1": "old_name.txt", "path2": "new_name.txt"})
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