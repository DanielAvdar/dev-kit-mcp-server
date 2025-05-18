import asyncio
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_stdio_server():
    # Create a new ClientSession with the StdioServerParameters
    params = StdioServerParameters(command="uvx", args=["dev-kit-mcp-server --directory .."])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write):
            print("inside ClientSession")
            # await c.initialize()


@pytest.mark.asyncio
async def test_stdio():
    root = Path(__file__).parent.parent
    process_get = await asyncio.create_subprocess_exec(
        *["make", "check"],
        cwd=root.as_posix(),
        # stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        # capture_output=True,
        # text=True,
        # check=True,
        # creationflags= asyncio.su.CREATE_NO_WINDOW,
    )
    stdout, stderr = await process_get.communicate()
    {
        "command": ["make", "check"],
        "stdout": stdout.decode(errors="replace"),
        "stderr": stderr.decode(errors="replace"),
        "cwd": root.as_posix(),
    }
