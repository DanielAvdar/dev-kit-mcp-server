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
    description="Model Context Protocol server for repository navigation and code exploration",
    version=__version__,
)


# Add HTTP endpoints to the FastAPI app
@app.get("/server-info")
async def server_info() -> Dict[str, Any]:
    """Get information about the repository navigation server.

    Returns:
        Dictionary with server name, version, and repository navigation capabilities

    """
    return impl_get_server_info()


# Create MCP server
mcp = FastMCP(
    name="Python Code MCP Server",
    description="Model Context Protocol server for turning repositories into navigable MCP systems",
)


@mcp.tool()
async def get_server_info() -> Dict[str, Any]:
    """Get information about the MCP repository navigation server.

    Returns:
        Server information including name, version, and description of the repository navigation capabilities

    """
    return impl_get_server_info()


@mcp.tool()
async def analyze_full(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Comprehensively analyze code structure for repository navigation.

    Args:
        code: Code string to analyze for navigation
        path: Optional file path within the repository

    Returns:
        Detailed code structure analysis for repository exploration

    """
    return impl_analyze_full(code, path)


@mcp.tool()
async def analyze_ast(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Extract code structure for repository navigation.

    Args:
        code: Code string to analyze for structure
        path: Optional file path within the repository

    Returns:
        Code structure information for navigating the repository

    """
    return impl_analyze_ast(code, path)


@mcp.tool()
async def analyze_tokens(code: str, path: Optional[str] = None) -> Dict[str, Any]:
    """Identify code elements for detailed repository exploration.

    Args:
        code: Code string to analyze for elements
        path: Optional file path within the repository

    Returns:
        Detailed code elements for fine-grained repository navigation

    """
    return impl_analyze_tokens(code, path)


@mcp.tool()
async def count_elements(code: str, path: Optional[str] = None, ctx: Context = None) -> Dict[str, Any]:
    """Summarize repository components for high-level navigation.

    Args:
        code: Code string to analyze for components
        path: Optional file path within the repository
        ctx: Optional MCP context

    Returns:
        Summary of repository components for high-level navigation

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
    name="Repository Navigation API",
    description="API for navigating and exploring code repositories through MCP",
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
        """Root endpoint for the repository navigation server.

        Provides basic information about the MCP repository navigation capabilities.
        SSE requests are handled by the FastAPI-MCP middleware.

        Args:
            request: The incoming request

        Returns:
            Response with repository navigation server info as JSON

        """
        # Return server info as JSON for regular HTTP requests
        return JSONResponse(content=impl_get_server_info())

    # Add the other HTTP endpoints
    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_code(request: CodeRequest) -> AnalysisResponse:
        """Comprehensively analyze code for repository navigation.

        Args:
            request: CodeRequest with code string and optional repository file path

        Returns:
            Detailed code structure analysis for repository exploration

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
        """Extract code structure for repository navigation.

        Args:
            request: CodeRequest with code string and optional repository file path

        Returns:
            Code structure information for navigating the repository

        Raises:
            HTTPException: If there's a syntax error or problem extracting the structure

        """
        try:
            result = impl_analyze_ast(request.code, request.path)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error parsing AST: {str(e)}") from e

    @app.post("/tokenize", response_model=AnalysisResponse)
    async def tokenize_code(request: CodeRequest) -> AnalysisResponse:
        """Identify code elements for detailed repository exploration.

        Args:
            request: CodeRequest with code string and optional repository file path

        Returns:
            Detailed code elements for fine-grained repository navigation

        Raises:
            HTTPException: If there's an error identifying code elements

        """
        try:
            result = impl_analyze_tokens(request.code, request.path)
            return AnalysisResponse(result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error tokenizing code: {str(e)}") from e

    @app.post("/count", response_model=AnalysisResponse)
    async def count_code_elements(request: CodeRequest) -> AnalysisResponse:
        """Summarize repository components for high-level navigation.

        Args:
            request: CodeRequest with code string and optional repository file path

        Returns:
            Summary of repository components for high-level navigation

        Raises:
            HTTPException: If there's an error summarizing repository components

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
