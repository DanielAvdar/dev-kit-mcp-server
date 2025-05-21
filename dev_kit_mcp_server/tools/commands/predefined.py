"""Module for executing predefined commands.

This module provides a tool for executing predefined configuration commands, uses by default the
pyproject.toml file to get the configuration commands. section [tool.dkmcp.commands] is used to get the commands.
for example:
[tool.dkmcp.commands]
pytest = "uv run pytest"
make = "make"
check = "uvx pre-commit run --all-files"
doctest = "make doctest"

"""
