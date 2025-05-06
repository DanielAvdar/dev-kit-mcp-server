"""Integrated FastAPI and FastMCP server implementation."""

from typing import Any, Dict, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi_mcp import FastApiMCP
from fastmcp import Client, FastMCP
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


@app.get("/", operation_id="get_server_info")
async def root():
    """Root endpoint that returns server info."""
    return {
        "name": "Python Code MCP Server",
        "version": "0.1.0",
        "description": "Model Context Protocol server for Python code analysis using AST and tokenize",
    }


@app.post("/analyze", response_model=AnalysisResponse, operation_id="analyze_full")
async def analyze_code(request: CodeRequest = Body(...)):
    """Analyze Python code using AST and tokenize.

    Args:
        request: CodeRequest with code string and optional file path

    Returns:
        Analysis results including AST and token information

    """
    try:
        result = CodeAnalyzer.analyze(request.code)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}")


@app.post("/ast", response_model=AnalysisResponse, operation_id="analyze_ast")
async def ast_analysis(request: CodeRequest = Body(...)):
    """Parse Python code and return AST analysis.

    Args:
        request: CodeRequest with code string and optional file path

    Returns:
        AST analysis results

    """
    try:
        result = CodeAnalyzer.parse_ast(request.code)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing AST: {str(e)}")


@app.post("/tokenize", response_model=AnalysisResponse, operation_id="analyze_tokens")
async def tokenize_code(request: CodeRequest = Body(...)):
    """Tokenize Python code.

    Args:
        request: CodeRequest with code string and optional file path

    Returns:
        Tokenization results

    """
    try:
        tokens = CodeAnalyzer.tokenize_code(request.code)
        # Limit token output
        return {"result": {"tokens": tokens[:100]}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tokenizing code: {str(e)}")


@app.post("/count", response_model=AnalysisResponse, operation_id="count_elements")
async def count_elements(request: CodeRequest = Body(...)):
    """Count elements in Python code (functions, classes, imports).

    Args:
        request: CodeRequest with code string and optional file path

    Returns:
        Count of code elements

    """
    try:
        ast_analysis = CodeAnalyzer.parse_ast(request.code)
        result = {
            "function_count": len(ast_analysis.get("functions", [])),
            "class_count": len(ast_analysis.get("classes", [])),
            "import_count": len(ast_analysis.get("imports", [])),
            "variable_count": len(ast_analysis.get("variables", [])),
        }
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting elements: {str(e)}")


# Create FastAPI-MCP server
fastapi_mcp = FastApiMCP(
    app,
    name="Python Code Analysis API",
    description="API for Python code analysis using AST and tokenize modules",
    describe_all_responses=True,
    describe_full_response_schema=True,
)


# Create a proxy to the FastMCP server
async def proxy_to_fastmcp():
    """Proxy requests to the FastMCP server."""
    # This creates a bridge between FastAPI and the separate FastMCP implementation
    proxy = FastMCP.from_client(
        Client(fastmcp_server),  # Use in-memory client
        name="FastMCP Proxy",
    )
    return proxy


# Configure the combined server
def create_combined_server():
    """Create and configure the combined FastAPI+MCP server."""
    # Mount the MCP server to make FastAPI endpoints available as MCP tools
    fastapi_mcp.mount()

    return app


# Entry point to run the server
def run_server(host: str = "0.0.0.0", port: int = 8000):
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
