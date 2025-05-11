.. Dev-Kit MCP Server documentation master file

Dev-Kit MCP Server
===================

A Model Context Protocol (MCP) server targeted for agent development tools, providing scoped authorized operations in the root project directory.

This package enables secure execution of operations such as running makefile commands, moving and deleting files, with future plans to include more tools for code editing.
It serves as an excellent MCP server for VS-Code copilot and other AI-assisted development tools.

Features
--------

- **Secure Operations**: Execute operations within a scoped, authorized root directory
- **Makefile Command Execution**: Run makefile commands securely within the project
- **File Operations**: Move, create, and delete files within the authorized directory
- **MCP Integration**: Turn any codebase into an MCP-compliant system
- **AI-Assisted Development**: Excellent integration with VS-Code copilot and other AI tools
- **Extensible Framework**: Easily add new tools for code editing and other operations
- **Fast Performance**: Built with FastMCP for high performance


Installation
------------

.. code-block:: bash

   pip install dev-kit-mcp-server

Quick Start
-----------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   api
