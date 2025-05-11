Usage
=====

This section provides information on how to use the Dev-Kit MCP Server.

Command-Line Arguments
-----------------------

The server supports the following command-line arguments:

.. code-block:: bash

   python -m dev_kit_mcp_server.mcp_server [--root-dir ROOT_DIR]

Arguments:

* ``--root-dir ROOT_DIR``: Specifies the root directory for file operations. This is the directory that file operations will be restricted to for security reasons. If not specified, the current working directory is used.

Example:

.. code-block:: bash

   python -m dev_kit_mcp_server.mcp_server --root-dir C:\path\to\project

File Operations
----------------

The server provides several tools for file operations:

Create Directory
~~~~~~~~~~~~~~~~

Creates a directory at the specified path.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("create_dir_or_file", {"path": "path/to/new/directory"})

The operation will fail if:

* The path is outside the root directory
* The path already exists

Move File or Directory
~~~~~~~~~~~~~~~~~~~~~~

Moves a file or directory from one path to another.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("move_dir_or_file", {"path1": "path/to/source", "path2": "path/to/destination"})

The operation will fail if:

* Either path is outside the root directory
* The source path does not exist
* The destination path already exists

Remove File or Directory
~~~~~~~~~~~~~~~~~~~~~~~~

Removes a file or directory at the specified path.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("remove_dir_or_file", {"path": "path/to/remove"})

The operation will fail if:

* The path is outside the root directory
* The path does not exist

Security Considerations
------------------------

All file operations are restricted to the specified root directory for security reasons. Any attempt to perform operations outside this directory will fail with an error message.
