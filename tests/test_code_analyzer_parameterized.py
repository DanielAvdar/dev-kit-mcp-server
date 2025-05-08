"""Parameterized tests for the code_analyzer module to improve test coverage."""

import os
from unittest.mock import MagicMock, patch

import pytest

from py_code.tools.code_analyzer import analyze_code_files, parse_ast_files


@pytest.mark.parametrize(
    "pattern,root_dir,ignore_gitignore,paths_result,python_files,expected_result_keys",
    [
        # Test with valid pattern and files
        (
            "*.py",
            "/fake/root",
            False,
            ["/fake/root/test.py", "/fake/root/example.py"],
            ["/fake/root/test.py", "/fake/root/example.py"],
            ["pattern", "root_dir", "file_count", "files", "summary"],
        ),
        # Test with pattern that doesn't match any files
        (
            "nonexistent*.py",
            "/fake/root",
            False,
            [],
            [],
            ["error", "pattern", "root_dir"],
        ),
        # Test with pattern that matches files but none are Python files
        (
            "*.txt",
            "/fake/root",
            False,
            ["/fake/root/file.txt"],
            [],
            ["error", "pattern", "root_dir"],
        ),
    ],
)
def test_parse_ast_files_with_different_patterns(
    pattern, root_dir, ignore_gitignore, paths_result, python_files, expected_result_keys
):
    """Test parse_ast_files with different patterns and configurations."""
    ctx = MagicMock()
    
    with patch("py_code.tools.code_analyzer.resolve_path_pattern") as mock_resolve, \
         patch("py_code.tools.code_analyzer.find_python_files") as mock_find, \
         patch("py_code.tools.code_analyzer.parse_gitignore") as mock_gitignore, \
         patch("py_code.tools.code_analyzer.open", create=True) as mock_open, \
         patch("py_code.tools.code_analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        
        # Configure mocks
        mock_resolve.return_value = paths_result
        mock_gitignore.return_value = ["*.pyc", "__pycache__"]
        
        if paths_result and python_files:
            mock_find.return_value = python_files
            
            # Setup mock file content
            mock_file = MagicMock()
            mock_file.__enter__.return_value.read.return_value = "def test(): pass"
            mock_open.return_value = mock_file
            
            # Setup mock AST analysis result
            mock_parse_ast.return_value = {
                "functions": [{"name": "test"}],
                "classes": [],
                "imports": [],
                "variables": []
            }
        else:
            mock_find.return_value = python_files
        
        # Call the function
        result = parse_ast_files(pattern, root_dir, ignore_gitignore, ctx)
        
        # Verify result structure
        assert all(key in result for key in expected_result_keys)
        
        if paths_result and python_files:
            # If files were found, verify content
            assert result["file_count"] == len(python_files)
            assert "summary" in result
            assert "total_files" in result["summary"]
            assert "total_functions" in result["summary"]
            assert result["summary"]["total_functions"] == len(python_files)
        elif not paths_result:
            # If no paths matched the pattern
            assert "error" in result
            assert "No files found matching pattern" in result["error"]
        else:
            # If paths matched but no Python files
            assert "error" in result
            assert "No Python files found matching pattern" in result["error"]
        
        # Verify context calls
        if paths_result and python_files:
            ctx.info.assert_called()


@pytest.mark.parametrize(
    "pattern,root_dir,ignore_gitignore,include_tokens,max_files_exceeded",
    [
        # Test with normal number of files and include_tokens=True
        ("*.py", "/fake/root", False, True, False),
        # Test with normal number of files and include_tokens=False
        ("*.py", "/fake/root", False, False, False),
        # Test with excessive number of files that gets limited
        ("*.py", "/fake/root", False, True, True),
    ],
)
def test_analyze_code_files(pattern, root_dir, ignore_gitignore, include_tokens, max_files_exceeded):
    """Test analyze_code_files with different parameters."""
    ctx = MagicMock()
    
    with patch("py_code.tools.code_analyzer.resolve_path_pattern") as mock_resolve, \
         patch("py_code.tools.code_analyzer.find_python_files") as mock_find, \
         patch("py_code.tools.code_analyzer.parse_gitignore") as mock_gitignore, \
         patch("py_code.tools.code_analyzer.open", create=True) as mock_open, \
         patch("py_code.tools.code_analyzer.CodeAnalyzer.analyze") as mock_analyze, \
         patch("py_code.tools.code_analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast:
        
        # Configure mocks
        python_files = [f"/fake/root/file{i}.py" for i in range(1, 60 if max_files_exceeded else 5)]
        mock_resolve.return_value = ["/fake/root"]
        mock_gitignore.return_value = ["*.pyc", "__pycache__"]
        mock_find.return_value = python_files
        
        # Setup mock file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "def test(): pass"
        mock_open.return_value = mock_file
        
        # Setup mock analysis results
        mock_analyze.return_value = {
            "ast_analysis": {
                "functions": [{"name": "test"}],
                "classes": [],
                "imports": [],
                "variables": []
            },
            "tokens": [{"type": "NAME", "string": "def"}]
        }
        
        mock_parse_ast.return_value = {
            "functions": [{"name": "test"}],
            "classes": [],
            "imports": [],
            "variables": []
        }
        
        # Call the function
        result = analyze_code_files(pattern, root_dir, ignore_gitignore, include_tokens, ctx)
        
        # Verify result structure
        assert "pattern" in result
        assert "root_dir" in result
        assert "file_count" in result
        assert "files" in result
        assert "summary" in result
        
        # If files were limited, check the warning
        if max_files_exceeded:
            ctx.warning.assert_called()
            assert result["file_count"] <= 50  # Max files limit
        else:
            assert result["file_count"] == len(python_files)
        
        # Verify the correct analyzer method was called based on include_tokens
        if include_tokens:
            mock_analyze.assert_called()
            assert not mock_parse_ast.called
        else:
            mock_parse_ast.assert_called()
            assert not mock_analyze.called


@pytest.mark.parametrize(
    "pattern,root_dir,paths_result,error_expected",
    [
        # Test with non-existent paths
        ("nonexistent*.py", "/fake/root", [], True),
        # Test with Python syntax error in file
        ("bad_syntax.py", "/fake/root", ["/fake/root/bad_syntax.py"], True),
    ],
)
def test_analyze_code_files_errors(pattern, root_dir, paths_result, error_expected):
    """Test error handling in analyze_code_files."""
    ctx = MagicMock()
    
    with patch("py_code.tools.code_analyzer.resolve_path_pattern") as mock_resolve, \
         patch("py_code.tools.code_analyzer.find_python_files") as mock_find, \
         patch("py_code.tools.code_analyzer.parse_gitignore") as mock_gitignore, \
         patch("py_code.tools.code_analyzer.open", create=True) as mock_open, \
         patch("py_code.tools.code_analyzer.CodeAnalyzer.analyze") as mock_analyze:
        
        # Configure mocks
        mock_resolve.return_value = paths_result
        mock_gitignore.return_value = []
        
        if paths_result:
            mock_find.return_value = paths_result
            
            # Setup file with syntax error
            mock_file = MagicMock()
            mock_file.__enter__.return_value.read.return_value = "def test() syntax error"
            mock_open.return_value = mock_file
            
            # Make the analyzer raise an exception
            mock_analyze.side_effect = SyntaxError("invalid syntax")
        else:
            mock_find.return_value = []
        
        # Call the function
        result = analyze_code_files(pattern, root_dir, False, True, ctx)
        
        # Verify error handling
        if not paths_result:
            assert "error" in result
            assert "No files found matching pattern" in result["error"]
        else:
            assert "errors" in result
            assert len(result["errors"]) > 0
            ctx.warning.assert_called()


@pytest.mark.parametrize(
    "root_dir,pattern,gitignore_exists",
    [
        # Test with existing .gitignore
        ("/fake/root", "*.py", True),
        # Test without .gitignore
        ("/fake/root", "*.py", False),
    ],
)
def test_gitignore_handling(root_dir, pattern, gitignore_exists):
    """Test how .gitignore patterns are handled."""
    ctx = MagicMock()
    
    with patch("py_code.tools.code_analyzer.parse_gitignore") as mock_gitignore, \
         patch("py_code.tools.code_analyzer.resolve_path_pattern") as mock_resolve, \
         patch("py_code.tools.code_analyzer.find_python_files") as mock_find, \
         patch("py_code.tools.code_analyzer.open", create=True) as mock_open, \
         patch("py_code.tools.code_analyzer.CodeAnalyzer.parse_ast") as mock_parse_ast, \
         patch("os.path.exists") as mock_exists:
        
        # Configure mocks
        mock_exists.return_value = gitignore_exists
        mock_gitignore.return_value = ["*.pyc", "__pycache__"] if gitignore_exists else []
        mock_resolve.return_value = ["/fake/root/file.py"]
        mock_find.return_value = ["/fake/root/file.py"]
        
        # Setup file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "def test(): pass"
        mock_open.return_value = mock_file
        
        # Setup AST result
        mock_parse_ast.return_value = {
            "functions": [{"name": "test"}],
            "classes": [],
            "imports": [],
            "variables": []
        }
        
        # Call the function
        parse_ast_files(pattern, root_dir, False, ctx)
        
        # Verify gitignore handling
        if gitignore_exists:
            mock_gitignore.assert_called_once()
            assert ctx.info.call_count >= 2  # Both for pattern and gitignore info
        else:
            mock_gitignore.assert_called_once()
            assert ctx.info.call_count >= 1  # At least for pattern info

