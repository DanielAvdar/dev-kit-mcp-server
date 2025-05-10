"""Command-line interface for running the MCP server."""

import argparse
import os
import sys


def main() -> None:
    """Parse command line arguments and start the server."""
    parser = argparse.ArgumentParser(
        description="Python Code MCP Server",
        epilog="Provides tools for file operations and running makefile commands",
    )
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to (default: 8000)")
    parser.add_argument(
        "--working-dir", type=str, help="Root directory for the server operations (defaults to current directory)"
    )

    args = parser.parse_args()

    # Set default working directory if not provided
    if args.working_dir is None:
        args.working_dir = os.getcwd()
        print(f"No working directory specified, using current directory: {args.working_dir}")

    # Validate working directory
    if not os.path.isdir(args.working_dir):
        print(f"Error: Working directory '{args.working_dir}' does not exist or is not a directory")
        sys.exit(1)

    print(f"Starting Python Code MCP Server on {args.host}:{args.port}")
    print(f"Working directory: {args.working_dir}")

    try:
        from .fastmcp_server import start_server

        start_server(host=args.host, port=args.port, working_dir=args.working_dir)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
