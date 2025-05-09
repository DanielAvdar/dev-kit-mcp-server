Usage Guide
===========

This guide provides detailed instructions on how to use the Python Code MCP Server.

Installation
------------

You can install the Python Code MCP Server using pip:

.. code-block:: bash

   pip install py-code-mcp-server

Running the Server
------------------

There are several ways to run the server:

Standard Method
~~~~~~~~~~~~~~~

Run the server with default settings (0.0.0.0:8000):

.. code-block:: bash

   py-mcp-server

You can specify a different host and port:

.. code-block:: bash

   py-mcp-server --host 127.0.0.1 --port 8080

Development Mode
~~~~~~~~~~~~~~~~

Run the server with auto-reload on code changes:

.. code-block:: bash

   # Using the Makefile
   make run-dev

   # Or directly
   python -m uvicorn "py_code.integrated_server:create_combined_server" --reload --host 127.0.0.1 --port 9090

FastMCP Mode
~~~~~~~~~~~~

Run the server using FastMCP:

.. code-block:: bash

   # Using the Makefile
   make run

   # Or directly
   python run_fastmcp.py

Watch Mode
~~~~~~~~~~

Run the server with file watching:

.. code-block:: bash

   # Using the Makefile
   make run-watch

   # Or directly
   watchfiles "python -m py_code.mcp_server.__main__ --host 127.0.0.1 --port 9090" py_code

API Endpoints
-------------

The server provides several endpoints for analyzing Python code and performing file operations:

Code Analysis Endpoints:

- ``GET /``: Server information
- ``POST /analyze``: Full code analysis
- ``POST /ast``: AST-only analysis
- ``POST /tokenize``: Token extraction
- ``POST /count``: Element counting

File Operations Endpoints:

- ``POST /read_file_content``: Read the contents of a file
- ``POST /list_directory``: List the contents of a directory
- ``POST /move_file_or_folder``: Move a file or folder to a new location
- ``POST /delete_file``: Delete a file from the workspace

Example Requests
----------------

Full Analysis
~~~~~~~~~~~~~

.. code-block:: python

   import requests

   code = """
   def hello_world():
       print("Hello, World!")

   class Person:
       def __init__(self, name):
           self.name = name
   """

   response = requests.post(
       "http://localhost:8000/analyze",
       json={"code": code}
   )

   print(response.json())

AST Analysis
~~~~~~~~~~~~

.. code-block:: python

   import requests

   code = """
   def hello_world():
       print("Hello, World!")
   """

   response = requests.post(
       "http://localhost:8000/ast",
       json={"code": code}
   )

   print(response.json())

Token Extraction
~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   code = """
   def hello_world():
       print("Hello, World!")
   """

   response = requests.post(
       "http://localhost:8000/tokenize",
       json={"code": code}
   )

   print(response.json())

Element Counting
~~~~~~~~~~~~~~~~

.. code-block:: python

   import requests

   code = """
   import os
   import sys

   def hello_world():
       print("Hello, World!")

   class Person:
       def __init__(self, name):
           self.name = name
   """

   response = requests.post(
       "http://localhost:8000/count",
       json={"code": code}
   )

   print(response.json())

File Operations
~~~~~~~~~~~~~~

Move File or Folder
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import requests

   response = requests.post(
       "http://localhost:8000/move_file_or_folder",
       json={
           "source_path": "path/to/source/file.py",
           "destination_path": "path/to/destination/file.py"
       }
   )

   print(response.json())

Delete File
^^^^^^^^^^

.. code-block:: python

   import requests

   response = requests.post(
       "http://localhost:8000/delete_file",
       json={
           "file_path": "path/to/file/to/delete.py"
       }
   )

   print(response.json())
