from pathlib import Path

import pytest
from fastmcp import Client

from dev_kit_mcp_server.create_server import server_init
from dev_kit_mcp_server.tools import __all__


@pytest.fixture
def fastmcp_server(temp_dir):
    """Fixture to start the FastMCP server."""
    with open(Path(__file__).parent / "Makefile", "r") as f:
        make_content = f.read()
    with open(Path(temp_dir) / "Makefile", "w") as f:
        f.write(make_content)
    server = server_init(root_dir=temp_dir, copilot_mode=False)

    return server


@pytest.mark.asyncio
async def test_tool_functionality(fastmcp_server):
    # Pass the server directly to the Client constructor
    async with Client(fastmcp_server) as client:
        result = await client.list_tools()
        list_tools = [tool.name for tool in result]
        assert len(result) == len(__all__)
        assert "move_dir" in list_tools
        # Find the make command by name
        assert "exec_make_target" in list_tools
        make_cmd = [tool for tool in result if tool.name == "exec_make_target"][0]

        res = await client.call_tool(make_cmd.name, {"commands": ["ls"]})
        text = res[0].text
        assert "ls" in text
        assert "stdout" in text


@pytest.mark.asyncio
async def test_encoding_error(fastmcp_server):
    async with Client(fastmcp_server) as client:
        make_cmd = [tool for tool in await client.list_tools() if tool.name == "exec_make_target"][0]
        res = await client.call_tool(make_cmd.name, {"commands": ["encoding-error"]})
        # Check that the result contains the expected error message
        assert "encoding-error" in res[0].text
        assert "UnicodeDecodeError" not in res[0].text
