"""Module for executing Makefile targets.

This module provides a tool for executing Makefile targets by running the commands
that make would run for the specified targets.
"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .file_ops import AsyncOperation


@dataclass
class ExecMakeTarget(AsyncOperation):
    """Class to execute Makefile targets.

    This tool executes Makefile targets by running the commands that make would run
    for the specified targets.
    """

    _make_file_exists: bool = field(init=False, default=False)

    name = "exec_make_target"

    def __post_init__(self) -> None:
        """Post-initialization to set the root path."""
        # Set the root path to the current working directory
        super().__post_init__()
        self._make_file_exists = (self._root_path / "Makefile").exists()

    async def __call__(
        self,
        commands: List[str],
    ) -> Dict[str, Any]:
        """Execute Makefile targets.

        Args:
            commands: List of Makefile targets to execute (e.g. ["test", "lint"])

        Returns:
            A dictionary containing the execution results for each target

        Raises:
            ValueError: If commands is not a list

        """
        if not isinstance(commands, list):
            raise ValueError("Expected a list of commands as the argument")
        result: Dict[str, Any] = {}
        for cmd in commands:
            await self._exec_commands(cmd, commands, result)
        return result

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        async def self_wrapper(
            commands: List[str],
        ) -> Dict[str, Any]:
            """Execute Makefile targets.

            Args:
                commands: List of Makefile targets to execute (e.g. ["test", "lint"])

            Returns:
                A dictionary containing the execution results for each target

            """
            return await self.__call__(commands)

        self_wrapper.__name__ = self.name

        return self_wrapper

    async def _exec_commands(self, target: str, commands: List[str], result: Dict[str, Any]) -> None:
        """Execute a Makefile target and store the result.

        Args:
            target: The Makefile target to execute
            commands: The list of all targets being executed
            result: Dictionary to store the execution results

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
                "commands": commands,
            }
            return

        try:
            result[target] = []
            process_get = await self.create_sub_proccess(f"make {target} --just-print --quiet")
            stdout, stderr = await process_get.communicate()
            cmd = stdout.decode()
            for line in cmd.splitlines():
                process = await self.create_sub_proccess(line)

                stdout, stderr = await process.communicate()

                res = {
                    "command": line,
                    "stdout": stdout.decode(errors="replace"),
                    "stderr": stderr.decode(errors="replace"),
                    "cwd": self._root_path.as_posix(),
                }
                result[target].append(res)
        except Exception as e:
            result[target] = {
                "error": f"Error running makefile command: {str(e)}",
                "make-target": target,
                "commands": commands,
                "cwd": self._root_path.as_posix(),
            }

    async def create_sub_proccess(self, cmd: str) -> asyncio.subprocess.Process:
        """Create a subprocess to execute a shell command.

        Args:
            cmd: The shell command to execute

        Returns:
            A subprocess object with stdout and stderr pipes

        """
        process_get = await asyncio.create_subprocess_shell(
            cmd,
            cwd=self._root_path.as_posix(),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return process_get
