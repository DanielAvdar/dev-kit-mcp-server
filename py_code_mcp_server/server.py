"""MCP Server implementation using FastAPI."""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from py_code_mcp_server.analyzer import CodeAnalyzer

# Create FastAPI app
app = FastAPI(
    title="Python Code MCP Server",
    description="Model Context Protocol server for Python code analysis",
    version="0.1.0",
)


class CodeRequest(BaseModel):
    """Code request model for API endpoints."""

    code: str
    path: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis API endpoints."""

    result: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint that returns server info."""
    return {
        "name": "Python Code MCP Server",
        "version": "0.1.0",
        "description": "Model Context Protocol server for Python code analysis using AST and tokenize",
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_code(request: CodeRequest):
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


@app.post("/ast", response_model=AnalysisResponse)
async def ast_analysis(request: CodeRequest):
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


@app.post("/tokenize", response_model=AnalysisResponse)
async def tokenize_code(request: CodeRequest):
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


def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the MCP server with uvicorn.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)
