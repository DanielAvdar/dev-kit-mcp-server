"""Parameterized tests for the grep_search module to improve test coverage."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from py_code.tools.code_analysis.grep_search import grep_search


@pytest.mark.parametrize(
    "query,include_pattern,is_regexp,matching_files,expected_matches",
    [
        # Test basic text search with matching content
        (
            "test_string",
            None,
            False,
            {"file1.py": ["line with test_string", "another line"]},
            [
                {
                    "file_path": "file1.py",
                    "matches": [{"line": 1, "content": "line with test_string"}],
                    "total_matches": 1,
                }
            ],
        ),
        # Test with include pattern
        (
            "test_string",
            "*.py",
            False,
            {"file1.py": ["line with test_string"]},  # Only include file1.py
            [
                {
                    "file_path": "file1.py",
                    "matches": [{"line": 1, "content": "line with test_string"}],
                    "total_matches": 1,
                }
            ],
        ),
        # Test with regular expression
        (
            r"test_\w+",
            None,
            True,
            {"file1.py": ["line with test_string", "another test_pattern"]},
            [
                {
                    "file_path": "file1.py",
                    "matches": [
                        {"line": 1, "content": "line with test_string"},
                        {"line": 2, "content": "another test_pattern"},
                    ],
                    "total_matches": 2,
                }
            ],
        ),
        # Test with multiple files (should be sorted by matches)
        (
            "test",
            None,
            False,
            {
                "file1.py": ["test once"],
                "file2.py": ["test", "test again"],
            },
            [
                {
                    "file_path": "file2.py",
                    "matches": [{"line": 1, "content": "test"}, {"line": 2, "content": "test again"}],
                    "total_matches": 2,
                },
                {"file_path": "file1.py", "matches": [{"line": 1, "content": "test once"}], "total_matches": 1},
            ],
        ),
        # Test with more than 10 matches in a file (should be limited to 10)
        (
            "test",
            None,
            False,
            {"file1.py": [f"test {i}" for i in range(15)]},
            [
                {
                    "file_path": "file1.py",
                    "matches": [{"line": i + 1, "content": f"test {i}"} for i in range(10)],
                    "total_matches": 15,
                }
            ],
        ),
    ],
)
def test_grep_search_matches(query, include_pattern, is_regexp, matching_files, expected_matches):
    """Test grep_search with various search scenarios."""
    ctx = MagicMock()

    with (
        patch("os.getcwd") as mock_getcwd,
        patch("glob.glob") as mock_glob,
        patch("os.walk") as mock_walk,
        patch("py_code.tools.code_analysis.grep_search.filter_binary_files") as mock_filter,
        patch("builtins.open", new_callable=mock_open) as mock_file,
    ):
        # Setup mocks
        mock_getcwd.return_value = "/fake/workspace"

        # Handle include_pattern
        if include_pattern:
            mock_glob.return_value = [f"/fake/workspace/{file}" for file in matching_files.keys()]
        else:
            mock_walk.return_value = [("/fake/workspace", [], list(matching_files.keys()))]

        # Setup file paths
        file_paths = [f"/fake/workspace/{file}" for file in matching_files.keys()]
        mock_filter.return_value = file_paths

        # Setup file content mocks
        file_contents = {}
        for file, lines in matching_files.items():
            file_contents[f"/fake/workspace/{file}"] = "\n".join(lines)

        def mock_open_func(file_path, *args, **kwargs):
            mock = MagicMock()
            mock.__enter__.return_value.readlines.return_value = file_contents[file_path].split("\n")
            return mock

        mock_file.side_effect = mock_open_func

        # Call the function
        result = grep_search(query, include_pattern, is_regexp, ctx)

        # Verify result structure
        assert "query" in result
        assert "is_regexp" in result
        assert "include_pattern" in result
        assert "results" in result
        assert "total_files" in result
        assert "limited" in result

        # Verify search parameters
        assert result["query"] == query
        assert result["is_regexp"] == is_regexp
        assert result["include_pattern"] == include_pattern

        # Verify results
        assert len(result["results"]) == len(expected_matches)
        assert result["total_files"] == len(expected_matches)

        # Check file paths and match counts
        for i, expected_file in enumerate(expected_matches):
            result_file = result["results"][i]
            assert result_file["file_path"] == expected_file["file_path"]
            assert result_file["total_matches"] == expected_file["total_matches"]

            # Check matches
            assert len(result_file["matches"]) == len(expected_file["matches"])
            for j, expected_match in enumerate(expected_file["matches"]):
                result_match = result_file["matches"][j]
                assert result_match["line"] == expected_match["line"]
                assert result_match["content"] == expected_match["content"]


@pytest.mark.parametrize(
    "query,is_regexp,ctx_warning_expected",
    [
        # Valid regex
        (r"test\d+", True, False),
        # Invalid regex that causes fallback to literal search
        (r"test[", True, True),
    ],
)
def test_grep_search_regex_handling(query, is_regexp, ctx_warning_expected):
    """Test grep_search regex handling including invalid regex."""
    ctx = MagicMock()

    with (
        patch("os.getcwd") as mock_getcwd,
        patch("os.walk") as mock_walk,
        patch("py_code.tools.code_analysis.grep_search.filter_binary_files") as mock_filter,
        patch("builtins.open", new_callable=mock_open) as mock_file,
    ):
        # Setup mocks
        mock_getcwd.return_value = "/fake/workspace"
        mock_walk.return_value = [("/fake/workspace", [], ["file1.py"])]
        mock_filter.return_value = ["/fake/workspace/file1.py"]

        # Setup file content
        mock_file().readlines.return_value = ["test123", "another line"]

        # Call the function
        grep_search(query, None, is_regexp, ctx)

        # Check if warning was called when expected
        if ctx_warning_expected:
            ctx.warning.assert_called_once()
            assert "Invalid regular expression" in ctx.warning.call_args[0][0]
        else:
            ctx.warning.assert_not_called()


@pytest.mark.parametrize(
    "encoding_error,other_exception",
    [
        # Test UnicodeDecodeError handling
        (True, False),
        # Test other exceptions
        (False, True),
    ],
)
def test_grep_search_error_handling(encoding_error, other_exception):
    """Test grep_search error handling for file reading."""
    ctx = MagicMock()

    with (
        patch("os.getcwd") as mock_getcwd,
        patch("os.walk") as mock_walk,
        patch("py_code.tools.code_analysis.grep_search.filter_binary_files") as mock_filter,
        patch("builtins.open", new_callable=mock_open) as mock_file,
    ):
        # Setup mocks
        mock_getcwd.return_value = "/fake/workspace"
        mock_walk.return_value = [("/fake/workspace", [], ["file1.py"])]
        mock_filter.return_value = ["/fake/workspace/file1.py"]

        # Setup file reading exceptions
        if encoding_error:
            mock_file.side_effect = UnicodeDecodeError("utf-8", b"test", 0, 1, "invalid start byte")
        elif other_exception:
            mock_file.side_effect = IOError("Test IO error")

        # Call the function
        result = grep_search("test", None, False, ctx)

        # Verify result structure
        assert "query" in result
        assert "results" in result

        # Should have no results due to error
        assert len(result["results"]) == 0
        assert result["total_files"] == 0

        # Check warning was logged for other exceptions
        if other_exception:
            ctx.warning.assert_called_once()
            assert "Error processing file" in ctx.warning.call_args[0][0]
        else:
            # No warning for UnicodeDecodeError as these are expected and silently skipped
            ctx.warning.assert_not_called()


@pytest.mark.parametrize(
    "total_results,max_display,expected_limited",
    [
        # Test with fewer results than limit
        (5, 20, False),
        # Test with more results than limit
        (25, 20, True),
    ],
)
def test_grep_search_result_limiting(total_results, max_display, expected_limited):
    """Test grep_search limiting of results."""
    ctx = MagicMock()

    with (
        patch("os.getcwd") as mock_getcwd,
        patch("os.walk") as mock_walk,
        patch("py_code.tools.code_analysis.grep_search.filter_binary_files") as mock_filter,
        patch("builtins.open", new_callable=mock_open) as mock_file,
    ):
        # Setup mocks
        mock_getcwd.return_value = "/fake/workspace"

        # Generate file paths and mock walk results
        file_paths = [f"/fake/workspace/file{i}.py" for i in range(total_results)]
        mock_walk.return_value = [("/fake/workspace", [], [f"file{i}.py" for i in range(total_results)])]
        mock_filter.return_value = file_paths

        # Set up file content for all files to contain the search string
        mock_file().readlines.return_value = ["test string"]

        # Call the function
        result = grep_search("test", None, False, ctx)

        # Verify limiting
        assert result["limited"] == expected_limited
        assert len(result["results"]) <= max_display
        # The total_files should be the total number of files with matches, not limited by display
        # This is the actual behavior of the grep_search function
        assert result["total_files"] == total_results
