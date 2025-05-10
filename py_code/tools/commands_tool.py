import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .file_ops import FileOperation


@dataclass
class MakeCommandsTool(FileOperation):
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

    def __call__(
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
        for c in commands:
            # Check for malicious characters
            if any(char in c for char in self.malicious_chars):
                return {
                    "error": f"For complex commands please use the Terminal.{c} is not allowed.",
                    "commands": commands,
                }
        make_cmd = [
            "make",
        ] + commands

        try:
            # Run the command and capture output
            result = subprocess.run(
                make_cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise an exception on non-zero exit code
            )

            return {
                "command": make_cmd,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {
                "error": f"Error running makefile commands: {str(e)}",
                "commands": commands,
            }

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper."""

        def self_wrapper(
            commands: List[str],
        ) -> Dict[str, Any]:
            """Run makefile commands."""
            return self.__call__(commands)

        self_wrapper.__name__ = self.name

        return self_wrapper
