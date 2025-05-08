"""Parameterized tests for the CodeAnalyzer class."""

import pytest

from py_code.tools.code_analysis.analyzer import CodeAnalyzer


@pytest.mark.parametrize(
    "code,expected_functions,expected_classes,expected_imports,expected_variables",
    [
        # Test case 1: Simple function
        (
            """
def hello_world():
    print("Hello, World!")
""",
            [{"name": "hello_world", "params": []}],
            [],
            [],
            [],
        ),
        # Test case 2: Function with parameters
        (
            """
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
""",
            [{"name": "greet", "params": ["name", "greeting"]}],
            [],
            [],
            [],
        ),
        # Test case 3: Class with methods
        (
            """
class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}!"
""",
            [{"name": "__init__", "params": ["self", "name"]}, {"name": "greet", "params": ["self"]}],
            [{"name": "Person", "bases": []}],
            [],
            [],
        ),
        # Test case 4: Imports and variables
        (
            """
import os
from sys import path

x = 10
y = "hello"
""",
            [],
            [],
            [{"name": "os", "alias": None}, {"name": "sys.path", "alias": None}],
            [{"name": "x"}, {"name": "y"}],
        ),
        # Test case 5: Class with inheritance
        (
            """
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"
""",
            [{"name": "speak", "params": ["self"]}, {"name": "speak", "params": ["self"]}],
            [{"name": "Animal", "bases": []}, {"name": "Dog", "bases": ["Animal"]}],
            [],
            [],
        ),
    ],
)
def test_parse_ast_parameterized(code, expected_functions, expected_classes, expected_imports, expected_variables):
    """Test parsing AST with various code snippets."""
    result = CodeAnalyzer.parse_ast(code)

    # Check functions
    if expected_functions:
        assert "functions" in result
        assert len(result["functions"]) == len(expected_functions)
        for i, expected_func in enumerate(expected_functions):
            assert result["functions"][i]["name"] == expected_func["name"]
            assert len(result["functions"][i]["params"]) == len(expected_func["params"])
            for param in expected_func["params"]:
                assert param in result["functions"][i]["params"]
    else:
        assert "functions" in result
        assert len(result["functions"]) == 0

    # Check classes
    if expected_classes:
        assert "classes" in result
        assert len(result["classes"]) == len(expected_classes)
        for i, expected_class in enumerate(expected_classes):
            assert result["classes"][i]["name"] == expected_class["name"]
            # Check bases if they exist
            if expected_class["bases"]:
                for base in expected_class["bases"]:
                    assert base in result["classes"][i]["bases"]
    else:
        assert "classes" in result
        assert len(result["classes"]) == 0

    # Check imports
    if expected_imports:
        assert "imports" in result
        assert len(result["imports"]) == len(expected_imports)
        for expected_import in expected_imports:
            assert any(
                imp["name"] == expected_import["name"] and imp["alias"] == expected_import["alias"]
                for imp in result["imports"]
            )
    else:
        assert "imports" in result
        assert len(result["imports"]) == 0

    # Check variables
    if expected_variables:
        assert "variables" in result
        assert len(result["variables"]) == len(expected_variables)
        for expected_var in expected_variables:
            assert any(var["name"] == expected_var["name"] for var in result["variables"])
    else:
        assert "variables" in result
        assert len(result["variables"]) == 0


@pytest.mark.parametrize(
    "code,expected_tokens",
    [
        # Test case 1: Simple print statement
        (
            'print("Hello, World!")',
            ["print", '"Hello, World!"'],
        ),
        # Test case 2: Variable assignment
        (
            "x = 42",
            ["x", "=", "42"],
        ),
        # Test case 3: Function definition
        (
            "def test(): pass",
            ["def", "test", "(", ")", ":", "pass"],
        ),
        # Test case 4: Import statement
        (
            "import os",
            ["import", "os"],
        ),
        # Test case 5: For loop
        (
            "for i in range(10): print(i)",
            ["for", "i", "in", "range", "(", "10", ")", ":", "print", "(", "i", ")"],
        ),
    ],
)
def test_tokenize_code_parameterized(code, expected_tokens):
    """Test tokenizing various code snippets."""
    tokens = CodeAnalyzer.tokenize_code(code)

    # Check that we have tokens and no errors
    assert len(tokens) > 0
    assert all("error" not in token for token in tokens)

    # Check for expected tokens
    token_strings = [token["string"] for token in tokens if "string" in token]
    for expected_token in expected_tokens:
        assert expected_token in token_strings


@pytest.mark.parametrize(
    "code,expected_ast_keys,expected_token_types",
    [
        # Test case 1: Simple function
        (
            """
def hello():
    return "Hello, World!"
""",
            {"functions": 1, "classes": 0, "imports": 0, "variables": 0},
            ["NAME", "OP", "STRING", "NEWLINE", "INDENT", "DEDENT"],
        ),
        # Test case 2: Class with methods
        (
            """
class Person:
    def __init__(self, name):
        self.name = name
""",
            {"functions": 1, "classes": 1, "imports": 0, "variables": 0},
            ["NAME", "OP", "NEWLINE", "INDENT", "DEDENT"],
        ),
        # Test case 3: Imports and variables
        (
            """
import os
x = 10
""",
            {"functions": 0, "classes": 0, "imports": 1, "variables": 1},
            ["NAME", "OP", "NUMBER", "NEWLINE"],
        ),
        # Test case 4: Complex example
        (
            """
import sys
from os import path

class Logger:
    def __init__(self, name):
        self.name = name
        self.level = 0

    def log(self, message):
        print(f"[{self.name}] {message}")

logger = Logger("main")
""",
            {"functions": 2, "classes": 1, "imports": 2, "variables": 1},
            ["NAME", "OP", "STRING", "NUMBER", "NEWLINE", "INDENT", "DEDENT"],
        ),
    ],
)
def test_analyze_parameterized(code, expected_ast_keys, expected_token_types):
    """Test full analysis of various code snippets."""
    result = CodeAnalyzer.analyze(code)

    # Check that we have ast_analysis, tokens, and token_summary
    assert "ast_analysis" in result
    assert "tokens" in result
    assert "token_summary" in result

    # Check AST analysis results
    ast_analysis = result["ast_analysis"]
    assert len(ast_analysis.get("functions", [])) == expected_ast_keys["functions"]
    assert len(ast_analysis.get("classes", [])) == expected_ast_keys["classes"]
    assert len(ast_analysis.get("imports", [])) == expected_ast_keys["imports"]
    assert len(ast_analysis.get("variables", [])) == expected_ast_keys["variables"]

    # Check token types
    token_summary = result["token_summary"]
    for expected_type in expected_token_types:
        assert expected_type in token_summary
