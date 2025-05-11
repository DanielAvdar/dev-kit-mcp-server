Usage
=====

This section provides information on how to use the Dev-Kit MCP Server.

Command-Line Arguments
-----------------------

The recommended way to use the Dev-Kit MCP Server is with the ``--root-dir`` parameter:

.. code-block:: bash

   dev-kit-mcp-server --root-dir=workdir

The server supports the following command-line argument:

* ``--root-dir ROOT_DIR``: Specifies the root directory for file operations. This is the directory that file operations will be restricted to for security reasons. If not specified, the current working directory is used.

Examples:

.. code-block:: bash

   # Recommended method (with root directory specified)
   dev-kit-mcp-server --root-dir=workdir

   # Alternative method
   python -m dev_kit_mcp_server.mcp_server --root-dir=workdir

The ``--root-dir`` parameter is important for security reasons, as it restricts file operations to the specified directory only.

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
