"""MCP Server implementation using FastAPI."""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .analyzer import CodeAnalyzer
from .version import __version__

# Create FastAPI app
app = FastAPI(
    title="Python Code MCP Server",
    description="Model Context Protocol server for Python code analysis",
    version=__version__,
)


class CodeRequest(BaseModel):
    """Code request model for API endpoints."""

    code: str
    path: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis API endpoints."""

    result: Dict[str, Any]


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint that returns server info.

    Returns:
        Dictionary with server name, version, and description

    """
    return {
        "name": "Python Code MCP Server",
        "version": __version__,
        "description": "Model Context Protocol server for Python code analysis using AST and tokenize",
    }


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
        result = CodeAnalyzer.analyze(request.code)
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
        HTTPException: If there's an error parsing the AST

    """
    try:
        result = CodeAnalyzer.parse_ast(request.code)
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
        tokens = CodeAnalyzer.tokenize_code(request.code)
        # Limit token output
        return AnalysisResponse(result={"tokens": tokens[:100]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tokenizing code: {str(e)}") from e


@app.post("/count", response_model=AnalysisResponse)
async def count_elements(request: CodeRequest) -> AnalysisResponse:
    """Count elements in Python code (functions, classes, imports).

    Args:
        request: CodeRequest with code string and optional file path

    Returns:
        Count of code elements

    Raises:
        HTTPException: If there's an error counting elements in the code

    """
    try:
        ast_analysis = CodeAnalyzer.parse_ast(request.code)
        result = {
            "function_count": len(ast_analysis.get("functions", [])),
            "class_count": len(ast_analysis.get("classes", [])),
            "import_count": len(ast_analysis.get("imports", [])),
            "variable_count": len(ast_analysis.get("variables", [])),
        }
        return AnalysisResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error counting elements: {str(e)}") from e


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the MCP server with uvicorn.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)
