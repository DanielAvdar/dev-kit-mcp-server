"""Command-line interface for running the MCP server."""

import sys

from dev_kit_mcp_server.create_server import arg_parse


def main() -> None:
    """Parse command line arguments and start the server."""
    # parser = argparse.ArgumentParser(
    #     description="Dev-Kit MCP Server",
    #     epilog="Provides tools for file operations and running makefile commands",
    # )
    # parser.add_argument(
    #     "--root-dir", type=str, help="Root directory for file operations (defaults to current directory)"
    # )

    args = arg_parse()

    print("Starting Dev-Kit MCP Server")
    print(f"Root directory: {args.root_dir}")

    try:
        # Override sys.argv to pass the root_dir to start_server
        # This is needed because start_server uses argparse internally
        sys.argv = [sys.argv[0]]
        if args.root_dir:
            sys.argv.extend(["--root-dir", args.root_dir])

        from .fastmcp_server import start_server

        # Get the server instance
        fastmcp = start_server()

        # Run the server
        fastmcp.run()
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
