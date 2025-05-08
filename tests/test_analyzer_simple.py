"""Simple test for the CodeAnalyzer class."""

from py_code.tools.code_analysis.analyzer import CodeAnalyzer


def test_parse_ast_simple():
    """Test parsing a simple function definition."""
    code = """
def hello_world():
    print("Hello, World!")
"""
    result = CodeAnalyzer.parse_ast(code)

    # Check that we have one function
    assert "functions" in result
    assert len(result["functions"]) == 1
    assert result["functions"][0]["name"] == "hello_world"
    assert result["functions"][0]["params"] == []


def test_tokenize_code_simple():
    """Test tokenizing a simple string."""
    code = 'print("Hello, World!")'
    tokens = CodeAnalyzer.tokenize_code(code)

    # Check that we have tokens and no errors
    assert len(tokens) > 0
    assert all("error" not in token for token in tokens)

    # Check for specific tokens
    token_strings = [token["string"] for token in tokens if "string" in token]
    assert "print" in token_strings
    assert '"Hello, World!"' in token_strings


def test_analyze_simple():
    """Test full analysis of a simple class."""
    code = """
class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"
"""
    result = CodeAnalyzer.analyze(code)

    # Check that we have ast_analysis, tokens, and token_summary
    assert "ast_analysis" in result
    assert "tokens" in result
    assert "token_summary" in result

    # Check class information
    assert len(result["ast_analysis"]["classes"]) == 1
    assert result["ast_analysis"]["classes"][0]["name"] == "Person"

    # Check function information
    assert len(result["ast_analysis"]["functions"]) == 2
    function_names = [f["name"] for f in result["ast_analysis"]["functions"]]
    assert "__init__" in function_names
    assert "greet" in function_names
