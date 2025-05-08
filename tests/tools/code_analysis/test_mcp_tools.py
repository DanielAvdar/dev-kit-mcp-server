"""Tests for the code_analysis.mcp_tools module."""

from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.code_analysis.mcp_tools import (
    analyze_ast,
    analyze_full,
    analyze_tokens,
    count_elements,
)


def test_analyze_full_valid_code():
    """Test analyze_full with valid Python code."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.analyze method
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.analyze") as mock_analyze:
        mock_analyze.return_value = {"sample": "analysis"}

        result = analyze_full(code)

        # Verify the analyzer was called and result is formatted correctly
        mock_analyze.assert_called_once_with(code)
        assert result == {"result": {"sample": "analysis"}}


def test_analyze_full_error():
    """Test analyze_full when an error occurs."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.analyze method to raise an exception
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.analyze") as mock_analyze:
        mock_analyze.side_effect = ValueError("Test error")

        # The function should re-raise as a generic Exception
        with pytest.raises(Exception) as exc_info:
            analyze_full(code)

        assert "Error analyzing code: Test error" in str(exc_info.value)


def test_analyze_ast_valid_code():
    """Test analyze_ast with valid Python code."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.parse_ast method
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.return_value = {"functions": [{"name": "hello"}]}

        result = analyze_ast(code)

        # Verify the parser was called and result is formatted correctly
        mock_parse_ast.assert_called_once_with(code)
        assert result == {"result": {"functions": [{"name": "hello"}]}}


def test_analyze_ast_none_code():
    """Test analyze_ast with None code."""
    with pytest.raises(Exception) as exc_info:
        analyze_ast(None)

    assert "Error parsing AST: code cannot be None" in str(exc_info.value)


def test_analyze_ast_syntax_error():
    """Test analyze_ast with code containing syntax errors."""
    code = "def hello() return 'world'"  # Missing colon

    with pytest.raises(Exception) as exc_info:
        analyze_ast(code)

    assert "Error parsing AST:" in str(exc_info.value)


def test_analyze_ast_processing_error():
    """Test analyze_ast when an error occurs during processing."""
    code = "def hello(): return 'world'"

    # Mock ast.parse to pass but CodeAnalyzer.parse_ast to fail
    with (
        patch("ast.parse") as mock_ast_parse,
        patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast,
    ):
        mock_ast_parse.return_value = MagicMock()
        mock_parse_ast.side_effect = ValueError("Test error")

        with pytest.raises(Exception) as exc_info:
            analyze_ast(code)

        assert "Error parsing AST: Test error" in str(exc_info.value)


def test_analyze_tokens_valid_code():
    """Test analyze_tokens with valid Python code."""
    code = "def hello(): return 'world'"
    tokens = [{"type": "NAME", "string": "def"}]

    # Mock the CodeAnalyzer.tokenize_code method
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.tokenize_code") as mock_tokenize:
        mock_tokenize.return_value = tokens

        result = analyze_tokens(code)

        # Verify the tokenizer was called and result is formatted correctly
        mock_tokenize.assert_called_once_with(code)
        assert result == {"result": {"tokens": tokens}}


def test_analyze_tokens_none_code():
    """Test analyze_tokens with None code."""
    with pytest.raises(Exception) as exc_info:
        analyze_tokens(None)

    assert "Error tokenizing code: code cannot be None" in str(exc_info.value)


def test_analyze_tokens_error():
    """Test analyze_tokens when an error occurs."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.tokenize_code method to raise an exception
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.tokenize_code") as mock_tokenize:
        mock_tokenize.side_effect = ValueError("Test error")

        with pytest.raises(Exception) as exc_info:
            analyze_tokens(code)

        assert "Error tokenizing code: Test error" in str(exc_info.value)


def test_count_elements_valid_code():
    """Test count_elements with valid Python code."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.parse_ast method
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.return_value = {"functions": [{"name": "hello"}], "classes": [], "imports": [], "variables": []}

        result = count_elements(code)

        # Verify the parser was called and result is formatted correctly
        mock_parse_ast.assert_called_once_with(code)
        assert result == {"result": {"function_count": 1, "class_count": 0, "import_count": 0, "variable_count": 0}}


def test_count_elements_with_context():
    """Test count_elements with a provided context."""
    code = "def hello(): return 'world'"
    mock_ctx = MagicMock()

    # Mock the CodeAnalyzer.parse_ast method
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.return_value = {"functions": [{"name": "hello"}], "classes": [], "imports": [], "variables": []}

        result = count_elements(code, ctx=mock_ctx)

        # Verify the context info method was called
        mock_ctx.info.assert_called_once()
        assert "characters" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert result["result"]["function_count"] == 1


def test_count_elements_error():
    """Test count_elements when an error occurs."""
    code = "def hello(): return 'world'"

    # Mock the CodeAnalyzer.parse_ast method to raise an exception
    with patch("py_code.tools.code_analysis.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.side_effect = ValueError("Test error")

        with pytest.raises(Exception) as exc_info:
            count_elements(code)

        assert "Error counting elements: Test error" in str(exc_info.value)
