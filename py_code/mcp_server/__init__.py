"""MCP server package for Python code analysis."""


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the MCP server with uvicorn.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    from ..fastmcp_server import start_server as fastmcp_start_server

    fastmcp_start_server(host=host, port=port)
