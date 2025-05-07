"""Script to run the FastMCP server using uv run."""

# Import the MCP instance from the module
from py_code.fastmcp_server import mcp

if __name__ == "__main__":
    # Run the MCP server with the specified transport
    print("Starting FastMCP server...")
    mcp.run(
        transport="stdio",
    )
