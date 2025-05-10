"""Tests for the authorized_commands tool."""

from unittest.mock import MagicMock, patch

from py_code.tools.commands_tool import authorized_commands


def test_authorized_commands_success():
    """Test running authorized commands successfully."""
    mock_ctx = MagicMock()
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Test output"
    mock_result.stderr = ""

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("subprocess.run", return_value=mock_result),
    ):
        result = authorized_commands(["test", "lint"], makefile_dir="/fake/path/custom", ctx=mock_ctx)

        # Check that the context info method was called
        mock_ctx.info.assert_called_once()
        assert "Running makefile commands" in mock_ctx.info.call_args[0][0]

        # Check the result
        assert result["success"] is True
        assert result["commands"] == ["test", "lint"]
        assert result["makefile_dir"] == "/fake/path/custom"
        assert result["stdout"] == "Test output"
        assert result["stderr"] == ""
        assert result["returncode"] == 0


def test_authorized_commands_with_makefile_dir():
    """Test running authorized commands with a specified makefile directory."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Test output"
    mock_result.stderr = ""

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("subprocess.run", return_value=mock_result),
    ):
        result = authorized_commands(["test"], makefile_dir="/fake/path/custom")

        # Check the result
        assert result["success"] is True
        assert result["commands"] == ["test"]
        assert result["makefile_dir"] == "/fake/path/custom"


def test_authorized_commands_makefile_dir_outside_working_dir():
    """Test error handling when makefile directory is outside working directory."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
    ):
        result = authorized_commands(["test"], makefile_dir="/outside/path")

        # Check the result
        assert "error" in result
        assert "Makefile directory must be within the working directory" in result["error"]
        assert result["commands"] == ["test"]
        assert result["makefile_dir"] == "/outside/path"


def test_authorized_commands_makefile_not_found():
    """Test error handling when Makefile is not found."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
        patch("os.path.exists", return_value=False),
    ):
        result = authorized_commands(["test"])

        # Check the result
        assert "error" in result
        assert "Makefile not found" in result["error"]
        assert result["commands"] == ["test"]


def test_authorized_commands_failure():
    """Test handling command execution failure."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Error: Test failed"

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("subprocess.run", return_value=mock_result),
    ):
        result = authorized_commands(["test"], makefile_dir="/fake/path/subdir")

        # Check the result
        assert result["success"] is False
        assert result["commands"] == ["test"]
        assert result["makefile_dir"] == "/fake/path/subdir"
        assert result["stderr"] == "Error: Test failed"
        assert result["returncode"] == 1


def test_authorized_commands_exception():
    """Test handling exceptions during command execution."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.path.isabs", return_value=True),
        patch("os.path.normpath", side_effect=lambda x: x),
        patch("os.path.exists", return_value=True),
        patch("subprocess.run", side_effect=Exception("Test error")),
    ):
        result = authorized_commands(["test"], makefile_dir="/fake/path/subdir")

        # Check the result
        assert "error" in result
        assert "Error running makefile commands" in result["error"]
        assert "Test error" in result["error"]
        assert result["commands"] == ["test"]
        assert result["makefile_dir"] == "/fake/path/subdir"
