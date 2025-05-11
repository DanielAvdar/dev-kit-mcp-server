import asyncio
import os
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from py_code.tools.commands_tool import ExecMakeTarget


@pytest.fixture
def mock_subprocess():
    """Mock the subprocess functionality."""
    with patch("py_code.tools.commands_tool.asyncio.create_subprocess_shell") as mock_subprocess:
        # Create a mock process
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"command output", b""))
        mock_subprocess.return_value = mock_process
        yield mock_subprocess, mock_process


@pytest.fixture
def exec_make_target():
    """Create an ExecMakeTarget instance with a mocked Makefile."""
    # Use the current directory as the root directory
    root_dir = os.getcwd()

    # Create a mock for Path.exists to simulate Makefile existence
    with patch("pathlib.Path.exists", return_value=True):
        tool = ExecMakeTarget(root_dir=root_dir)
        yield tool


@pytest.mark.asyncio
async def test_exec_make_target_init():
    """Test initialization of ExecMakeTarget."""
    # Test with non-existent directory
    with pytest.raises(Exception, match="Path does not exist"):
        ExecMakeTarget(root_dir="/non/existent/path")

    # Test with existing directory but no Makefile
    with patch("pathlib.Path.exists") as mock_exists:
        # First call is for directory existence check, second is for Makefile check
        mock_exists.side_effect = [True, False]
        tool = ExecMakeTarget(root_dir=os.getcwd())
        assert tool._make_file_exists is False

    # Test with existing directory and Makefile
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.side_effect = [True, True]
        tool = ExecMakeTarget(root_dir=os.getcwd())
        assert tool._make_file_exists is True
        assert tool.name == "exec_make_target"


@pytest.mark.asyncio
async def test_exec_make_target_call_invalid_input(exec_make_target):
    """Test __call__ method with invalid input."""
    # Test with non-list input
    with pytest.raises(ValueError, match="Expected a list of commands as the argument"):
        await exec_make_target("not_a_list")


@pytest.mark.asyncio
async def test_exec_make_target_no_makefile():
    """Test behavior when Makefile doesn't exist."""
    with patch("pathlib.Path.exists") as mock_exists:
        # First call is for directory existence check, second is for Makefile check
        mock_exists.side_effect = [True, False]
        tool = ExecMakeTarget(root_dir=os.getcwd())
        result = await tool(["test"])
        assert "error" in result["test"]
        assert "'Makefile' not found" == result["test"]["error"]


@pytest.mark.asyncio
async def test_exec_make_target_invalid_target(exec_make_target):
    """Test behavior with invalid target name."""
    # Test with invalid target name
    result = await exec_make_target(["invalid;command"])
    assert "error" in result["invalid;command"]
    assert "Target 'invalid;command' is invalid." == result["invalid;command"]["error"]


@pytest.mark.asyncio
async def test_exec_make_target_successful_execution(exec_make_target, mock_subprocess):
    """Test successful execution of a Makefile target."""
    mock_subprocess_shell, mock_process = mock_subprocess

    # Mock the first subprocess call to return make commands
    mock_process.communicate.side_effect = [
        (b"echo 'Running test'\npython -m pytest", b""),  # make --just-print output
        (b"Running test", b""),  # echo command output
        (b"All tests passed", b""),  # pytest command output
    ]

    result = await exec_make_target(["test"])

    # Check that the subprocess was called correctly
    assert mock_subprocess_shell.call_count == 3
    mock_subprocess_shell.assert_any_call(
        "make test --just-print --quiet",
        cwd=Path(os.getcwd()).as_posix(),
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Check the result structure
    assert "test" in result
    assert isinstance(result["test"], list)
    assert len(result["test"]) == 2

    # Check first command result
    assert result["test"][0]["command"] == "echo 'Running test'"
    assert result["test"][0]["stdout"] == "Running test"
    assert result["test"][0]["stderr"] == ""

    # Check second command result
    assert result["test"][1]["command"] == "python -m pytest"
    assert result["test"][1]["stdout"] == "All tests passed"
    assert result["test"][1]["stderr"] == ""


@pytest.mark.asyncio
async def test_exec_make_target_exception_handling(exec_make_target):
    """Test exception handling during execution."""
    with patch.object(exec_make_target, "create_sub_proccess") as mock_create_subprocess:
        mock_create_subprocess.side_effect = Exception("Command failed")

        result = await exec_make_target(["test"])

        assert "error" in result["test"]
        assert "Error running makefile command: Command failed" == result["test"]["error"]
        assert result["test"]["make-target"] == "test"


@pytest.mark.asyncio
async def test_self_wrapper(exec_make_target):
    """Test the self_wrapper method."""
    # Mock the __call__ method
    exec_make_target.__call__ = AsyncMock(return_value={"test": "result"})

    # Get the wrapper function
    wrapper = exec_make_target.self_warpper()

    # Check the wrapper name
    assert wrapper.__name__ == "exec_make_target"

    # Call the wrapper
    result = await wrapper(["test"])

    # Check that __call__ was called with the right arguments
    exec_make_target.__call__.assert_called_once_with(["test"])

    # Check the result
    assert result == {"test": "result"}
