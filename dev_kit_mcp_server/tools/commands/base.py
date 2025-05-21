"""Module for executing Makefile targets.

This module provides a tool for executing Makefile targets by running the commands
that make would run for the specified targets.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List

from dev_kit_mcp_server.core import AsyncOperation


@dataclass
class _BaseExec(AsyncOperation):
    async def _exec_commands(self, target: str, result: Dict[str, Any]) -> None: ...

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
