import os
import subprocess
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import Context


def authorized_commands(
    commands: List[str], makefile_dir: Optional[str] = None, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Run authorized makefile commands.

    Args:
        commands: List of makefile commands to run (e.g. ["test", "lint"])
        makefile_dir: Optional directory containing the Makefile (defaults to current working directory)
        ctx: Optional context for logging

    Returns:
        A dictionary containing the command output and status

    """
    if ctx:
        ctx.info(f"Running makefile commands: {commands}")

    # Set default makefile directory if not provided
    workspace_root = os.getcwd()
    if makefile_dir is None:
        makefile_dir = workspace_root
    elif not os.path.isabs(makefile_dir):
        makefile_dir = os.path.join(workspace_root, makefile_dir)

    # Normalize path
    makefile_dir = os.path.normpath(makefile_dir)

    # Verify makefile directory is within the working directory
    if not makefile_dir.startswith(workspace_root):
        return {
            "error": f"Makefile directory must be within the working directory: {makefile_dir}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }

    # Validate makefile exists
    makefile_path = os.path.join(makefile_dir, "Makefile")
    if not os.path.exists(makefile_path):
        return {
            "error": f"Makefile not found at {makefile_path}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }

    # Construct the make command
    make_cmd = ["make", "-C", makefile_dir] + commands

    try:
        # Run the command and capture output
        result = subprocess.run(
            make_cmd,
            capture_output=True,
            text=True,
            check=False,  # Don't raise an exception on non-zero exit code
        )

        return {
            "success": result.returncode == 0,
            "commands": commands,
            "makefile_dir": makefile_dir,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {
            "error": f"Error running makefile commands: {str(e)}",
            "commands": commands,
            "makefile_dir": makefile_dir,
        }
