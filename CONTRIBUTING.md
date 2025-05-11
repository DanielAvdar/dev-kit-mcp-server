# Contributing to Dev-Kit MCP Server

Thank you for your interest in contributing to this project! Here's how you can help.

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/DanielAvdar/dev-kit-mcp-server.git
   cd dev-kit-mcp-server
   ```

2. Create a virtual environment and install development dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks:
   ```
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch:
   ```
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run the quality checks:
   ```
   make check-all
   ```

4. Run the test suite:
   ```
   make test
   ```

5. Submit a pull request

## Code Standards

- Follow PEP 8 style guidelines
- Include type annotations for all functions and methods
- Include docstrings for all modules, classes, functions, and methods
- Write tests for new functionality
- Keep test coverage high

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if necessary
3. Add entry to CHANGELOG.md in the "Unreleased" section
4. Request review from a maintainer

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
