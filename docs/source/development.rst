Development Guide
=================

This guide provides information for developers who want to contribute to the Python Code MCP Server project.

Environment Setup
-----------------

Prerequisites
~~~~~~~~~~~~~

- Python 3.10 or higher
- `uv <https://github.com/astral-sh/uv>`_ for dependency management

Installation for Development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/DanielAvdar/py-code-mcp-server.git
      cd py-code-mcp-server

2. Install dependencies using uv:

   .. code-block:: bash

      make install

   This will install all dependencies including development dependencies and set up pre-commit hooks.

3. Alternative installation commands:

   .. code-block:: bash

      # Update dependencies
      make update

      # Install documentation dependencies only
      make install-docs

Project Structure
-----------------

- ``py_code/``: Main package code
  - ``fastmcp_server.py``: FastMCP server implementation
  - ``tools/``: MCP tools implementation
    - ``code_analysis/``: Code analysis tools
    - ``code_editing/``: Code editing tools
    - ``utils/``: Utility functions
- ``py_code_mcp_server/``: Separate server package
- ``tests/``: Test directory
- ``docs/``: Documentation
- ``scripts/``: Utility scripts

Testing
-------

Running Tests
~~~~~~~~~~~~~

The project uses pytest for testing. Tests are located in the ``tests/`` directory.

.. code-block:: bash

   # Run all tests
   make test

   # Run tests with coverage
   make cov

   # Generate XML coverage report
   make coverage

   # Run specific tests
   uv run pytest tests/test_analyzer_simple.py

   # Run with verbose output
   uv run pytest tests/test_analyzer_simple.py -v

   # Run tests matching a pattern
   uv run pytest -k "analyzer"

Writing Tests
~~~~~~~~~~~~~

1. Test File Naming:
   - Name test files with the prefix ``test_`` (e.g., ``test_analyzer.py``)
   - Place test files in the ``tests/`` directory

2. Test Function Naming:
   - Name test functions with the prefix ``test_`` (e.g., ``test_parse_ast_simple``)
   - Use descriptive names that indicate what is being tested

3. Test Structure:
   - Each test should focus on testing a single functionality
   - Include clear docstrings explaining what the test is checking
   - Use assertions to verify expected behavior

4. Example Test:

   .. code-block:: python

      """Tests for the code analyzer module."""

      import pytest

      from py_code.tools.code_analysis.analyzer import CodeAnalyzer


      def test_parse_ast_simple():
          """Test parsing a simple function definition."""
          code = """
      def hello_world():
          print("Hello, World!")
      """
          result = CodeAnalyzer.parse_ast(code)

          # Check that we have one function
          assert "functions" in result
          assert len(result["functions"]) == 1
          assert result["functions"][0]["name"] == "hello_world"
          assert result["functions"][0]["params"] == []

Code Style
----------

The project follows strict code style guidelines:

1. Linting:
   - Uses `ruff <https://github.com/astral-sh/ruff>`_ for linting
   - Run linting checks with ``make check``
   - Configuration is in ``pyproject.toml`` under ``[tool.ruff]``

2. Type Checking:
   - Uses `mypy <https://mypy.readthedocs.io/>`_ for static type checking
   - Run type checking with ``make mypy``
   - Configuration is in ``pyproject.toml`` under ``[tool.mypy]``
   - All functions and methods should have type annotations

3. Documentation:
   - All modules, classes, functions, and methods should have docstrings
   - Docstrings should follow the Google style format
   - Build documentation with ``make doc``
   - Run doctests with ``make doctest``

Pre-commit Hooks
----------------

The project uses pre-commit hooks to ensure code quality:

.. code-block:: bash

   # Install pre-commit hooks
   uv tool install pre-commit --with pre-commit-uv --force-reinstall
   uv run pre-commit install

   # Run pre-commit hooks on all files
   make check

Continuous Integration
----------------------

The project uses GitHub Actions for CI/CD:

1. Tests: Run on every push and pull request
2. Code Checks: Linting, type checking, and other quality checks
3. Coverage: Test coverage reporting

Development Workflow
-------------------

1. Create a feature branch from ``main``
2. Make changes and add tests
3. Run tests and code checks
4. Submit a pull request
5. Address review comments
6. Merge to ``main`` after approval

Building Documentation
----------------------

The project uses Sphinx for documentation:

.. code-block:: bash

   # Install documentation dependencies
   make install-docs

   # Build documentation
   make doc

   # Run doctests
   make doctest

   # Build documentation ignoring warnings
   make doc-build

The documentation is built in the ``docs/build/`` directory.
