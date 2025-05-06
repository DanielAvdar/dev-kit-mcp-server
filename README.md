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

A Model Context Protocol (MCP) server for Python code analysis. This package provides a fast and efficient way to analyze Python code using Abstract Syntax Trees (AST) and tokenization.

## Features

- 🔍 **Code Analysis**: Analyze Python code structure using AST
- 🔢 **Tokenization**: Extract tokens from Python code
- 📊 **Element Counting**: Count functions, classes, imports, and variables
- 🚀 **Fast API**: Built with FastAPI for high performance
- 🔌 **MCP Compliant**: Follows the Model Context Protocol specification

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

- `GET /`: Server information
- `POST /analyze`: Full code analysis
- `POST /ast`: AST-only analysis
- `POST /tokenize`: Token extraction
- `POST /count`: Element counting

### Example Request

```python
import requests

code = """
def hello_world():
    print("Hello, World!")

class Person:
    def __init__(self, name):
        self.name = name
"""

response = requests.post(
    "http://localhost:8000/analyze",
    json={"code": code}
)

print(response.json())
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
