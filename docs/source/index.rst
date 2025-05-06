.. Python Code MCP Server documentation master file

Python Code MCP Server
======================

A Model Context Protocol (MCP) server for Python code analysis.

This package provides a fast and efficient way to analyze Python code using Abstract Syntax Trees (AST) and tokenization.

Features
--------

- **Code Analysis**: Analyze Python code structure using AST
- **Tokenization**: Extract tokens from Python code
- **Element Counting**: Count functions, classes, imports, and variables
- **Fast API**: Built with FastAPI for high performance
- **MCP Compliant**: Follows the Model Context Protocol specification

Installation
-----------

.. code-block:: bash

   pip install py-code-mcp-server

Quick Start
----------

Running the Server
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Start the MCP server
   py-mcp-server

   # Specify host and port
   py-mcp-server --host 127.0.0.1 --port 8080

API Endpoints
~~~~~~~~~~~~

- ``GET /``: Server information
- ``POST /analyze``: Full code analysis
- ``POST /ast``: AST-only analysis
- ``POST /tokenize``: Token extraction
- ``POST /count``: Element counting

Example Request
~~~~~~~~~~~~~~

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

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
