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

import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

from dev_kit_mcp_server.tools.commands.base import _BaseExec

from ...core import tomllib


@dataclass
class PredefinedCommands(_BaseExec):
    """Class to execute predefined commands from pyproject.toml.

    This tool executes predefined commands configured in the pyproject.toml file
    under the [tool.dkmcp.commands] section.
    """

    _commands_config: Dict[str, str] = field(init=False, default_factory=dict)
    _pyproject_exists: bool = field(init=False, default=False)
    commands_toml: Optional[str] = None

    @property
    def _name(self) -> str:
        return "predefined_commands"

    # Class attribute for valid param regex
    VALID_PARAM_REGEX = r"^[a-zA-Z0-9_\-\.\s\/\\:@=,]+$"

    @property
    def docstring(self) -> str:
        """Return a docstring that includes the available commands from pyproject.toml."""
        base_docstring = self.__call__.__doc__ or "No docstring provided"
        cmd_list = sorted(self._commands_config.keys())
        return base_docstring.format(cmd_list)

    def __post_init__(self) -> None:
        """Post-initialization to set the root path and load commands from TOML file."""
        super().__post_init__()

        if self.commands_toml:
            # Use the custom TOML file if provided
            custom_toml_path = Path(self.commands_toml)
            self._pyproject_exists = custom_toml_path.exists()
            if self._pyproject_exists:
                self._load_commands_from_toml(custom_toml_path)
        else:
            # Use the default pyproject.toml file
            self._pyproject_exists = (self._root_path / "pyproject.toml").exists()
            if self._pyproject_exists:
                self._load_commands_from_toml(self._root_path / "pyproject.toml")

    def _load_commands_from_toml(self, toml_path: Path) -> None:
        """Load predefined commands from a TOML file.

        Args:
            toml_path: Path to the TOML file containing command definitions

        """
        try:
            with open(toml_path, "rb") as f:
                toml_data = tomllib.load(f)
            # Get commands from [tool.dkmcp.commands] section
            commands = toml_data.get("tool", {}).get("dkmcp", {}).get("commands", {})
            if commands:
                self._commands_config = commands
        except Exception as e:
            # If there's an error reading the file, just log it and continue with empty commands
            print(f"Error loading commands from {toml_path}: {e}")

    def _repo_init(self) -> None:
        """Initialize the repository."""
        super()._repo_init()

    async def __call__(
        self,
        command: str,
    ) -> Dict[str, Any]:
        """Execute a predefined command. The command string may include parameters after the command name.

           Available commands list: {}.

        Args:
            command: The command to execute, with optional parameters (e.g., 'test', 'test myparam')

        Returns:
            A dictionary containing the execution results for the command

        Raises:
            ValueError: If no command is provided

        """
        result: Dict[str, Any] = {}
        # Split command into command_name and param (if any)
        parts = shlex.split(command)
        if not parts:
            raise ValueError("No command provided")
        command_name = parts[0]
        param = " ".join(parts[1:]) if len(parts) > 1 else None
        await self._exec_commands(command_name, result, param)
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
            toml_file = self.commands_toml or "pyproject.toml"
            result[command_name] = {
                "error": f"'{toml_file}' not found",
                "directory": self._root_path.as_posix(),
            }
            return

        if command_name not in self._commands_config:
            toml_file = self.commands_toml or "pyproject.toml"
            available = list(self._commands_config.keys())
            result[command_name] = {
                "error": f"Command '{command_name}', not found, the available commands are {available}",
            }
            return

        # Get the command string from the configuration
        command_str = self._commands_config[command_name]

        # Split the command string into a list of arguments
        if param is not None:
            # Validate param to prevent command injection
            if not re.match(self.VALID_PARAM_REGEX, param):
                error_msg = f"Parameter '{param}' must follow the regex pattern: {self.VALID_PARAM_REGEX}. "
                result[command_name] = {
                    "error": error_msg,
                    "directory": self._root_path.as_posix(),
                }
                return
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
