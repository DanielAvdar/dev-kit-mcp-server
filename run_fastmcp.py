"""Script to run the FastMCP server using uv run."""

# Import the MCP instance from the module
from py_code.fastmcp_server import run_server, start_server

mcp = start_server()
if __name__ == "__main__":
    # Run the MCP server with the specified transport
    run_server(
        mcp,
    )
