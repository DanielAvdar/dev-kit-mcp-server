"""Tests for the MakeCommandsTool class."""

import tempfile
from pathlib import Path
from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.commands_tool import MakeCommandsTool


@pytest.fixture
def temp_root_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(
    params=[
        "\n",
        "\n\n",
        "\n\n\n",
        "\t",
        "\t\n",
        "\t\n\n",
        "\t\n\n\n",
        "\t\t",
        "\t\t\n",
        "\t\t\n\n",
        "\t\t\n\n\n",
    ]
)
def mock_makefile_content(request: pytest.FixtureRequest) -> tuple[str, Dict[str, Any]]:
    """Return mock Makefile content for testing."""
    noise = request.param
    expected_parsed_content = {
        "install": ["uv", "sync", "--all-extras", "--all-groups", "--frozen"],
        "test": ["uv", "run", "pytest"],
        "check": ["uv", "run", "pre-commit", "run", "--all-files"],
        "coverage": ["uv", "run", "pytest", "--cov=py_code", "--cov-report=xml"],
        "mypy": ["uv", "tool", "run", "mypy", "py_code", "--config-file", "pyproject.toml"],
        "doctest": ["uv", "run", "--no-project", "sphinx-build", "-M", "doctest", "docs/source", "docs/build/"],
    }
    return (
        f"""
.PHONY: help
.PHONY: default
default: install
{noise}
install:
	uv sync --all-extras --all-groups --frozen
	{noise}

	uv tool install pre-commit --with pre-commit-uv --force-reinstall
{noise}

test:
	uv run pytest
{noise}

check:
{noise}

	uv run pre-commit run --all-files
{noise}

coverage:
{noise}

	uv run pytest --cov=py_code --cov-report=xml
{noise}

mypy:
	uv tool run mypy py_code --config-file pyproject.toml

doctest:
	uv run --no-project sphinx-build -M doctest docs/source docs/build/

	{noise}

""",
        expected_parsed_content,
    )


@pytest.fixture
def commands_tool(temp_root_dir: str) -> MakeCommandsTool:
    """Create a MakeCommandsTool instance with a temporary root directory."""
    return MakeCommandsTool(root_dir=temp_root_dir)


@pytest.fixture
def commands_tool_with_makefile(temp_root_dir: str, mock_makefile_content: str) -> MakeCommandsTool:
    """Create a MakeCommandsTool instance with a mock Makefile."""
    # Create a mock Makefile in the temporary directory
    makefile_path = Path(temp_root_dir) / "Makefile"

    # Create mock commands
    makefile_content, expected_parsed_content = mock_makefile_content
    makefile_path.write_text(makefile_content)

    tool = MakeCommandsTool(root_dir=temp_root_dir)
    # Override the _make_shlex_cmds attribute directly

    return tool


def test_parsing(commands_tool_with_makefile, mock_makefile_content: str) -> None:
    commnads_names_tool = commands_tool_with_makefile._make_shlex_cmds.keys()
    commnads_names_expected = mock_makefile_content[1].keys()
    assert set(commnads_names_tool) == set(commnads_names_expected)
    for command in commnads_names_tool:
        assert command in commnads_names_expected
        assert commands_tool_with_makefile._make_shlex_cmds[command] == mock_makefile_content[1][command]


class TestMakeCommandsTool:
    """Tests for MakeCommandsTool."""

    def test_read_makefile(self, temp_root_dir: str, mock_makefile_content: str) -> None:
        """Test reading the Makefile content."""
        # Arrange
        makefile_path = Path(temp_root_dir) / "Makefile"
        makefile_path.write_text(mock_makefile_content)

        # Act
        tool = MakeCommandsTool(root_dir=temp_root_dir)
        content = tool._read_makefile()

        # Assert
        assert content == mock_makefile_content

    def test_read_makefile_not_found(self, temp_root_dir: str) -> None:
        """Test reading a non-existent Makefile."""
        # Arrange - Create a tool with mocked _read_makefile to avoid it being called in __post_init__
        with patch.object(MakeCommandsTool, "_read_makefile", return_value=""):
            tool = MakeCommandsTool(root_dir=temp_root_dir)

        # Remove the patch to test the actual method
        tool._read_makefile = MakeCommandsTool._read_makefile.__get__(tool)

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            tool._read_makefile()

    def test_parse_makefile_commands(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test parsing Makefile commands."""
        # Act
        commands = commands_tool_with_makefile._make_shlex_cmds

        # Assert
        assert "install" in commands
        assert "test" in commands
        assert "check" in commands
        assert "coverage" in commands
        assert "mypy" in commands
        assert "doctest" in commands

        # Check specific commands
        assert commands["test"] == ["uv", "run", "pytest"]
        assert commands["check"] == ["uv", "run", "pre-commit", "run", "--all-files"]

    @pytest.mark.asyncio
    async def test_exec_commands_success(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test executing commands successfully."""
        # Arrange
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Test output"
            mock_result.stderr = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Act
            result: Dict[str, Any] = {}
            await commands_tool_with_makefile._exec_commands("test", ["test"], result)

            # Assert
            assert "test" in result
            assert result["test"]["stdout"] == "Test output"
            assert result["test"]["returncode"] == 0
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_exec_commands_not_found(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test executing a command that doesn't exist in the Makefile."""
        # Arrange
        # Override the _make_shlex_cmds to simulate a missing command
        commands_tool_with_makefile._make_shlex_cmds = {}

        # Act
        result: Dict[str, Any] = {}
        await commands_tool_with_makefile._exec_commands("nonexistent", ["nonexistent"], result)

        # Assert
        assert "nonexistent" in result
        assert "error" in result["nonexistent"]
        assert "not found in Makefile" in result["nonexistent"]["error"]

    @pytest.mark.asyncio
    async def test_exec_commands_exception(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test handling exceptions when executing commands."""
        # Arrange
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test exception")

            # Act
            result: Dict[str, Any] = {}
            await commands_tool_with_makefile._exec_commands("test", ["test"], result)

            # Assert
            assert "test" in result
            assert "error" in result["test"]
            assert "Test exception" in result["test"]["error"]

    @pytest.mark.asyncio
    async def test_call_method(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test the __call__ method."""
        # Arrange
        with patch.object(commands_tool_with_makefile, "_exec_commands") as mock_exec:
            # Act
            result = await commands_tool_with_makefile(["test", "check"])

            # Assert
            assert isinstance(result, dict)
            assert mock_exec.call_count == 2
            mock_exec.assert_any_call("test", ["test", "check"], result)
            mock_exec.assert_any_call("check", ["test", "check"], result)

    def test_self_wrapper(self, commands_tool_with_makefile: MakeCommandsTool) -> None:
        """Test the self_wrapper method."""
        # Act
        wrapper = commands_tool_with_makefile.self_warpper()

        # Assert
        assert callable(wrapper)
        assert wrapper.__name__ == "commands_tool"
