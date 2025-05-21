import argparse
import json
import os
from pathlib import Path

confs = {
    "servers": {
        "dev-kit-mcp-server": {
            "command": "uvx",
            "args": ["-n", "dev-kit-mcp-server", "--root-dir", "${workspaceFolder}"],
            "env": {},
        }
    }
}


def create_vscode_config() -> None:
    """Create a VS Code configuration file for the MCP server."""
    parser = argparse.ArgumentParser(description="Start the FastMCP server")
    parser.add_argument(
        "--root-dir",
        type=str,
        default=os.getcwd(),
        help="Root directory for file operations (default: current working directory)",
    )
    args = parser.parse_args()
    work_folder = Path(args.root_dir)
    path_vs = Path(work_folder / ".vscode")
    path = path_vs / "mcp.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            file.write(json.dumps(confs, indent=4))
        print(f"Created new MCP configuration at {path}")

    with open(path, "r") as file:
        # file_dict = json.loads(file.read())
        content = file.read()
        file_dict = {}
        if content:
            file_dict = json.loads(content)

    if "servers" not in file_dict:
        file_dict["servers"] = {}
    file_dict["servers"]["dev-kit-mcp-server"] = confs["servers"]["dev-kit-mcp-server"]
    with open(path, "w") as file:
        file.write(json.dumps(file_dict, indent=4))
