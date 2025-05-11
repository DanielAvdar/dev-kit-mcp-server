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

A Model Context Protocol (MCP) server for interacting with codebases.
This package provides tools for turning any repository or code base into an MCP system.

## Features

- 🔌 **MCP Integration**: Turn any codebase into an MCP-compliant system
- 🛠️ **Custom Tools**: Create custom tools for specific repository needs
- 🔍 **Repository Navigation**: Navigate and explore code repositories with ease
- 🧩 **Code Structure Analysis**: Understand code structure through AST analysis
- 🔢 **Code Exploration**: Explore code elements like functions, classes, and imports
- 🚀 **Fast API**: Built with FastAPI for high performance

## Installation

```bash
pip install dev-kit-mcp-server
```

## Usage

### Running the Server

```bash
# Recommended method (fastest startup)
uv run python -m dev_kit.mcp_server

# Alternative method
python -m dev_kit.mcp_server

# Traditional method with optional parameters
dev-kit-mcp-server --host 127.0.0.1 --port 8080
```

### API Endpoints

- `GET /`: Repository navigation server information
- `POST /analyze`: Comprehensive repository structure analysis
- `POST /ast`: Code structure extraction for navigation
- `POST /tokenize`: Detailed code element identification
- `POST /count`: Repository component summarization



# Get repository structure for navigation
response = requests.post(
    "http://localhost:8000/analyze",
    json={"code": code, "path": "src/data/navigator.py"}
)

# Use the structure for repository navigation
structure = response.json()
print(f"Repository components found: {len(structure['result']['ast_analysis']['functions'])} functions, "
      f"{len(structure['result']['ast_analysis']['classes'])} classes")
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
