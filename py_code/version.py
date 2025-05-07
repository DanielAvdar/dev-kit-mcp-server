"""Version information for py-code-mcp-server."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("py-code-mcp-server")
except PackageNotFoundError:
    # Package is not installed, set a default version
    __version__ = "0.1.0"

# Export the version explicitly to ensure coverage
try:
    VERSION = version("py-code-mcp-server")
except PackageNotFoundError:
    # Use the default version if the package is not installed
    VERSION = __version__
