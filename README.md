# Python Code MCP Server

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-code-mcp-server)](https://pypi.org/project/py-code-mcp-server/)
[![version](https://img.shields.io/pypi/v/py-code-mcp-server)](https://img.shields.io/pypi/v/py-code-mcp-server)
[![License](https://img.shields.io/:license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![OS](https://img.shields.io/badge/ubuntu-blue?logo=ubuntu)
![OS](https://img.shields.io/badge/win-blue?logo=windows)
![OS](https://img.shields.io/badge/mac-blue?logo=apple)
[![Tests](https://github.com/DanielAvdar/py-code-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/DanielAvdar/py-code-mcp-server/actions/workflows/ci.yml)
[![Code Checks](https://github.com/DanielAvdar/py-code-mcp-server/actions/workflows/code-checks.yml/badge.svg)](https://github.com/DanielAvdar/py-code-mcp-server/actions/workflows/code-checks.yml)
[![codecov](https://codecov.io/gh/DanielAvdar/py-code-mcp-server/graph/badge.svg?token=N0V9KANTG2)](https://codecov.io/gh/DanielAvdar/py-code-mcp-server)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Last Commit](https://img.shields.io/github/last-commit/DanielAvdar/py-code-mcp-server/main)

A Model Context Protocol (MCP) server for interacting with codebases. This package provides tools for turning any repository or code base into an MCP system, allowing for efficient navigation and exploration of code repositories.

## Features

- 🔍 **Repository Navigation**: Navigate and explore code repositories with ease
- 🔌 **MCP Integration**: Turn any codebase into an MCP-compliant system
- 🧩 **Code Structure Analysis**: Understand code structure through AST analysis
- 🔢 **Code Exploration**: Explore code elements like functions, classes, and imports
- 🚀 **Fast API**: Built with FastAPI for high performance

## Installation

```bash
pip install py-code-mcp-server
```

## Usage

### Running the Server

```bash
# Recommended method (fastest startup)
uv run python -m py_code.mcp_server

# Alternative method
python -m py_code.mcp_server

# Traditional method with optional parameters
py-mcp-server --host 127.0.0.1 --port 8080
```

### API Endpoints

- `GET /`: Repository navigation server information
- `POST /analyze`: Comprehensive repository structure analysis
- `POST /ast`: Code structure extraction for navigation
- `POST /tokenize`: Detailed code element identification
- `POST /count`: Repository component summarization

### Example Repository Navigation

```python
import requests

# Example code from a repository file
code = """
def process_data(data_path):
    """Process data from the specified path."""
    with open(data_path, 'r') as f:
        data = f.read()
    return data

class DataNavigator:
    """Navigate through repository data structures."""
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def find_components(self):
        """Find all components in the repository."""
        # Implementation details
        return ["component1", "component2"]
"""

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
git clone https://github.com/DanielAvdar/py-code-mcp-server.git
cd py-code-mcp-server

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
