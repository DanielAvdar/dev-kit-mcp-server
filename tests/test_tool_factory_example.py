"""Tests for the tool factory example module."""

import ast
import asyncio
from unittest.mock import MagicMock, call, patch

import pytest

from py_code.tools.tool_factory_example import (
    CodeMetricsAnalyzer,
    analyze_code_complexity,
    get_code_summary,
    init_application,
    log_execution_time,
    log_input_params,
    start_server,
    start_timer,
    validate_code,
)


def test_log_execution_time():
    """Test log_execution_time hook."""
    mock_logger = MagicMock()

    with patch("py_code.tools.tool_factory_example.logger", mock_logger):
        # Test with _start_time provided
        log_execution_time("result", arg1="value", _start_time=100.0)
        mock_logger.info.assert_called_once()
        assert "executed in" in mock_logger.info.call_args[0][0]

        mock_logger.reset_mock()

        # Test without _start_time
        log_execution_time("result", arg1="value")
        mock_logger.info.assert_not_called()


def test_start_timer():
    """Test start_timer hook."""
    with patch("py_code.tools.tool_factory_example.time.time") as mock_time:
        mock_time.return_value = 12345.0

        result = start_timer("arg1", "arg2", kwarg="value")

        assert isinstance(result, dict)
        assert "_start_time" in result
        assert result["_start_time"] == 12345.0


def test_log_input_params():
    """Test log_input_params hook."""
    mock_logger = MagicMock()

    with patch("py_code.tools.tool_factory_example.logger", mock_logger):
        log_input_params("arg1", "arg2", kwarg="value")

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        assert "Function called with args" in log_message
        assert "arg1" in log_message
        assert "arg2" in log_message
        assert "kwarg" in log_message


def test_analyze_code_complexity():
    """Test analyze_code_complexity function."""
    test_code = "def hello(): return 'world'"
    mock_ast_analysis = {"functions": [{"name": "hello"}], "classes": []}

    with patch("py_code.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.return_value = mock_ast_analysis

        result = analyze_code_complexity(test_code)

        # Verify analysis was performed
        mock_parse_ast.assert_called_once_with(test_code)

        # Check result structure
        assert "function_count" in result
        assert "class_count" in result
        assert "line_count" in result
        assert "character_count" in result
        assert "complexity_score" in result

        # Check values
        assert result["function_count"] == 1
        assert result["class_count"] == 0
        assert result["character_count"] == len(test_code)


def test_get_code_summary():
    """Test get_code_summary function."""
    test_code = """
def hello():
    return 'world'

class Test:
    pass
"""

    mock_ast_analysis = {"functions": [{"name": "hello"}], "classes": [{"name": "Test"}], "imports": [{"name": "os"}]}

    mock_tokens = [{"type": "NAME", "string": "def"}]

    with (
        patch("py_code.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast,
        patch("py_code.analyzer.CodeAnalyzer.tokenize_code") as mock_tokenize,
    ):
        mock_parse_ast.return_value = mock_ast_analysis
        mock_tokenize.return_value = mock_tokens

        result = get_code_summary(test_code)

        # Verify methods were called
        mock_parse_ast.assert_called_once_with(test_code)
        mock_tokenize.assert_called_once_with(test_code)

        # Check result structure
        assert "functions" in result
        assert "classes" in result
        assert "imports" in result
        assert "token_count" in result
        assert "line_count" in result

        # Check values
        assert result["functions"] == ["hello"]
        assert result["classes"] == ["Test"]
        assert result["imports"] == ["os"]
        assert result["token_count"] == 1


@pytest.mark.asyncio
async def test_validate_code_valid():
    """Test validate_code function with valid code."""
    test_code = "def hello(): return 'world'"
    mock_ctx = MagicMock()

    # Create a future to return from the mock async method
    future = asyncio.Future()
    future.set_result(None)
    mock_ctx.info.return_value = future

    with patch("py_code.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.return_value = {}

        result = await validate_code(test_code, ctx=mock_ctx)

        # Verify methods were called
        mock_parse_ast.assert_called_once()  # Just check it was called, not with what
        mock_ctx.info.assert_called_once()

        # Check result
        assert result["valid"] is True
        assert result["errors"] is None


@pytest.mark.asyncio
async def test_validate_code_invalid():
    """Test validate_code function with invalid code."""
    test_code = "def hello() return 'world'"  # Missing colon
    mock_ctx = MagicMock()

    # Create a future to return from the mock async method
    future = asyncio.Future()
    future.set_result(None)
    mock_ctx.error.return_value = future

    with patch("py_code.analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        mock_parse_ast.side_effect = SyntaxError("invalid syntax")

        result = await validate_code(test_code, ctx=mock_ctx)

        # Verify methods were called
        mock_parse_ast.assert_called_once()  # Just check it was called, not with what
        mock_ctx.error.assert_called_once()

        # Check result
        assert result["valid"] is False
        assert isinstance(result["errors"], str)


def test_code_metrics_analyzer_count_statements():
    """Test CodeMetricsAnalyzer.count_statements method."""
    test_code = """
x = 1
if x > 0:
    print("Positive")
for i in range(10):
    x += i
return x
"""

    analyzer = CodeMetricsAnalyzer()

    # Create nodes of different types
    mock_tree = MagicMock()
    assign_node = MagicMock(spec=ast.Assign)
    call_node = MagicMock(spec=ast.Call)
    if_node = MagicMock(spec=ast.If)
    for_node = MagicMock(spec=ast.For)
    return_node = MagicMock(spec=ast.Return)

    # Set up the ast.walk patch to return our nodes
    with patch("ast.walk") as mock_walk:
        mock_walk.return_value = [assign_node, call_node, if_node, for_node, return_node]
        with patch("py_code.analyzer.CodeAnalyzer.parse_raw_ast") as mock_parse_raw_ast:
            mock_parse_raw_ast.return_value = mock_tree

            result = analyzer.count_statements(test_code)

            # Verify methods were called
            mock_parse_raw_ast.assert_called_once_with(test_code)
            mock_walk.assert_called_once_with(mock_tree)

            # Check result
            assert result["assignments"] == 1
            assert result["calls"] == 1
            assert result["conditionals"] == 1
            assert result["loops"] == 1
            assert result["returns"] == 1


def test_code_metrics_analyzer_count_statements_error():
    """Test CodeMetricsAnalyzer.count_statements with an error."""
    test_code = "invalid syntax"
    analyzer = CodeMetricsAnalyzer()

    with patch("py_code.analyzer.CodeAnalyzer.parse_raw_ast") as mock_parse_raw_ast:
        mock_parse_raw_ast.side_effect = SyntaxError("invalid syntax")

        result = analyzer.count_statements(test_code)

        # Verify method was called
        mock_parse_raw_ast.assert_called_once_with(test_code)

        # Check error in result
        assert "error" in result
        assert "invalid syntax" in result["error"]


def test_code_metrics_analyzer_measure_complexity():
    """Test CodeMetricsAnalyzer.measure_complexity method."""
    test_code = """
if x > 0:
    print("Positive")
for i in range(10):
    if i % 2 == 0:
        print("Even")
    try:
        result = 10 / i
    except ZeroDivisionError:
        pass
"""

    analyzer = CodeMetricsAnalyzer()

    # Create nodes that contribute to complexity
    mock_tree = MagicMock()
    if_node1 = MagicMock(spec=ast.If)
    for_node = MagicMock(spec=ast.For)
    if_node2 = MagicMock(spec=ast.If)
    try_node = MagicMock(spec=ast.Try)

    with patch("ast.walk") as mock_walk:
        mock_walk.return_value = [if_node1, for_node, if_node2, try_node]
        with patch("py_code.analyzer.CodeAnalyzer.parse_raw_ast") as mock_parse_raw_ast:
            mock_parse_raw_ast.return_value = mock_tree

            result = analyzer.measure_complexity(test_code)

            # Verify methods were called
            mock_parse_raw_ast.assert_called_once_with(test_code)
            mock_walk.assert_called_once_with(mock_tree)

            # Check result
            assert "cyclomatic_complexity" in result
            assert "branch_points" in result
            assert result["cyclomatic_complexity"] == 5  # 1 + 4 branches
            assert result["branch_points"] == 4


def test_code_metrics_analyzer_measure_complexity_error():
    """Test CodeMetricsAnalyzer.measure_complexity with an error."""
    test_code = "invalid syntax"
    analyzer = CodeMetricsAnalyzer()

    with patch("py_code.analyzer.CodeAnalyzer.parse_raw_ast") as mock_parse_raw_ast:
        mock_parse_raw_ast.side_effect = SyntaxError("invalid syntax")

        result = analyzer.measure_complexity(test_code)

        # Verify method was called
        mock_parse_raw_ast.assert_called_once_with(test_code)

        # Check error in result
        assert "error" in result
        assert "invalid syntax" in result["error"]


def test_init_application():
    """Test init_application function."""
    mock_logger = MagicMock()
    mock_tool_factory = MagicMock()

    with (
        patch("py_code.tools.tool_factory_example.logger", mock_logger),
        patch("py_code.tools.tool_factory_example.tool_factory", mock_tool_factory),
    ):
        init_application()

        # Verify hooks were added
        assert mock_tool_factory.add_pre_hook.call_count == 2
        mock_tool_factory.add_pre_hook.assert_has_calls([call(start_timer), call(log_input_params)], any_order=True)

        mock_tool_factory.add_post_hook.assert_called_once_with(log_execution_time)

        # Verify CodeMetricsAnalyzer class was decorated
        mock_tool_factory.assert_called_once_with(CodeMetricsAnalyzer)

        # Verify log message
        mock_logger.info.assert_called_once_with("All tools have been registered successfully")


def test_start_server():
    """Test start_server function."""
    mock_logger = MagicMock()
    mock_mcp = MagicMock()

    with (
        patch("py_code.tools.tool_factory_example.logger", mock_logger),
        patch("py_code.tools.tool_factory_example.mcp", mock_mcp),
        patch("py_code.tools.tool_factory_example.init_application") as mock_init,
    ):
        # Call with default args
        start_server()

        # Verify init_application was called
        mock_init.assert_called_once()

        # Verify log message
        mock_logger.info.assert_called_once_with("Starting ToolFactory example server on 0.0.0.0:8000")

        # Verify server was started
        mock_mcp.run.assert_called_once_with(transport="sse", host="0.0.0.0", port=8000)

        # Reset mocks for next test
        mock_logger.reset_mock()
        mock_mcp.reset_mock()
        mock_init.reset_mock()

        # Call with custom args
        start_server(host="127.0.0.1", port=9000)

        # Verify init_application was called again
        mock_init.assert_called_once()

        # Verify log message with custom args
        mock_logger.info.assert_called_once_with("Starting ToolFactory example server on 127.0.0.1:9000")

        # Verify server was started with custom args
        mock_mcp.run.assert_called_once_with(transport="sse", host="127.0.0.1", port=9000)
