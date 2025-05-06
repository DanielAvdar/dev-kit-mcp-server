"""MCP Server implementation using FastMCP."""

from typing import Any, Dict, List

from fastmcp import Context, FastMCP

from .analyzer import CodeAnalyzer

# Create the FastMCP server
mcp = FastMCP(
    name="Python Code Analysis MCP", instructions="This server analyzes Python code using AST and tokenize modules."
)


@mcp.tool()
def analyze_code(code: str) -> Dict[str, Any]:
    """Analyze Python code using AST and tokenize modules.

    Args:
        code: Python code as string

    Returns:
        Analysis results including AST and token information

    """
    return CodeAnalyzer.analyze(code)


@mcp.tool()
def parse_ast(code: str) -> Dict[str, Any]:
    """Parse Python code and return AST analysis.

    Args:
        code: Python code as string

    Returns:
        AST analysis results

    """
    return CodeAnalyzer.parse_ast(code)


@mcp.tool()
def tokenize_code(code: str) -> List[Dict[str, Any]]:
    """Tokenize Python code.

    Args:
        code: Python code as string

    Returns:
        List of tokens with type and string value

    """
    return CodeAnalyzer.tokenize_code(code)


@mcp.tool()
async def count_functions(code: str, ctx: Context) -> Dict[str, Any]:
    """Count the number of functions, classes, and imports in the code.

    Args:
        code: Python code as string
        ctx: Context object for logging and interaction

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
