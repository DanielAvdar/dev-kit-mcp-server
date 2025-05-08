"""Parameterized tests for the list_code_usages module."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.code_analysis.list_code_usages import list_code_usages


@pytest.fixture
def temp_dir_with_python_files():
    """Create a temporary directory with Python files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file with function definition and usage
        with open(os.path.join(temp_dir, "functions.py"), "w") as f:
            f.write("""
def test_function(arg1, arg2):
    \"\"\"A test function.\"\"\"
    return arg1 + arg2

def another_function():
    # Call test_function
    result = test_function(1, 2)
    return result
""")

        # Create a file with class definition and usage
        with open(os.path.join(temp_dir, "classes.py"), "w") as f:
            f.write("""
class TestClass:
    \"\"\"A test class.\"\"\"
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

# Create an instance of TestClass
test_instance = TestClass(42)
result = test_instance.get_value()
""")

        # Create a file with imports
        with open(os.path.join(temp_dir, "imports.py"), "w") as f:
            f.write("""
from functions import test_function
import classes

# Use the imported function
result = test_function(3, 4)

# Use the imported class
instance = classes.TestClass(10)
""")

        # Create a file with variable definition and usage
        with open(os.path.join(temp_dir, "variables.py"), "w") as f:
            f.write("""
test_variable = 42

def use_variable():
    return test_variable + 10
""")

        yield temp_dir


def test_list_code_usages_function(temp_dir_with_python_files):
    """Test finding usages of a function."""
    with patch("os.getcwd", return_value=temp_dir_with_python_files):
        result = list_code_usages("test_function")

        # Check the result structure
        assert "symbol" in result
        assert "definitions" in result
        assert "references" in result
        assert "imports" in result
        assert "total_usages" in result

        # Check the symbol name
        assert result["symbol"] == "test_function"

        # Check that we found the definition
        assert len(result["definitions"]) == 1
        assert "functions.py" in result["definitions"][0]["file_path"]
        assert "def test_function" in result["definitions"][0]["content"]

        # Check that we found the references
        assert len(result["references"]) >= 1
        assert any("result = test_function(1, 2)" in ref["content"] for ref in result["references"])

        # Check that we found the import
        assert len(result["imports"]) >= 1
        assert any("from functions import test_function" in imp["content"] for imp in result["imports"])

        # Check the total usages
        assert result["total_usages"] == len(result["definitions"]) + len(result["references"]) + len(result["imports"])


def test_list_code_usages_class(temp_dir_with_python_files):
    """Test finding usages of a class."""
    with patch("os.getcwd", return_value=temp_dir_with_python_files):
        result = list_code_usages("TestClass")

        # Check that we found the definition
        assert len(result["definitions"]) == 1
        assert "classes.py" in result["definitions"][0]["file_path"]
        assert "class TestClass" in result["definitions"][0]["content"]

        # Check that we found the references
        assert len(result["references"]) >= 1
        assert any("TestClass" in ref["content"] for ref in result["references"])


def test_list_code_usages_variable(temp_dir_with_python_files):
    """Test finding usages of a variable."""
    with patch("os.getcwd", return_value=temp_dir_with_python_files):
        result = list_code_usages("test_variable")

        # Check that we found the definition
        assert len(result["definitions"]) == 1
        assert "variables.py" in result["definitions"][0]["file_path"]
        assert "test_variable = 42" in result["definitions"][0]["content"]

        # Check that we found the references
        assert len(result["references"]) >= 1
        assert any("test_variable" in ref["content"] for ref in result["references"])


def test_list_code_usages_with_file_paths(temp_dir_with_python_files):
    """Test finding usages with specific file paths."""
    # Only search in functions.py
    file_path = os.path.join(temp_dir_with_python_files, "functions.py")

    with patch("os.getcwd", return_value=temp_dir_with_python_files):
        result = list_code_usages("test_function", [file_path])

        # Check that we only found usages in functions.py
        all_files = [item["file_path"] for item in result["definitions"] + result["references"] + result["imports"]]
        assert all("functions.py" in file for file in all_files)
        assert not any("imports.py" in file for file in all_files)


def test_list_code_usages_with_context():
    """Test finding usages with a context object."""
    mock_ctx = MagicMock()

    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.walk", return_value=[("/fake/path", [], ["test.py"])]),
        patch("os.path.join", return_value="/fake/path/test.py"),
        patch("builtins.open", side_effect=IOError("Test error")),
    ):
        list_code_usages("test_symbol", ctx=mock_ctx)

        # Check that the context methods were called
        mock_ctx.info.assert_called_once()
        mock_ctx.warning.assert_called_once()
        assert "Error processing file" in mock_ctx.warning.call_args[0][0]


def test_list_code_usages_with_exception():
    """Test handling exceptions when reading files."""
    with (
        patch("os.getcwd", return_value="/fake/path"),
        patch("os.walk", return_value=[("/fake/path", [], ["test.py"])]),
        patch("os.path.join", return_value="/fake/path/test.py"),
        patch("builtins.open", side_effect=IOError("Test error")),
    ):
        result = list_code_usages("test_symbol")

        # Check that we got an empty result but no exception was raised
        assert result["total_usages"] == 0
        assert len(result["definitions"]) == 0
        assert len(result["references"]) == 0
        assert len(result["imports"]) == 0
