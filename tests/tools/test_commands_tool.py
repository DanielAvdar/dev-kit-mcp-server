import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dev_kit_mcp_server.tools import ExecMakeTarget, PredefinedCommands


@pytest.fixture
def mock_subprocess():
    """Mock the subprocess functionality."""
    with patch("dev_kit_mcp_server.tools.commands_tool.asyncio.create_subprocess_shell") as mock_subprocess:
        # Create a mock process
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"command output", b""))
        mock_subprocess.return_value = mock_process
        yield mock_subprocess, mock_process


@pytest.fixture
def exec_make_target(temp_dir):
    """Create an ExecMakeTarget instance with a mocked Makefile."""
    # Create a mock for Path.exists to simulate Makefile existence
    with patch("pathlib.Path.exists", return_value=True):
        tool = ExecMakeTarget(root_dir=temp_dir)
        yield tool


@pytest.mark.asyncio
async def test_exec_make_target_init(temp_dir):
    """Test initialization of ExecMakeTarget."""
    # Test with non-existent directory
    with pytest.raises(Exception, match="Path does not exist"):
        ExecMakeTarget(root_dir="/non/existent/path")

    # Test with existing directory but no Makefile
    with patch("pathlib.Path.exists") as mock_exists:
        # First call is for directory existence check, second is for Makefile check
        mock_exists.side_effect = [True, False]
        tool = ExecMakeTarget(root_dir=temp_dir)
        assert tool._make_file_exists is False

    # Test with existing directory and Makefile
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.side_effect = [True, True]
        tool = ExecMakeTarget(root_dir=temp_dir)
        assert tool._make_file_exists is True
        assert tool.name == "exec_make_target"


@pytest.mark.asyncio
async def test_exec_make_target_call_invalid_input(exec_make_target):
    """Test __call__ method with invalid input."""
    # Test with non-list input
    with pytest.raises(ValueError, match="Expected a list of commands as the argument"):
        await exec_make_target("not_a_list")


@pytest.mark.asyncio
async def test_exec_make_target_no_makefile(temp_dir):
    """Test behavior when Makefile doesn't exist."""
    with patch("pathlib.Path.exists") as mock_exists:
        # First call is for directory existence check, second is for Makefile check
        mock_exists.side_effect = [True, False]
        tool = ExecMakeTarget(root_dir=temp_dir)
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
@pytest.mark.skip(reason="Skipping test which checking old exec_version")
async def test_exec_make_target_successful_execution(exec_make_target, mock_subprocess, temp_dir):
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
        "make check --just-print --quiet",
        cwd=Path(temp_dir).as_posix(),
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

        # Should raise the exception from create_sub_proccess
        with pytest.raises(Exception, match="Command failed"):
            await exec_make_target(["test"])


# PredefinedCommands Tests


@pytest.fixture
def mock_tomllib_load():
    """Mock the tomllib.load function."""
    with patch("tomllib.load") as mock_load:
        mock_load.return_value = {
            "tool": {"dkmcp": {"commands": {"test": "pytest", "lint": "ruff check", "build": "make build"}}}
        }
        yield mock_load


@pytest.fixture
def predefined_commands(mock_tomllib_load, temp_dir):
    """Create a PredefinedCommands instance with mocked pyproject.toml."""
    # Create a mock for Path.exists to simulate pyproject.toml existence
    with patch("pathlib.Path.exists", return_value=True), patch("builtins.open", MagicMock()):
        tool = PredefinedCommands(root_dir=temp_dir)
        yield tool


@pytest.mark.asyncio
async def test_predefined_commands_init(temp_dir):
    """Test initialization of PredefinedCommands."""
    # Test with non-existent directory
    with pytest.raises(Exception, match="Path does not exist"):
        PredefinedCommands(root_dir="/non/existent/path")

    # Test with existing directory but no pyproject.toml
    with patch("pathlib.Path.exists") as mock_exists:
        # First call is for directory existence check, second is for pyproject.toml check
        mock_exists.side_effect = [True, False]
        tool = PredefinedCommands(root_dir=temp_dir)
        assert tool._pyproject_exists is False
        assert tool._commands_config == {}

    # Test with existing directory and pyproject.toml but error loading
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("builtins.open", MagicMock()),
        patch("tomllib.load") as mock_load,
    ):
        mock_exists.side_effect = [True, True]
        mock_load.side_effect = Exception("Error loading file")

        # Should not raise exception, just log error and continue with empty commands
        tool = PredefinedCommands(root_dir=temp_dir)
        assert tool._pyproject_exists is True
        assert tool._commands_config == {}

    # Test with existing directory and valid pyproject.toml
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("builtins.open", MagicMock()),
        patch("tomllib.load") as mock_load,
    ):
        mock_exists.side_effect = [True, True]
        mock_load.return_value = {"tool": {"dkmcp": {"commands": {"test": "pytest", "lint": "ruff check"}}}}

        tool = PredefinedCommands(root_dir=temp_dir)
        assert tool._pyproject_exists is True
        assert tool._commands_config == {"test": "pytest", "lint": "ruff check"}
        assert tool.name == "predefined_commands"


@pytest.mark.asyncio
async def test_predefined_commands_docstring(predefined_commands):
    """Test the docstring property of PredefinedCommands."""
    # The docstring should include the available commands
    docstring = predefined_commands.docstring
    assert ": [" in docstring
    assert "build" in docstring
    assert "lint" in docstring
    assert "test" in docstring

    # Test with empty commands
    with patch.object(predefined_commands, "_commands_config", {}):
        docstring = predefined_commands.docstring
        assert "[]" in docstring


@pytest.mark.asyncio
async def test_predefined_commands_call(predefined_commands):
    """Test the __call__ method of PredefinedCommands."""
    # Mock the _exec_commands method
    with patch.object(predefined_commands, "_exec_commands") as mock_exec:
        # Test with command only
        await predefined_commands("test")
        mock_exec.assert_called_once_with("test", {}, None)
        mock_exec.reset_mock()

        # Test with command and param
        await predefined_commands("test", "specific_test")
        mock_exec.assert_called_once_with("test", {}, "specific_test")


@pytest.mark.asyncio
async def test_predefined_commands_exec_no_pyproject(predefined_commands):
    """Test _exec_commands when pyproject.toml doesn't exist."""
    # Set _pyproject_exists to False
    predefined_commands._pyproject_exists = False

    result = {}
    await predefined_commands._exec_commands("test", result)

    assert "test" in result
    assert "error" in result["test"]
    assert "'pyproject.toml' not found" == result["test"]["error"]


@pytest.mark.asyncio
async def test_predefined_commands_exec_command_not_found(predefined_commands):
    """Test _exec_commands when command is not found in config."""
    result = {}
    await predefined_commands._exec_commands("nonexistent", result)

    assert "nonexistent" in result
    assert "error" in result["nonexistent"]
    assert "Command 'nonexistent' not found in pyproject.toml" == result["nonexistent"]["error"]


@pytest.mark.asyncio
async def test_predefined_commands_exec_success(predefined_commands):
    """Test successful execution of a command."""
    # Mock the create_sub_proccess method
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"command output", b"")
    mock_process.returncode = 0

    with patch.object(predefined_commands, "create_sub_proccess", return_value=mock_process):
        result = {}
        await predefined_commands._exec_commands("test", result)

        assert "test" in result
        assert result["test"]["command"] == "test"
        assert result["test"]["executed"] == "pytest"
        assert result["test"]["stdout"] == "command output"
        assert result["test"]["stderr"] == ""
        assert result["test"]["exitcode"] == 0


@pytest.mark.asyncio
async def test_predefined_commands_exec_with_param(predefined_commands):
    """Test execution of a command with a parameter."""
    # Mock the create_sub_proccess method
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"command output", b"")
    mock_process.returncode = 0

    with patch.object(predefined_commands, "create_sub_proccess", return_value=mock_process):
        result = {}
        await predefined_commands._exec_commands("test", result, "specific_test")

        assert "test" in result
        assert result["test"]["command"] == "test"
        assert result["test"]["executed"] == "pytest specific_test"
        assert result["test"]["stdout"] == "command output"
        assert result["test"]["stderr"] == ""
        assert result["test"]["exitcode"] == 0


@pytest.mark.asyncio
async def test_predefined_commands_exec_subprocess_exception(predefined_commands):
    """Test handling of subprocess creation exception."""
    with patch.object(predefined_commands, "create_sub_proccess", side_effect=Exception("Command failed")):
        result = {}
        await predefined_commands._exec_commands("test", result)

        assert "test" in result
        assert "error" in result["test"]
        assert "Failed to create subprocess: Command failed" == result["test"]["error"]


@pytest.mark.asyncio
async def test_predefined_commands_exec_nonzero_exit(predefined_commands):
    """Test handling of non-zero exit code."""
    # Mock the create_sub_proccess method
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"command output", b"error output")
    mock_process.returncode = 1

    with patch.object(predefined_commands, "create_sub_proccess", return_value=mock_process):
        result = {}
        with pytest.raises(RuntimeError, match="non-zero exitcode: 1"):
            await predefined_commands._exec_commands("test", result)
