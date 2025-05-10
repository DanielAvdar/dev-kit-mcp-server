from pathlib import Path

import pytest
from fastmcp import Client

from py_code import start_server


@pytest.fixture
def fastmcp_server():
    server = start_server(Path(__file__).parent)

    return server


@pytest.mark.asyncio
async def test_tool_functionality_2(fastmcp_server):
    # Pass the server directly to the Client constructor
    async with Client(fastmcp_server) as client:
        result = await client.list_tools()
        assert len(result) == 4
        assert "move_dir_tool" in str(result[0].name)
