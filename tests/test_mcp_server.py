"""Tests for the MCP server implementation."""

from fastapi.testclient import TestClient

from py_code.server import app

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns the correct info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_ast_analysis():
    """Test the AST analysis endpoint."""
    code = """
def hello(name):
    return f"Hello, {name}!"

class Person:
    def __init__(self, name):
        self.name = name
"""

    response = client.post("/ast", json={"code": code})

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    # Check that the result contains the expected structure
    result = data["result"]
    assert "functions" in result
    assert "classes" in result

    # Verify the function was detected
    functions = result["functions"]
    assert len(functions) >= 2  # hello and __init__

    function_names = [f["name"] for f in functions]
    assert "hello" in function_names

    # Verify the class was detected
    classes = result["classes"]
    assert len(classes) >= 1

    class_names = [c["name"] for c in classes]
    assert "Person" in class_names


def test_tokenize_endpoint():
    """Test the tokenize endpoint."""
    code = 'print("Hello, world!")'

    response = client.post("/tokenize", json={"code": code})

    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tokens" in data["result"]

    # Check that we have some tokens
    tokens = data["result"]["tokens"]
    assert len(tokens) > 0

    # Verify token structure
    for token in tokens:
        assert "type" in token
        assert "string" in token


def test_analyze_endpoint():
    """Test the comprehensive analyze endpoint."""
    code = """
import os
from typing import List

def get_files(directory: str) -> List[str]:
    return os.listdir(directory)
"""

    response = client.post("/analyze", json={"code": code})

    assert response.status_code == 200
    data = response.json()
    assert "result" in data

    # Check that the result contains all expected components
    result = data["result"]
    assert "ast_analysis" in result
    assert "tokens" in result
    assert "token_summary" in result

    # Verify AST analysis
    ast_analysis = result["ast_analysis"]
    assert "imports" in ast_analysis
    assert "functions" in ast_analysis

    # Check that imports were detected
    imports = ast_analysis["imports"]
    import_modules = [imp["name"] for imp in imports]
    assert "os" in import_modules
    assert "typing.List" in import_modules

    # Verify function detection
    functions = ast_analysis["functions"]
    function_names = [f["name"] for f in functions]
    assert "get_files" in function_names
