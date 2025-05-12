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

A Model Context Protocol (MCP) server for agent development tools.
This package provides scoped authorized operations in the root project directory such as running makefile commands, moving and deleting files, and renaming files. It's a great MCP for VS-Code Copilot and other AI-assisted development tools.

## Features

- 🔌 **MCP Integration**: Turn any codebase into an MCP-compliant system
- 🛠️ **File Operations**: Create, move, delete, and rename files and directories
- 🔧 **Makefile Integration**: Execute makefile commands securely within the root directory
- 🔒 **Scoped Authorization**: All operations are restricted to the specified root directory
- 🔄 **VS-Code Copilot Integration**: Works seamlessly with VS-Code Copilot
- 🚀 **Fast API**: Built with FastAPI for high performance

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

- **create_dir**: Create directories and files
- **move_dir**: Move files and directories
- **remove_file**: Remove files and directories
- **rename_file**: Rename files and directories
- **exec_make_target**: Execute makefile targets

### Example Usage

```python
from fastmcp import Client

async with Client("http://localhost:8000") as client:
    # List available tools
    tools = await client.list_tools()

    # Create a directory
    result = await client.call_tool("create_dir", {"path": "new_directory"})

    # Execute a makefile target
    result = await client.call_tool("exec_make_target", {"commands": ["test"]})
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
