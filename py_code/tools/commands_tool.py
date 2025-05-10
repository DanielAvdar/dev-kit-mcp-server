import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .file_ops import _Operation


@dataclass
class MakeCommandsTool(_Operation):
    """Class to run makefile commands."""

    name = "commands_tool"
    malicious_chars = [
        "&",
        "|",
        ";",
        "`",
        "$",
        "<",
        ">",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "\\",
        '"',
        "'",
        "&&",
        "||",
        ";;",
        "?",
    ]

    def __post_init__(self) -> None:
        """Post-initialization to set the root path."""
        # Set the root path to the current working directory
        super().__post_init__()
        self._make_shlex_cmds: Dict[str, List[str]] = self._parse_makefile_commands()

    async def __call__(
        self,
        commands: List[str],
    ) -> Dict[str, Any]:
        """Run makefile commands. list of commands ['command1', 'command2',...],
            to execute in `make command1 command2 ...`, in root directory of the workspace.
            possible to insert make options in the command list.



        Args:
            commands: (List) of makefile commands to run (e.g. ["test", "lint"])


        Returns:
            A dictionary containing the command output and status

        """
        # make_cmd:Dict[str, List[str]] = {}
        result: Dict[str, Any] = {}
        for cmd in commands:
            shlex_cmd = self._make_shlex_cmds.get(cmd)

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
                    "error": f"Error running makefile commands: {str(e)}",
                    "command": shlex_cmd,
                    "commands": commands,
                }

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper."""

        async def self_wrapper(
            commands: List[str],
        ) -> Dict[str, Any]:
            """Run makefile commands."""
            return await self.__call__(commands)

        self_wrapper.__name__ = self.name

        return self_wrapper
