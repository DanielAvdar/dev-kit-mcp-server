"""Script to run the FastMCP server using uv run."""

# Import the MCP instance from the module
from dev_kit_mcp_server.fastmcp_server import start_server

fastmcp = start_server()
mcp = fastmcp

if __name__ == "__main__":
    fastmcp.run()
