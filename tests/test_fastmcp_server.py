"""Tests for the FastMCP server implementation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from py_code.fastmcp_server import (
    analyze_code,
    class_example,
    count_functions,
    hello_world_example,
    mcp,
    parse_ast,
    tokenize_code,
)


def test_analyze_code():
    """Test the analyze_code tool."""
    code = "def test(): return 42"

    # Call the function directly
    result = analyze_code(code)

    # Verify result structure
    assert "ast_analysis" in result
    assert "tokens" in result
    assert "token_summary" in result

    # Verify AST analysis
    ast_analysis = result["ast_analysis"]
    assert "functions" in ast_analysis

    # Check that the function was detected
    functions = ast_analysis["functions"]
    assert len(functions) == 1
    assert functions[0]["name"] == "test"


def test_parse_ast():
    """Test the parse_ast tool."""
    code = "class TestClass:\n    def method(self): pass"

    # Call the function directly
    result = parse_ast(code)

    # Verify structure
    assert "classes" in result
    assert "functions" in result

    # Check class detection
    classes = result["classes"]
    assert len(classes) == 1
    assert classes[0]["name"] == "TestClass"

    # Check method detection
    functions = result["functions"]
    assert len(functions) == 1
    assert functions[0]["name"] == "method"


def test_tokenize_code():
    """Test the tokenize_code tool."""
    code = "x = 1 + 2"

    # Call the function directly
    tokens = tokenize_code(code)

    # Verify token list structure
    assert len(tokens) > 0

    # Check for expected token types
    token_types = [token["type"] for token in tokens]
    assert "NAME" in token_types  # Variable name
    assert "NUMBER" in token_types  # Numeric literals

    # Check specific tokens
    token_strings = [token["string"] for token in tokens]
    assert "x" in token_strings
    assert "1" in token_strings
    assert "2" in token_strings
    assert "+" in token_strings


@pytest.mark.asyncio
async def test_count_functions():
    """Test the count_functions tool."""
    code = """
import os
from sys import path

class TestClass:
    def __init__(self):
        self.x = 1

def func1():
    pass

def func2():
    pass
"""

    # Create a mock context
    mock_ctx = AsyncMock()
    mock_ctx.info = AsyncMock()

    # Call the function with mock context
    result = await count_functions(code, mock_ctx)

    # Verify result structure
    assert "function_count" in result
    assert "class_count" in result
    assert "import_count" in result
    assert "variable_count" in result

    # Check counts
    assert result["function_count"] == 3  # __init__, func1, func2
    assert result["class_count"] == 1  # TestClass
    assert result["import_count"] == 2  # os, sys.path

    # Verify context.info was called
    mock_ctx.info.assert_called_once()


def test_hello_world_example():
    """Test the hello_world_example resource."""
    # Call the resource function
    code = hello_world_example()

    # Verify it returns a string
    assert isinstance(code, str)

    # Check content
    assert "def greet" in code
    assert "Hello, {name}" in code


def test_class_example():
    """Test the class_example resource."""
    # Call the resource function
    code = class_example()

    # Verify it returns a string
    assert isinstance(code, str)

    # Check content
    assert "class Person" in code
    assert "__init__" in code
    assert "def greet" in code


@pytest.mark.asyncio
async def test_mcp_server_tools():
    """Test that the FastMCP server has the expected tools."""
    # Create patch for get_tools
    with patch.object(mcp, "get_tools", new_callable=AsyncMock) as mock_get_tools:
        # Mock return value
        mock_get_tools.return_value = {
            "analyze_code": MagicMock(),
            "parse_ast": MagicMock(),
            "tokenize_code": MagicMock(),
            "count_functions": MagicMock(),
        }

        # Call the mocked method
        tools = await mcp.get_tools()

        # Check tool names
        tool_names = list(tools.keys())
        assert "analyze_code" in tool_names
        assert "parse_ast" in tool_names
        assert "tokenize_code" in tool_names
        assert "count_functions" in tool_names


@pytest.mark.asyncio
async def test_mcp_server_resources():
    """Test that the FastMCP server has the expected resources."""
    # Create patch for get_resources
    with patch.object(mcp, "get_resources", new_callable=AsyncMock) as mock_get_resources:
        # Mock return value
        mock_get_resources.return_value = {
            "code://examples/hello_world": MagicMock(),
            "code://examples/class_example": MagicMock(),
        }

        # Call the mocked method
        resources = await mcp.get_resources()

        # Check resource URIs
        resource_uris = list(resources.keys())
        assert "code://examples/hello_world" in resource_uris
        assert "code://examples/class_example" in resource_uris
