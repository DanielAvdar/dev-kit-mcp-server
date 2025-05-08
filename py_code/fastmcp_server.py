"""MCP Server implementation using FastMCP."""

from typing import Any, Dict, List, Optional

from fastmcp import Context, FastMCP

from .tools.code_analysis.analyzer import CodeAnalyzer
from .tools.code_analysis.code_analyzer import analyze_code_files, parse_ast_files
from .tools.code_analysis.file_search import file_search
from .tools.code_analysis.grep_search import grep_search
from .tools.code_analysis.list_code_usages import list_code_usages
from .tools.code_editing.list_dir import list_dir
from .tools.code_editing.read_file import read_file
from .tools.tool_factory import ToolFactory

# Create the FastMCP server
mcp = FastMCP(
    name="Python Code Analysis MCP",
    instructions="This server analyzes Python code and repositories using AST and tokenize modules.",
)

# Create a tool factory instance
tool_factory = ToolFactory(mcp)


# Create named wrappers for functions that we want to expose with specific names
@mcp.tool(name="find_code_usages")
def find_code_usages(
    symbol_name: str, file_paths: Optional[List[str]] = None, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """List all usages of a function, class, method, variable etc.

    Args:
        symbol_name: The name of the symbol to find usages for
        file_paths: Optional list of file paths to search in
        ctx: Optional context for logging

    Returns:
        A dictionary containing the found usages and metadata

    """
    return list_code_usages(symbol_name, file_paths, ctx)


@mcp.tool(name="search_files")
def search_files(query: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """Search for files by glob pattern.

    Args:
        query: The glob pattern to search for
        ctx: Optional context for logging

    Returns:
        A dictionary containing matching files and metadata

    """
    return file_search(query, ctx)


@mcp.tool(name="search_text")
def search_text(
    query: str, include_pattern: Optional[str] = None, is_regexp: bool = False, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Search for text in files.

    Args:
        query: The text pattern to search for
        include_pattern: Optional pattern to filter files to search
        is_regexp: Whether to treat the query as a regular expression
        ctx: Optional context for logging

    Returns:
        A dictionary containing search results and metadata

    """
    return grep_search(query, include_pattern, is_regexp, ctx)


@mcp.tool(name="read_file_content")
def read_file_content(
    file_path: str,
    start_line_number_base_zero: int = 0,
    end_line_number_base_zero: Optional[int] = None,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Read the contents of a file.

    Args:
        file_path: Path to the file to read
        start_line_number_base_zero: Line number to start reading from (0-based)
        end_line_number_base_zero: Line number to end reading at (0-based)
        ctx: Optional context for logging

    Returns:
        A dictionary containing the file contents and metadata

    """
    return read_file(file_path, start_line_number_base_zero, end_line_number_base_zero, ctx)


@mcp.tool(name="list_directory")
def list_directory(path: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
    """List the contents of a directory.

    Args:
        path: Path to the directory to list
        ctx: Optional context for logging

    Returns:
        A dictionary containing directory contents and metadata

    """
    return list_dir(path, ctx)


@mcp.tool(name="analyze_code")
def analyze_code(code: str) -> Dict[str, Any]:
    """Analyze Python code using AST and tokenize modules.

    Args:
        code: Python code as a string

    Returns:
        A dictionary containing code analysis results

    """
    return CodeAnalyzer.analyze(code)


@mcp.tool(name="parse_ast")
def parse_ast(code: str) -> Dict[str, Any]:
    """Parse Python code and return AST analysis.

    Args:
        code: Python code as a string

    Returns:
        A dictionary containing AST analysis results

    """
    return CodeAnalyzer.parse_ast(code)


@mcp.tool(name="parse_ast_from_files")
def parse_ast_from_files_tool(
    pattern: str, root_dir: Optional[str] = None, ignore_gitignore: bool = False, ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """Parse Python files matching the pattern and return AST analysis.

    Args:
        pattern: Glob pattern to match files
        root_dir: Optional root directory to search from
        ignore_gitignore: Whether to ignore .gitignore patterns
        ctx: Optional context for logging

    Returns:
        A dictionary containing AST analysis results for matched files

    """
    return parse_ast_files(pattern, root_dir, ignore_gitignore, ctx)


@mcp.tool(name="analyze_codebase")
def analyze_codebase_tool(
    pattern: str,
    root_dir: Optional[str] = None,
    ignore_gitignore: bool = False,
    include_tokens: bool = True,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    """Analyze Python files matching the pattern using AST and tokenize modules.

    Args:
        pattern: Glob pattern to match files
        root_dir: Optional root directory to search from
        ignore_gitignore: Whether to ignore .gitignore patterns
        include_tokens: Whether to include token analysis
        ctx: Optional context for logging

    Returns:
        A dictionary containing analysis results for matched files

    """
    return analyze_code_files(pattern, root_dir, ignore_gitignore, include_tokens, ctx)


@mcp.tool(name="tokenize_code")
def tokenize_code(code: str) -> List[Dict[str, Any]]:
    """Tokenize Python code.

    Args:
        code: Python code as a string

    Returns:
        A list of tokens from the Python code

    """
    return CodeAnalyzer.tokenize_code(code)


@mcp.tool(name="analyze_repository")
def analyze_repository(repo_path: str, file_filter: Optional[str] = None) -> Dict[str, Any]:
    """Analyze an entire repository or a specific path within it.

    Args:
        repo_path: Path to the repository
        file_filter: Optional filter to limit which files are analyzed

    Returns:
        A dictionary containing analysis results for the repository

    """
    return CodeAnalyzer.analyze_repository(repo_path, file_filter)


@mcp.tool(name="find_dependencies")
def find_dependencies(repo_path: str) -> Dict[str, Any]:
    """Analyze repository to find module dependencies between files.

    Args:
        repo_path: Path to the repository

    Returns:
        A dictionary containing dependency analysis results

    """
    return CodeAnalyzer.find_dependencies(repo_path)


# Register the tools using tool_factory
tool_factory([])


async def count_functions(code: str, ctx: Context) -> Dict[str, Any]:
    """Count the number of functions, classes, and imports in the code.

    Args:
        code: Python code as string
        ctx: Context object for logging and interaction.

    Returns:
        Counts of functions, classes, and imports

    """
    ast_analysis = CodeAnalyzer.parse_ast(code)

    # Log information using Context
    await ctx.info(f"Analyzing code with {len(code)} characters")

    result = {
        "function_count": len(ast_analysis.get("functions", [])),
        "class_count": len(ast_analysis.get("classes", [])),
        "import_count": len(ast_analysis.get("imports", [])),
        "variable_count": len(ast_analysis.get("variables", [])),
    }

    return result


async def analyze_code_or_repo(
    repo_path: Optional[str] = None, file_path: Optional[str] = None, code: Optional[str] = None, ctx: Context = None
) -> Dict[str, Any]:
    """Analyze Python code or an entire repository.

    Args:
        repo_path: Path to the repository (if analyzing a repository)
        file_path: Path to a specific file in the repository (optional)
        code: Python code as string (if analyzing raw code)
        ctx: Context object for logging and interaction

    Returns:
        Analysis results for the code or repository

    Raises:
        ValueError: If neither code nor repo_path is provided, or if the specified file_path doesn't exist

    """
    if ctx:
        if code:
            await ctx.info(f"Analyzing code with {len(code)} characters")
        elif repo_path:
            await ctx.info(f"Analyzing repository at {repo_path}")
            if file_path:
                await ctx.info(f"Focusing on file/directory: {file_path}")

    try:
        if code:
            # Analyze provided code
            return CodeAnalyzer.analyze(code)
        elif repo_path:
            if file_path:
                # Read and analyze specific file/directory
                import os

                full_path = os.path.join(repo_path, file_path)

                if os.path.isfile(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        file_code = f.read()
                    return CodeAnalyzer.analyze(file_code)
                elif os.path.isdir(full_path):
                    return CodeAnalyzer.analyze_repository(full_path)
                else:
                    raise ValueError(f"Path not found: {full_path}")
            else:
                # Analyze entire repository
                return CodeAnalyzer.analyze_repository(repo_path)
        else:
            raise ValueError("Either code or repo_path must be provided")
    except Exception as e:
        if ctx:
            await ctx.error(f"Error during analysis: {str(e)}")
        return {"error": str(e)}


@mcp.resource("code://examples/hello_world")
def hello_world_example() -> str:
    """Provide a simple Hello World example in Python.

    Returns:
        A string containing a Hello World example in Python

    """
    return """# Hello World example
def greet(name: str) -> str:
    '''Greet someone by name'''
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
"""


@mcp.resource("code://examples/class_example")
def class_example() -> str:
    """Provide a simple class example in Python.

    Returns:
        A string containing a class example in Python

    """
    return """# Class example
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"Hello, my name is {self.name} and I am {self.age} years old."

if __name__ == "__main__":
    person = Person("Alice", 30)
    print(person.greet())
"""


def start_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the MCP server with the specified transport.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to

    """
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    # This allows running the module directly
    start_server(host="127.0.0.1", port=9090)
