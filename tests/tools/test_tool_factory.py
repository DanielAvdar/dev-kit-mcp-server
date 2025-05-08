"""Tests for the tool factory module."""

from unittest.mock import MagicMock, patch

from fastmcp import FastMCP

from py_code.tools.tool_factory import ToolFactory


def test_tool_factory_init():
    """Test ToolFactory initialization."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    assert factory.mcp == mock_mcp
    assert factory._pre_hooks == []
    assert factory._post_hooks == []


def test_add_pre_hook():
    """Test adding a pre-execution hook."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    def sample_hook():
        pass

    factory.add_pre_hook(sample_hook)
    assert factory._pre_hooks == [sample_hook]


def test_add_post_hook():
    """Test adding a post-execution hook."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    def sample_hook():
        pass

    factory.add_post_hook(sample_hook)
    assert factory._post_hooks == [sample_hook]


def test_decorate_function():
    """Test decorating a single function."""
    mock_mcp = MagicMock(spec=FastMCP)
    # Mock the tool decorator to return the function unchanged for testing
    mock_mcp.tool.return_value = lambda x: x
    factory = ToolFactory(mock_mcp)

    def sample_function(param1, param2):
        return f"{param1} {param2}"

    decorated = factory._decorate_function(sample_function)

    # Ensure the function can still be called
    result = decorated("hello", "world")
    assert result == "hello world"

    # Ensure the decorator was applied
    mock_mcp.tool.assert_called_once()


def test_decorate_function_with_hooks():
    """Test decorating a function with pre and post hooks."""
    mock_mcp = MagicMock(spec=FastMCP)
    # Mock the tool decorator to return the function unchanged for testing
    mock_mcp.tool.return_value = lambda x: x
    factory = ToolFactory(mock_mcp)

    pre_hook_called = False
    post_hook_called = False

    def pre_hook(*args, **kwargs):
        nonlocal pre_hook_called
        pre_hook_called = True
        return {"extra_param": "added"}

    def post_hook(result, *args, **kwargs):
        nonlocal post_hook_called
        post_hook_called = True
        return f"{result} modified"

    factory.add_pre_hook(pre_hook)
    factory.add_post_hook(post_hook)

    def sample_function(param1, extra_param=None):
        return f"{param1} {extra_param}"

    decorated = factory._decorate_function(sample_function)

    # Call the decorated function
    result = decorated("hello")

    # Verify hooks were called and modified the result
    assert pre_hook_called
    assert post_hook_called
    assert result == "hello added modified"


def test_call_with_function():
    """Test calling the factory directly with a function."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    # Patch the _decorate_function method to verify it's called
    with patch.object(factory, "_decorate_function") as mock_decorate:
        mock_decorate.return_value = "decorated"

        def sample_function():
            pass

        result = factory(sample_function)

        mock_decorate.assert_called_once_with(sample_function)
        assert result == "decorated"


def test_call_with_function_list():
    """Test calling the factory with a list of functions."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    # Patch the _decorate_function method to verify it's called for each function
    with patch.object(factory, "_decorate_function") as mock_decorate:
        mock_decorate.side_effect = ["decorated1", "decorated2"]

        def function1():
            pass

        def function2():
            pass

        result = factory([function1, function2])

        assert mock_decorate.call_count == 2
        assert result == ["decorated1", "decorated2"]


def test_call_with_class():
    """Test calling the factory with a class."""
    mock_mcp = MagicMock(spec=FastMCP)
    factory = ToolFactory(mock_mcp)

    # Patch the decorate_methods method to verify it's called
    with patch.object(factory, "decorate_methods") as mock_decorate_methods:

        class SampleClass:
            def method1(self):
                pass

            def method2(self):
                pass

        result = factory(SampleClass)

        mock_decorate_methods.assert_called_once_with(SampleClass)
        assert result == SampleClass


def test_decorate_methods():
    """Test decorating all public methods of a class."""
    mock_mcp = MagicMock(spec=FastMCP)
    # Mock the tool decorator to return the function unchanged for testing
    mock_mcp.tool.return_value = lambda x: x
    factory = ToolFactory(mock_mcp)

    class SampleClass:
        def public_method(self):
            return "public"

        def _private_method(self):
            return "private"

    # Patch the _decorate_function method to verify it's called for public methods only
    with patch.object(factory, "_decorate_function") as mock_decorate:
        mock_decorate.return_value = "decorated"

        factory.decorate_methods(SampleClass)

        # Verify that only the public method was decorated
        mock_decorate.assert_called_once()

        # Check that the method was replaced on the class
        assert hasattr(SampleClass, "public_method")

        # Ensure private methods are untouched
        instance = SampleClass()
        assert instance._private_method() == "private"
