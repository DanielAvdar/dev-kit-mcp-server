"""Parameterized tests for the read_file module to improve test coverage."""

import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from py_code.tools.read_file import read_file


@pytest.mark.parametrize(
    "file_path,exists,is_file,expected_error",
    [
        # Test with file that exists
        ("/fake/path/to/file.txt", True, True, None),
        # Test with non-existent file
        ("/fake/path/to/nonexistent.txt", False, False, "File not found"),
        # Test with directory instead of file
        ("/fake/path/to/directory", True, False, "Not a file"),
    ],
)
def test_read_file_validation(file_path, exists, is_file, expected_error):
    """Test file validation in read_file function."""
    ctx = MagicMock()
    
    with patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile") as mock_isfile, \
         patch("os.path.isabs") as mock_isabs, \
         patch("py_code.tools.read_file.normalize_path") as mock_normalize, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        
        # Configure mocks
        mock_exists.return_value = exists
        mock_isfile.return_value = is_file
        mock_isabs.return_value = True
        mock_normalize.return_value = file_path
        
        if exists and is_file:
            # Setup mock file content
            mock_file().readlines.return_value = ["Line 1\n", "Line 2\n", "Line 3\n"]
            
            # Mock os.stat
            with patch("os.stat") as mock_stat:
                mock_stat.return_value = MagicMock(st_size=100)
                
                # Call the function
                result = read_file(file_path, ctx=ctx)
                
                # Check result
                assert result["file_path"] == file_path
                assert "content" in result
                assert "error" not in result
                assert result["total_lines"] == 3
                assert result["size_bytes"] == 100
        else:
            # Call the function
            result = read_file(file_path, ctx=ctx)
            
            # Check error handling
            assert "error" in result
            assert expected_error in result["error"]
            assert result["file_path"] == file_path
        
        # Verify context calls
        ctx.info.assert_called_once()


@pytest.mark.parametrize(
    "is_absolute_path,normalized_path",
    [
        # Test with absolute path
        (True, "/normalized/path/file.txt"),
        # Test with relative path
        (False, "/fake/working/dir/relative/path/file.txt"),
    ],
)
def test_read_file_path_handling(is_absolute_path, normalized_path):
    """Test path handling in read_file function."""
    ctx = MagicMock()
    file_path = "/path/to/file.txt" if is_absolute_path else "relative/path/file.txt"
    
    with patch("os.path.isabs") as mock_isabs, \
         patch("os.getcwd") as mock_getcwd, \
         patch("os.path.join") as mock_join, \
         patch("py_code.tools.read_file.normalize_path") as mock_normalize, \
         patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        
        # Configure mocks
        mock_isabs.return_value = is_absolute_path
        mock_getcwd.return_value = "/fake/working/dir"
        mock_join.return_value = "/fake/working/dir/relative/path/file.txt"
        mock_normalize.return_value = normalized_path
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Setup mock file content
        mock_file().readlines.return_value = ["Line 1\n", "Line 2\n", "Line 3\n"]
        
        # Mock os.stat
        with patch("os.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=100)
            
            # Call the function
            result = read_file(file_path, ctx=ctx)
            
            # Check result
            assert result["file_path"] == normalized_path
            assert "content" in result
            assert "error" not in result
        
        # Verify that path normalization happened
        mock_normalize.assert_called_once()
        
        # For relative paths, verify they're joined with cwd
        if not is_absolute_path:
            mock_getcwd.assert_called_once()
            mock_join.assert_called_once()


@pytest.mark.parametrize(
    "start_line,end_line,total_lines,expected_start,expected_end",
    [
        # Test with normal range
        (0, 1, 3, 0, 1),
        # Test with end line None (should read until end)
        (1, None, 3, 1, 2),
        # Test with start line > end line (should adjust)
        (2, 1, 3, 2, 2),
        # Test with negative start line (should adjust to 0)
        (-1, 1, 3, 0, 1),
        # Test with start and end beyond file size (should adjust)
        (5, 10, 3, 2, 2),
    ],
)
def test_read_file_line_range_handling(start_line, end_line, total_lines, expected_start, expected_end):
    """Test line range handling in read_file function."""
    ctx = MagicMock()
    file_path = "/path/to/file.txt"
    
    with patch("os.path.isabs") as mock_isabs, \
         patch("py_code.tools.read_file.normalize_path") as mock_normalize, \
         patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        
        # Configure mocks
        mock_isabs.return_value = True
        mock_normalize.return_value = file_path
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Create mock lines
        mock_lines = [f"Line {i+1}\n" for i in range(total_lines)]
        mock_file().readlines.return_value = mock_lines
        
        # Mock os.stat
        with patch("os.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=100)
            
            # Call the function
            result = read_file(file_path, start_line, end_line, ctx=ctx)
            
            # Check result
            assert result["file_path"] == file_path
            assert "content" in result
            assert "error" not in result
            assert result["start_line"] == expected_start + 1  # +1 because it's converted to 1-based
            assert result["end_line"] == expected_end + 1      # +1 because it's converted to 1-based
            
            # Verify content is correct based on adjusted line ranges
            expected_content = ''.join(mock_lines[expected_start:expected_end+1])
            assert result["content"] == expected_content


@pytest.mark.parametrize(
    "total_lines,expected_outline",
    [
        # Test with small file (should generate line-by-line outline)
        (10, ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5", "Line 6", "Line 7", "Line 8", "Line 9", "Line 10"]),
        # Test with large file (should generate ranged outline)
        (120, ["Lines 1-12", "Lines 13-24", "Lines 25-36", "Lines 37-48", "Lines 49-60", 
               "Lines 61-72", "Lines 73-84", "Lines 85-96", "Lines 97-108", "Lines 109-120"]),
        # Test with reading entire file (should not have outline)
        (3, None),  # When reading all lines, outline should be None
    ],
)
def test_read_file_outline_generation(total_lines, expected_outline):
    """Test outline generation in read_file function."""
    ctx = MagicMock()
    file_path = "/path/to/file.txt"
    
    with patch("os.path.isabs") as mock_isabs, \
         patch("py_code.tools.read_file.normalize_path") as mock_normalize, \
         patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        
        # Configure mocks
        mock_isabs.return_value = True
        mock_normalize.return_value = file_path
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # Create mock lines
        mock_lines = [f"Line {i+1}\n" for i in range(total_lines)]
        mock_file().readlines.return_value = mock_lines
        
        # Mock os.stat
        with patch("os.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=total_lines * 10)
            
            if expected_outline is None:
                # Test reading the entire file (no outline)
                result = read_file(file_path, 0, None, ctx=ctx)
            else:
                # Test reading a partial file (should have outline)
                result = read_file(file_path, 0, 0, ctx=ctx)
            
            # Check outline
            if expected_outline is None:
                assert result["outline"] is None
            else:
                assert "outline" in result
                assert len(result["outline"]) == len(expected_outline)
                for i, outline_item in enumerate(expected_outline):
                    assert outline_item in result["outline"][i]


@pytest.mark.parametrize(
    "encoding_error,expected_error",
    [
        # Test with UnicodeDecodeError (should try latin-1)
        (UnicodeDecodeError("utf-8", b"test", 0, 1, "invalid start byte"), None),
        # Test with other exception (should fail)
        (IOError("File I/O error"), "Error reading file: File I/O error"),
    ],
)
def test_read_file_encoding_handling(encoding_error, expected_error):
    """Test encoding error handling in read_file function."""
    ctx = MagicMock()
    file_path = "/path/to/file.txt"
    
    with patch("os.path.isabs") as mock_isabs, \
         patch("py_code.tools.read_file.normalize_path") as mock_normalize, \
         patch("os.path.exists") as mock_exists, \
         patch("os.path.isfile") as mock_isfile, \
         patch("builtins.open", new_callable=mock_open) as mock_file:
        
        # Configure mocks
        mock_isabs.return_value = True
        mock_normalize.return_value = file_path
        mock_exists.return_value = True
        mock_isfile.return_value = True
        
        # First time open is called, raise encoding error
        mock_file.side_effect = [encoding_error]
        
        if isinstance(encoding_error, UnicodeDecodeError):
            # If it's UnicodeDecodeError, setup second open with latin-1 encoding
            second_open = MagicMock()
            second_open.readlines.return_value = ["Line 1\n", "Line 2\n"]
            mock_file.side_effect = [encoding_error, second_open]
            
            # Mock os.stat
            with patch("os.stat") as mock_stat:
                mock_stat.return_value = MagicMock(st_size=100)
                
                # Call the function
                result = read_file(file_path, ctx=ctx)
                
                # Check result for latin-1 encoding fallback
                assert "error" not in result
                assert "encoding" in result
                assert result["encoding"] == "latin-1"
                assert "content" in result
        else:
            # Call the function
            result = read_file(file_path, ctx=ctx)
            
            # Check error handling
            assert "error" in result
            assert expected_error in result["error"]
            assert result["file_path"] == file_path

