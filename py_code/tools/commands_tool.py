import re
import shlex
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .file_ops import AsyncOperation


@dataclass
class MakeCommandsTool(AsyncOperation):
    """Class to run makefile commands."""

    name = "commands_tool"

    def __post_init__(self) -> None:
        """Post-initialization to set the root path."""
        # Set the root path to the current working directory
        super().__post_init__()

        # Initialize with empty commands dictionary
        self._make_shlex_cmds: Dict[str, List[str]] = {}

        # Try to parse Makefile commands, but don't fail if Makefile doesn't exist
        try:
            self._make_shlex_cmds = self._parse_makefile_commands()
        except FileNotFoundError:
            # If Makefile doesn't exist, just use empty commands dictionary
            pass

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

    def _parse_makefile_commands(self) -> Dict[str, List[str]]:
        """Parse the Makefile content to extract commands for each target.

        Returns:
            A dictionary mapping target names to lists of command arguments.

        """
        makefile_content = self._read_makefile()
        makefile_lines = makefile_content.splitlines()

        commands: Dict[str, List[str]] = {}
        current_target = None
        cmd_que = []
        for line in makefile_lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Check if this is a target definition
            target_match = re.match(r"^([a-zA-Z0-9_-]+):", line)
            if target_match:
                current_target = target_match.group(1)
                # Initialize the target with an empty list if it doesn't exist
                if current_target not in commands:
                    commands[current_target] = []
                    cmd_que.append(current_target)
                continue

            # If we have a current target and this line is indented (a command)
            if current_target and line.startswith("\t"):
                # Remove the tab and sanitize the command
                cmd = line[1:].strip()

                # Skip empty commands
                if not cmd:
                    continue

                # No need to check for malicious characters anymore

                # Parse the command using shlex to handle quotes correctly
                try:
                    cmd_args = shlex.split(cmd)
                    # Use the first command as the representative command for this target
                    if not commands[current_target]:
                        commands[current_target] = cmd_args
                except ValueError:
                    # Skip commands that can't be parsed
                    continue

        return commands

    async def _exec_commands(self, cmd: str, commands: List[str], result: Dict[str, Any]) -> None:
        """Execute a makefile command and store the result.

        Args:
            cmd: The makefile target to execute
            commands: The list of all commands being executed
            result: Dictionary to store the execution results

        """
        shlex_cmd = self._make_shlex_cmds.get(cmd)

        if not shlex_cmd:
            result[cmd] = {
                "error": f"Command '{cmd}' not found in Makefile",
                "commands": commands,
            }
            return

        try:
            # Run the command and capture output
            shlex_result = subprocess.run(
                shlex_cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise an exception on non-zero exit code
            )

            result[cmd] = {
                "command": shlex_cmd,
                "stdout": shlex_result.stdout,
                "stderr": shlex_result.stderr,
                "returncode": shlex_result.returncode,
            }
        except Exception as e:
            result[cmd] = {
                "error": f"Error running makefile command '{cmd}': {str(e)}",
                "command": shlex_cmd,
                "commands": commands,
            }
