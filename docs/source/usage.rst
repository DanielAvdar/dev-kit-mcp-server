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

Rename File or Directory
~~~~~~~~~~~~~~~~~~~~~~~~

Renames a file or directory to a new name within the same directory.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("rename_file", {"path": "path/to/file.txt", "new_name": "new_file_name.txt"})

The operation will fail if:

* The path is outside the root directory
* The path does not exist
* A file or folder with the new name already exists in the same directory

Git Operations
--------------

The server provides several tools for Git operations:

Git Status
~~~~~~~~~~

Gets the status of the Git repository, including changed files, untracked files, and staged files.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("git_status")

Git Add
~~~~~~~

Adds files to the Git index (staging area).

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("git_add", {"paths": ["file1.txt", "file2.txt"]})

The operation will fail if:

* Any of the paths are outside the root directory
* Any of the paths do not exist

Git Commit
~~~~~~~~~~

Commits changes to the Git repository.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("git_commit", {"message": "Commit message"})

The operation will fail if:

* The commit message is empty

Git Push
~~~~~~~~

Pushes changes to a remote Git repository.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("git_push")

Git Pull
~~~~~~~~

Pulls changes from a remote Git repository.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("git_pull", {"remote": "origin", "branch": "main"})

Git Checkout
~~~~~~~~~~~~

Checks out or creates a branch in the Git repository.

.. code-block:: python

   # Using the MCP client
   # Checkout existing branch
   result = await client.call_tool("git_checkout", {"branch": "main"})

   # Create and checkout new branch
   result = await client.call_tool("git_checkout", {"branch": "feature-branch", "create": True})

The operation will fail if:

* The branch name is empty
* The branch doesn't exist and create is False

Git Diff
~~~~~~~~

Shows diffs between commits, commit and working tree, etc.

.. code-block:: python

   # Using the MCP client
   # Show diff for a specific file
   result = await client.call_tool("git_diff", {"path_or_commit": "file.txt"})

   # Show diff with options
   result = await client.call_tool("git_diff", {"path_or_commit": "file.txt", "options": "--stat"})

The operation will fail if:

* The path or commit is empty

Makefile Operations
-------------------

The server provides a tool for executing Makefile targets:

Execute Makefile Target
~~~~~~~~~~~~~~~~~~~~~~~

Executes a Makefile target securely within the project.

.. code-block:: python

   # Using the MCP client
   result = await client.call_tool("exec_make_target", {"commands": ["test"]})

The operation will fail if:

* The Makefile doesn't exist in the root directory
* The target is invalid
* The command execution fails

Security Considerations
------------------------

All file operations are restricted to the specified root directory for security reasons. Any attempt to perform operations outside this directory will fail with an error message.
