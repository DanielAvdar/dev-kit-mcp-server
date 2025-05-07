"""Integrated FastAPI and FastMCP server implementation."""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi_mcp import FastApiMCP
from fastmcp import Client, Context, FastMCP
from pydantic import BaseModel
from starlette.responses import Response

from .fastmcp_server import mcp as fastmcp_server
from .tools.mcp_tools import (
    analyze_ast as impl_analyze_ast,
    analyze_full as impl_analyze_full,
    analyze_tokens as impl_analyze_tokens,
    count_elements as impl_count_elements,
    get_server_info as impl_get_server_info,
)
from .version import __version__


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
    version=__version__,
)


# Add HTTP endpoints to the FastAPI app
@app.get("/server-info")
async def server_info() -> Dict[str, Any]:
    """Server info endpoint that returns server details.

    Returns:
        Dictionary with server name, version, and description

    """
    return impl_get_server_info()


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
    return impl_get_server_info()


@mcp.tool()
async def analyze_full(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Analyze Python code using AST and tokenize.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        Analysis results including AST and token information

    """
    return impl_analyze_full(code, path)


@mcp.tool()
async def analyze_ast(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Parse Python code and return AST analysis.

    Args:
        code: Python code string to analyze
        path: Optional file path for the code

    Returns:
        AST analysis results

    """
    return impl_analyze_ast(code, path)


@mcp.tool()
async def analyze_tokens(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Tokenize Python code.

    Args:
        code: Python code string to tokenize
        path: Optional file path for the code

    Returns:
        Tokenization results

    """
    return impl_analyze_tokens(code, path)


@mcp.tool()
async def count_elements(code: str, path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """Count elements in Python code (functions, classes, imports).

    Args:
        code: Python code string to analyze
        path: Optional file path for the code
        ctx: Optional MCP context

    Returns:
        Count of code elements

    """
    return impl_count_elements(code, path, ctx)


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


# Create FastAPI-MCP server
fastapi_mcp = FastApiMCP(
    app,  # Pass the FastAPI app directly
    name="Python Code Analysis API",
    description="API for Python code analysis using AST and tokenize modules",
    describe_all_responses=True,
    describe_full_response_schema=True,
)


# Configure the combined server
def create_combined_server() -> FastAPI:
    """Create and configure the combined FastAPI+MCP server.

    Returns:
        FastAPI application instance with MCP server mounted

    """

    # Add the root endpoint for regular HTTP requests (not SSE)
    @app.get("/", include_in_schema=False)
    async def root(request: Request) -> Response:
        """Root endpoint that handles regular HTTP requests (not SSE).

        SSE requests are handled by the FastAPI-MCP middleware.

        Args:
            request: The incoming request

        Returns:
            Response with server info as JSON

        """
        # Return server info as JSON for regular HTTP requests
        return JSONResponse(content=impl_get_server_info())

    # Add the other HTTP endpoints
    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_code(request: CodeRequest) -> AnalysisResponse:
        """Analyze Python code using AST and tokenize.

        Args:
            request: CodeRequest with code string and optional file path

        Returns:
            Analysis results including AST and token information

        Raises:
            HTTPException: If there's an error analyzing the code

        """
        try:
            result = impl_analyze_full(request.code, request.path)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing code: {str(e)}") from e

    @app.post("/ast", response_model=AnalysisResponse)
    async def ast_analysis(request: CodeRequest) -> AnalysisResponse:
        """Parse Python code and return AST analysis.

        Args:
            request: CodeRequest with code string and optional file path

        Returns:
            AST analysis results

        Raises:
            HTTPException: If there's a syntax error or problem parsing the AST

        """
        try:
            result = impl_analyze_ast(request.code, request.path)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing AST: {str(e)}") from e

    @app.post("/tokenize", response_model=AnalysisResponse)
    async def tokenize_code(request: CodeRequest) -> AnalysisResponse:
        """Tokenize Python code.

        Args:
            request: CodeRequest with code string and optional file path

        Returns:
            Tokenization results

        Raises:
            HTTPException: If there's an error tokenizing the code

        """
        try:
            result = impl_analyze_tokens(request.code, request.path)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error tokenizing code: {str(e)}") from e

    @app.post("/count", response_model=AnalysisResponse)
    async def count_code_elements(request: CodeRequest) -> AnalysisResponse:
        """Count elements in Python code (functions, classes, imports).

        Args:
            request: CodeRequest with code string and optional file path

        Returns:
            Count of code elements

        Raises:
            HTTPException: If there's an error counting elements in the code

        """
        try:
            result = impl_count_elements(request.code, request.path, None)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error counting elements: {str(e)}") from e

    # Mount the MCP server with correct SSE handling
    fastapi_mcp.mount()

    return app


# Entry point to run the server
def run_server(host: str = "localhost", port: int = 8000) -> None:
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
