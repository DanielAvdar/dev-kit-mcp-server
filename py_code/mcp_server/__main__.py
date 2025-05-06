"""Main entry point for the MCP server command-line interface."""

import argparse
import socket
import sys


def find_available_port(start_port: int, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port.

    Args:
        start_port: The port to start checking from
        max_attempts: Maximum number of ports to check

    Returns:
        An available port or raises RuntimeError if none is found

    Raises:
        RuntimeError: If no available ports are found

    """
    ports_to_try = list(range(start_port, start_port + max_attempts))

    for port in ports_to_try:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue

    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")


def main() -> None:
    """Entry point for the package."""
    parser = argparse.ArgumentParser(description="Python Code MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the server to (default: 8000)")
    parser.add_argument(
        "--auto-port", action="store_true", help="Automatically find an available port if specified port is in use"
    )

    args = parser.parse_args()

    port = args.port
    if args.auto_port:
        try:
            port = find_available_port(port)
            print(f"Port {args.port} is in use, using port {port} instead")
        except RuntimeError as e:
            print(f"Error: {e}")
            sys.exit(1)

    print(f"Starting Python Code MCP Server on {args.host}:{port}")

    try:
        # Using the integrated server to get both FastAPI and MCP features
        from py_code.integrated_server import run_server

        run_server(host=args.host, port=port)
    except OSError as e:
        if "address already in use" in str(e).lower() or "only one usage of each socket address" in str(e).lower():
            print(f"Error: Port {port} is already in use. Try with --auto-port option or specify a different port.")
        else:
            print(f"Error starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
