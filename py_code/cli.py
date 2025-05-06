"""Command-line interface for running the MCP server."""

import argparse
import sys


def main() -> None:
    """Parse command line arguments and start the server."""
    parser = argparse.ArgumentParser(
        description="Python Code MCP Server",
        epilog="Recommended usage: uv run python -m py_code.mcp_server",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to (default: 8000)")
    parser.add_argument(
        "--server-type",
        type=str,
        choices=["mcp"],
        default="mcp",
        help="Type of server to run (default: mcp)",
    )

    args = parser.parse_args()

    print(f"Starting Python Code MCP Server on {args.host}:{args.port}")
    print("Note: For best performance, use: uv run python -m py_code.mcp_server")

    try:
        from .mcp_server import start_server

        start_server(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
