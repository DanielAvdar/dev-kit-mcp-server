"""Additional tests for the analyzer module to improve coverage."""

import io
from unittest import mock

from py_code.tools.code_analysis.analyzer import CodeAnalyzer


def test_parse_ast_with_syntax_error():
    """Test parsing AST with syntax error."""
    code = "def func() return 'hi'"  # Missing colon
    result = CodeAnalyzer.parse_ast(code)
    assert "error" in result
    assert "Syntax error" in result["error"]


def test_parse_ast_with_import_from():
    """Test parsing AST with import from statements."""
    code = "from os import path"
    result = CodeAnalyzer.parse_ast(code)
    assert "imports" in result
    assert any(imp["name"] == "os.path" for imp in result["imports"])


def test_parse_ast_with_import_from_no_module():
    """Test parsing AST with import from statements without module."""
    code = "from . import path"
    result = CodeAnalyzer.parse_ast(code)
    assert "imports" in result
    assert any(imp["name"] == ".path" for imp in result["imports"])


def test_tokenize_code_with_error():
    """Test tokenizing code that causes an error."""
    # Create a broken byte sequence to force an error
    # We'll mock an error condition rather than trying to pass wrong types
    with mock.patch.object(io, "BytesIO") as mock_bytesio:
        mock_bytesio.side_effect = Exception("Tokenization error")
        tokens = CodeAnalyzer.tokenize_code("any code")
        # The function handles exceptions internally and returns error info
        assert len(tokens) == 1
        assert "error" in tokens[0]
        assert "Tokenization error" in tokens[0]["error"]


def test_token_type_counting():
    """Test that token types are properly counted in analyze."""
    code = "x = 1 + 2"
    result = CodeAnalyzer.analyze(code)
    assert "token_summary" in result
    # The code should have NAME, OP, NUMBER tokens
    assert "NAME" in result["token_summary"]
    assert "OP" in result["token_summary"]
    assert "NUMBER" in result["token_summary"]

    # Check that counts are accumulated
    assert result["token_summary"]["NAME"] >= 1
    assert result["token_summary"]["OP"] >= 1
    assert result["token_summary"]["NUMBER"] >= 1
