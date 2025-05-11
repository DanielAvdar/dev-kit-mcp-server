from pathlib import Path

import pytest
from fastmcp import Client

from dev_kit_mcp_server import start_server


@pytest.fixture
def fastmcp_server():
    server = start_server(Path(__file__).parent.as_posix())

    return server


@pytest.mark.asyncio
async def test_tool_functionality(fastmcp_server):
    # Pass the server directly to the Client constructor
    async with Client(fastmcp_server) as client:
        result = await client.list_tools()
        assert len(result) == 4
        assert "move_dir" in str(result[0].name)
        make_cmd = result[-1]
        assert make_cmd.name == "exec_make_target"
        res = await client.call_tool(make_cmd.name, dict(commands=["ls"]))
        text = res[0].text
        assert "command is successful" in text
        assert "stdout" in text
