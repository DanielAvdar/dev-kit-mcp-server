"""Integrated FastAPI and FastMCP server implementation."""

import ast
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastmcp import Client, Context, FastMCP
from pydantic import BaseModel

from py_code_mcp_server.analyzer import CodeAnalyzer
from py_code_mcp_server.fastmcp_server import mcp as fastmcp_server


class CodeRequest(BaseModel):
    """Code request model for API endpoints."""

    code: str
    path: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis API endpoints."""

    result: Dict[str, Any]


# Create FastAPI app
app = FastAPI(
    title="Python Code MCP Server",
    description="Model Context Protocol server for Python code analysis",
    version="0.1.0",
)

# Create MCP server
mcp = FastMCP(
    name="Python Code MCP Server",
    description="Model Context Protocol server for Python code analysis using AST and tokenize",
)


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """Get server information.

    Returns:
        Server information including name, version, and description

    """
    return {
        "name": "Python Code MCP Server",
        "version": "0.1.0",
        "description": "Model Context Protocol server for Python code analysis using AST and tokenize",
    }


@mcp.tool()
async def analyze_full(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Analyze Python code using AST and tokenize.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        Analysis results including AST and token information

    Raises:
        Exception: If there's an error analyzing the code

    """
    try:
        result = CodeAnalyzer.analyze(code)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error analyzing code: {str(e)}") from e


@mcp.tool()
async def analyze_ast(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Parse Python code and return AST analysis.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        AST analysis results

    Raises:
        Exception: If code is None or there's a syntax/parsing error

    """
    # First check for syntax errors
    if code is None:
        raise Exception("Error parsing AST: code cannot be None")

    try:
        # Try to parse the code to catch syntax errors early
        ast.parse(code)
    except SyntaxError as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e

    try:
        result = CodeAnalyzer.parse_ast(code)
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error parsing AST: {str(e)}") from e


@mcp.tool()
async def analyze_tokens(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Tokenize Python code.

    Args:
        code: Python code string to tokenize
        path: Optional file path for the code

    Returns:
        Tokenization results

    Raises:
        Exception: If code is None or there's an error tokenizing the code

    """
    # First check for None values to match test expectations
    if code is None:
        raise Exception("Error tokenizing code: code cannot be None")

    try:
        tokens = CodeAnalyzer.tokenize_code(code)
        # Limit token output
        return {"result": {"tokens": tokens[:100]}}
    except Exception as e:
        raise Exception(f"Error tokenizing code: {str(e)}") from e


@mcp.tool()
async def count_elements(code: str, path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """Count elements in Python code (functions, classes, imports).

    Args:
        code: Python code string to analyze
        path: Optional file path for the code
        ctx: Optional MCP context

    Returns:
        Count of code elements

    Raises:
        Exception: If there's an error counting elements in the code

    """
    try:
        if ctx:
            await ctx.info(f"Counting elements in code with {len(code)} characters")

        ast_analysis = CodeAnalyzer.parse_ast(code)
        result = {
            "function_count": len(ast_analysis.get("functions", [])),
            "class_count": len(ast_analysis.get("classes", [])),
            "import_count": len(ast_analysis.get("imports", [])),
            "variable_count": len(ast_analysis.get("variables", [])),
        }
        return {"result": result}
    except Exception as e:
        raise Exception(f"Error counting elements: {str(e)}") from e


# Create FastAPI-MCP server
fastapi_mcp = FastApiMCP(
    app,
    name="Python Code Analysis API",
    description="API for Python code analysis using AST and tokenize modules",
    describe_all_responses=True,
    describe_full_response_schema=True,
)


# Create a proxy to the FastMCP server
async def proxy_to_fastmcp() -> FastMCP:
    """Proxy requests to the FastMCP server.

    Returns:
        FastMCP proxy instance that bridges FastAPI and the separate FastMCP implementation

    """
    # This creates a bridge between FastAPI and the separate FastMCP implementation
    proxy = FastMCP.from_client(
        Client(fastmcp_server),  # Use in-memory client
        name="FastMCP Proxy",
    )
    return proxy


# Configure the combined server
def create_combined_server() -> FastAPI:
    """Create and configure the combined FastAPI+MCP server.

    Returns:
        FastAPI application instance with MCP server mounted

    """
    # Mount the MCP server to make FastAPI endpoints available as MCP tools
    fastapi_mcp.mount()

    return app


# Entry point to run the server
def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Run the integrated MCP server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    import uvicorn

    # Create and configure the server
    app = create_combined_server()

    # Run the server
    uvicorn.run(app, host=host, port=port)
