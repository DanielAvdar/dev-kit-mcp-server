API Reference
=============

This section provides detailed API documentation for the Python Code MCP Server.

Server Module
------------

.. py:module:: py_code.fastmcp_server

.. py:function:: start_server() -> FastMCP

   Start the FastMCP server.

   This function initializes and configures the FastMCP server with the necessary tools.
   It parses command-line arguments to determine the root directory for file operations.

   :return: A configured FastMCP server instance
   :rtype: FastMCP
   :raises ValueError: If the root directory does not exist or is not a directory

.. py:function:: run_server()

   Run the FastMCP server.

   This function starts the server and begins listening for client connections.

File Operations
--------------

Base File Operation
~~~~~~~~~~~~~~~~~~

.. py:module:: py_code.tools.code_editing.file_ops

.. py:class:: FileOperation

   Base class for file operations.

   :param root_dir: The root directory for file operations
   :type root_dir: str
   :raises Exception: If the root directory does not exist or is not a directory

   .. py:method:: _validate_path_in_root(path: str) -> bool

      Check if the given path is within the root directory.

      :param path: The path to check
      :type path: str
      :return: True if the path is within the root directory, False otherwise
      :rtype: bool

Create Directory Operation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: py_code.tools.code_editing.create

.. py:class:: CreateDirOperation

   Class to create a folder in the workspace.

   :param root_dir: The root directory for file operations
   :type root_dir: str

   .. py:method:: _create_folder(path: str) -> None

      Create a folder at the specified path.

      :param path: Path to the folder to create
      :type path: str
      :raises ValueError: If the path is not within the root directory
      :raises FileExistsError: If the path already exists
      :raises OSError: If there's an error creating the folder

   .. py:method:: __call__(path: str) -> Dict[str, Any]

      Create a file or folder in the workspace.

      :param path: Path to the folder to create
      :type path: str
      :return: A dictionary containing the status and path of the created file or folder
      :rtype: Dict[str, Any]

Move Directory Operation
~~~~~~~~~~~~~~~~~~~~~~~

.. py:module:: py_code.tools.code_editing.move

.. py:class:: MoveDirOperation

   Class to move a file or folder in the workspace.

   :param root_dir: The root directory for file operations
   :type root_dir: str

   .. py:method:: _move_folder(path1: str, path2: str) -> None

      Move a file or folder from path1 to path2.

      :param path1: Source path
      :type path1: str
      :param path2: Destination path
      :type path2: str
      :raises ValueError: If either path is not within the root directory
      :raises FileNotFoundError: If the source path does not exist
      :raises FileExistsError: If the destination path already exists
      :raises OSError: If there's an error moving the file or folder

   .. py:method:: __call__(path1: str, path2: str) -> Dict[str, Any]

      Move a file or folder from path1 to path2.

      :param path1: Source path
      :type path1: str
      :param path2: Destination path
      :type path2: str
      :return: A dictionary containing the status and paths of the moved file or folder
      :rtype: Dict[str, Any]

Remove File Operation
~~~~~~~~~~~~~~~~~~~~

.. py:module:: py_code.tools.code_editing.remove

.. py:class:: RemoveFileOperation

   Class to remove a file or folder.

   :param root_dir: The root directory for file operations
   :type root_dir: str

   .. py:method:: _remove_folder(path: str) -> None

      Remove a file or folder at the specified path.

      :param path: Path to the file or folder to remove
      :type path: str
      :raises ValueError: If the path is not within the root directory
      :raises FileNotFoundError: If the path does not exist
      :raises OSError: If there's an error removing the file or folder

   .. py:method:: __call__(path: str) -> Dict[str, Any]

      Remove a file or folder.

      :param path: Path to the file or folder to remove
      :type path: str
      :return: A dictionary containing the status and path of the removed file or folder
      :rtype: Dict[str, Any]
