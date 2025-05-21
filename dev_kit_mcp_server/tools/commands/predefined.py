"""Module for executing predefined commands.

This module provides a tool for executing predefined configuration commands, uses by default the
pyproject.toml file to get the configuration commands. section [tool.dkmcp.commands] is used to get the commands.
for example:
[tool.dkmcp.commands]
pytest = "uv run pytest"
make = "make"
check = "uvx pre-commit run --all-files"
doctest = "make doctest"

"""

import shlex
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import tomllib

from dev_kit_mcp_server.tools.commands.base import _BaseExec


@dataclass
class PredefinedCommands(_BaseExec):
    """Class to execute predefined commands from pyproject.toml.

    This tool executes predefined commands configured in the pyproject.toml file
    under the [tool.dkmcp.commands] section.
    """

    _commands_config: Dict[str, str] = field(init=False, default_factory=dict)
    _pyproject_exists: bool = field(init=False, default=False)

    name = "predefined_commands"

    def __post_init__(self) -> None:
        """Post-initialization to set the root path and load commands from pyproject.toml."""
        super().__post_init__()
        self._pyproject_exists = (self._root_path / "pyproject.toml").exists()
        if self._pyproject_exists:
            self._load_commands_from_pyproject()

    def _load_commands_from_pyproject(self) -> None:
        """Load predefined commands from pyproject.toml file."""
        pyproject_path = self._root_path / "pyproject.toml"
        try:
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
            # Get commands from [tool.dkmcp.commands] section
            commands = pyproject_data.get("tool", {}).get("dkmcp", {}).get("commands", {})
            if commands:
                self._commands_config = commands
        except Exception as e:
            # If there's an error reading the file, just log it and continue with empty commands
            print(f"Error loading commands from pyproject.toml: {e}")

    def _repo_init(self) -> None:
        """Initialize the repository."""
        super()._repo_init()

    async def __call__(
        self,
        command: str,
        param: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a predefined command with an optional parameter.

        Args:
            command: The name of the predefined command to execute
            param: Optional parameter to append to the command

        Returns:
            A dictionary containing the execution results for the command

        """
        result: Dict[str, Any] = {}
        await self._exec_commands(command, result, param)
        return result

    async def _exec_commands(self, command_name: str, result: Dict[str, Any], param: Optional[str] = None) -> None:
        """Execute a predefined command and store the result.

        Args:
            command_name: The name of the predefined command to execute
            result: Dictionary to store the execution results
            param: Optional parameter to append to the command

        Raises:
            RuntimeError: If the command returns a non-zero exit code

        """
        if not self._pyproject_exists:
            result[command_name] = {
                "error": "'pyproject.toml' not found",
                "directory": self._root_path.as_posix(),
            }
            return

        if command_name not in self._commands_config:
            result[command_name] = {
                "error": f"Command '{command_name}' not found in pyproject.toml",
            }
            return

        # Get the command string from the configuration
        command_str = self._commands_config[command_name]

        # Split the command string into a list of arguments
        if param is not None:
            # Update the command string to include the param for reporting
            command_str = f"{command_str} {param}"
        cmd_args = shlex.split(command_str)
        try:
            process = await self.create_sub_proccess(cmd_args)
            stdout, stderr = await process.communicate()

        except Exception as e:
            result[command_name] = {
                "error": f"Failed to create subprocess: {e}",
                "directory": self._root_path.as_posix(),
                "command_str": command_str,
                "command": cmd_args,
            }
            return

        res = {
            "command": command_name,
            "executed": command_str,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
            "exitcode": process.returncode,
            "cwd": self._root_path.as_posix(),
        }

        if process.returncode != 0:
            raise RuntimeError(f"non-zero exitcode: {process.returncode}. details: {res}")

        result[command_name] = res
