"""Tests for the server module."""

import pytest

# Skip all tests in this file since server.py has been removed
pytestmark = pytest.mark.skip("Skipped because server.py has been removed and we are using fastmcp_server.py instead")


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data


def test_analyze_code_endpoint():
    """Test the analyze code endpoint."""
    code = "def hello(): return 'world'"
    response = client.post("/analyze", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data


def test_analyze_code_endpoint_error():
    """Test the analyze code endpoint with invalid code."""
    code = "def hello() return 'world'"  # Syntax error
    response = client.post("/analyze", json={"code": code})
    # The implementation might handle errors with 200 or raise an exception with 500
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        # If error is handled in the implementation
        assert "error" in str(response.json())
    else:
        # If error is thrown as HTTP exception
        assert "detail" in response.json()


def test_ast_analysis_endpoint():
    """Test the AST analysis endpoint."""
    code = "def hello(): return 'world'"
    response = client.post("/ast", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "functions" in data["result"]


def test_ast_analysis_endpoint_error():
    """Test the AST analysis endpoint with invalid code."""
    code = "def hello() return 'world'"  # Syntax error
    response = client.post("/ast", json={"code": code})
    # The implementation might handle errors with 200 or raise an exception with 500
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        # If error is handled in the implementation
        assert "error" in str(response.json())
    else:
        # If error is thrown as HTTP exception
        assert "detail" in response.json()


def test_tokenize_code_endpoint():
    """Test the tokenize code endpoint."""
    code = "def hello(): return 'world'"
    response = client.post("/tokenize", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "tokens" in data["result"]


def test_tokenize_code_endpoint_error():
    """Test the tokenize code endpoint with invalid code."""
    # Testing with None instead of a string will cause a validation error
    response = client.post("/tokenize", json={"code": None})
    assert response.status_code == 422  # Validation error


def test_count_elements_endpoint():
    """Test the count elements endpoint."""
    code = "def hello(): return 'world'\nclass Test: pass\nimport os"
    response = client.post("/count", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "function_count" in data["result"]
    assert "class_count" in data["result"]
    assert "import_count" in data["result"]
    assert "variable_count" in data["result"]


def test_count_elements_endpoint_error():
    """Test the count elements endpoint with invalid code."""
    code = "def hello() return 'world'"  # Syntax error
    response = client.post("/count", json={"code": code})
    # The implementation might handle errors with 200 or raise an exception with 500
    assert response.status_code in (200, 500)
    if response.status_code == 200:
        # The implementation might return zeros or an error
        result_str = str(response.json())
        assert "function_count" in result_str  # Should at least have this field
    else:
        # If error is thrown as HTTP exception
        assert "detail" in response.json()


def test_start_server(monkeypatch):
    """Test the start_server function."""
    # Mock uvicorn.run to prevent actually starting the server
    mock_called = False
    mock_args = None
    mock_kwargs = None

    def mock_run(*args, **kwargs):
        nonlocal mock_called, mock_args, mock_kwargs
        mock_called = True
        mock_args = args
        mock_kwargs = kwargs

    # Apply the monkeypatch
    monkeypatch.setattr("uvicorn.run", mock_run)

    # Call the function
    start_server(host="localhost", port=8888)

    # Verify the mock was called with expected args
    assert mock_called
    assert mock_kwargs["host"] == "localhost"
    assert mock_kwargs["port"] == 8888
    assert mock_args[0] == app
