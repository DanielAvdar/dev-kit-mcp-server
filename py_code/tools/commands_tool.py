import asyncio
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List

from .file_ops import AsyncOperation


@dataclass
class MakeCommandsTool(AsyncOperation):
    """Class to run makefile commands."""

    _make_file_exists: bool = field(init=False, default=False)

    name = "commands_tool"

    def __post_init__(self) -> None:
        """Post-initialization to set the root path."""
        # Set the root path to the current working directory
        super().__post_init__()
        self._make_file_exists = (self._root_path / "Makefile").exists()

    async def __call__(
        self,
        commands: List[str],
    ) -> Dict[str, Any]:
        """Run makefile commands.

        Args:
            commands: List of makefile commands to run (e.g. ["test", "lint"])

        Returns:
            A dictionary containing the command output and status

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
        """Return the self wrapper."""

        async def self_wrapper(
            commands: List[str],
        ) -> Dict[str, Any]:
            """Run makefile commands.

            Args:
                commands: List of makefile commands to run (e.g. ["test", "lint"])

            Returns:
                A dictionary containing the command output and status

            """
            return await self.__call__(commands)

        self_wrapper.__name__ = self.name

        return self_wrapper

    def _read_makefile(self) -> str:
        """Read the Makefile content from the root directory."""
        makefile_path = self._root_path / "Makefile"
        if not makefile_path.exists():
            raise FileNotFoundError(f"Makefile not found at {makefile_path}")
        return makefile_path.read_text()

    async def _exec_commands(self, target: str, commands: List[str], result: Dict[str, Any]) -> None:
        """Execute a makefile command and store the result.

        Args:
            target: The makefile target to execute
            commands: The list of all commands being executed
            result: Dictionary to store the execution results

        """
        if not self._make_file_exists:
            result[target] = {
                "error": f"Makefile not found at {self._root_path.as_posix()}",
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
            for  line in cmd.splitlines():
                process = await self.create_sub_proccess(line)

                stdout, stderr = await process.communicate()

                res = {
                    "command": line,
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
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

    async def create_sub_proccess(self, cmd: str):
        process_get = await asyncio.create_subprocess_shell(
            cmd,
            cwd=self._root_path.as_posix(),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return process_get
