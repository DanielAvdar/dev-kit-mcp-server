"""Module for executing Makefile targets.

This module provides a tool for executing Makefile targets by running the commands
that make would run for the specified targets.
"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List

from dev_kit_mcp_server.tools.commands.base import _BaseExec


@dataclass
class ExecMakeTarget(_BaseExec):
    """Class to execute Makefile targets.

    This tool executes Makefile targets by running the commands that make would run
    for the specified targets.
    """

    _make_file_exists: bool = field(init=False, default=False)

    _name = "exec_make_target"

    def __post_init__(self) -> None:
        """Post-initialization to set the root path."""
        # Set the root path to the current working directory
        super().__post_init__()
        self._make_file_exists = (self._root_path / "Makefile").exists()

    def _repo_init(self) -> None: ...
    async def __call__(
        self,
        commands: List[str],
    ) -> Dict[str, Any]:
        """Execute Makefile targets.

        Args:
            commands: List of Makefile targets to execute

        Returns:
            A dictionary containing the execution results for each target

        Raises:
            ValueError: If commands is not a list

        """
        # Handle both model and direct list input for backward compatibility
        if not isinstance(commands, list):
            raise ValueError("Expected a list of commands as the argument")

        result: Dict[str, Any] = {}

        for cmd in commands:
            await self._exec_commands(cmd, result)
        return result

    async def _exec_commands(self, target: str, result: Dict[str, Any]) -> None:
        """Execute a Makefile target and store the result.

        Args:
            target: The Makefile target to execute
            commands: The list of all targets being executed
            result: Dictionary to store the execution results

        Raises:
            RuntimeError: If the make command returns a non-zero exit code

        """
        if not self._make_file_exists:
            result[target] = {
                "error": "'Makefile' not found",
                "directory": self._root_path.as_posix(),
            }
            return
        valid_cmd_regex = r"^[a-zA-Z0-9_-]+$"

        if not re.match(valid_cmd_regex, target):
            result[target] = {
                "error": f"Target '{target}' is invalid.",
            }
            return

        line = ["make", target, "--quiet"]
        process = await self.create_sub_proccess(line)

        stdout, stderr = await process.communicate()

        res = {
            "target": target,
            "stdout": stdout.decode(errors="replace"),
            "stderr": stderr.decode(errors="replace"),
            "exitcode": process.returncode,
            "cwd": self._root_path.as_posix(),
        }
        if process.returncode != 0:
            raise RuntimeError(f"non-zero exitcode: {process.returncode}. details: {res}")

        result[target] = res

    async def create_sub_proccess(self, cmd: List[str]) -> asyncio.subprocess.Process:
        """Create a subprocess to execute a shell command.

        Args:
            cmd: The shell command to execute as a list of strings

        Returns:
            A subprocess object with stdout and stderr pipes

        """
        process_get = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self._root_path.as_posix(),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return process_get
