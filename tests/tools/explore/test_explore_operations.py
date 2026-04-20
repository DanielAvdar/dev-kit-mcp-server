"""Tests for exploration tools."""

import os

import pytest

from dev_kit_mcp_server.tools import ReadLinesOperation, SearchFilesOperation, SearchRegexOperation, SearchTextOperation


@pytest.fixture(scope="function")
def temp_root_dir(temp_dir) -> str:
    """Create a temporary directory for testing."""
    return temp_dir


@pytest.fixture
def search_files_operation(temp_root_dir: str) -> SearchFilesOperation:
    """Create a SearchFilesOperation instance with a temporary root directory."""
    return SearchFilesOperation(root_dir=temp_root_dir)


@pytest.fixture
def search_text_operation(temp_root_dir: str) -> SearchTextOperation:
    """Create a SearchTextOperation instance with a temporary root directory."""
    return SearchTextOperation(root_dir=temp_root_dir)


@pytest.fixture
def search_regex_operation(temp_root_dir: str) -> SearchRegexOperation:
    """Create a SearchRegexOperation instance with a temporary root directory."""
    return SearchRegexOperation(root_dir=temp_root_dir)


@pytest.fixture
def read_lines_operation(temp_root_dir: str) -> ReadLinesOperation:
    """Create a ReadLinesOperation instance with a temporary root directory."""
    return ReadLinesOperation(root_dir=temp_root_dir)


@pytest.fixture
def setup_test_files(temp_root_dir: str) -> dict:
    """Set up test files and directories for exploration tests."""
    # Create directory structure
    subdir = os.path.join(temp_root_dir, "subdir")
    os.makedirs(subdir)

    # Create various test files
    files = {}

    # Python file
    files["python_file"] = os.path.join(temp_root_dir, "test_script.py")
    with open(files["python_file"], "w") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("def hello_world():\n")
        f.write("    print('Hello, World!')\n")
        f.write("    return 42\n")
        f.write("\n")
        f.write("if __name__ == '__main__':\n")
        f.write("    hello_world()\n")

    # Text file with multiple lines
    files["text_file"] = os.path.join(temp_root_dir, "sample.txt")
    with open(files["text_file"], "w") as f:
        f.write("Line 1: This is the first line\n")
        f.write("Line 2: This contains the word 'search'\n")
        f.write("Line 3: Another line here\n")
        f.write("Line 4: Final line with search term\n")
        f.write("Line 5: Last line\n")

    # Markdown file in subdirectory
    files["markdown_file"] = os.path.join(subdir, "README.md")
    with open(files["markdown_file"], "w") as f:
        f.write("# Test README\n")
        f.write("\n")
        f.write("This is a test markdown file.\n")
        f.write("It contains some **search** content.\n")
        f.write("\n")
        f.write("## Section\n")
        f.write("More content here.\n")

    # JSON file
    files["json_file"] = os.path.join(temp_root_dir, "data.json")
    with open(files["json_file"], "w") as f:
        f.write("{\n")
        f.write('  "name": "test",\n')
        f.write('  "search": true,\n')
        f.write('  "value": 123\n')
        f.write("}\n")

    # File with special characters in name
    files["special_file"] = os.path.join(temp_root_dir, "test-file_v2.txt")
    with open(files["special_file"], "w") as f:
        f.write("Special file content\n")

    return files


class TestSearchFilesOperation:
    """Test the SearchFilesOperation class."""

    @pytest.mark.asyncio
    async def test_search_files_basic(self, search_files_operation, setup_test_files):
        """Test basic file search functionality."""
        result = await search_files_operation(pattern=".*\\.py$")

        assert result["status"] == "success"
        assert result["matches_found"] == 1
        assert "test_script.py" in result["content"]
        assert not result["truncated"]

    @pytest.mark.asyncio
    async def test_search_files_multiple_matches(self, search_files_operation, setup_test_files):
        """Test file search with multiple matches."""
        result = await search_files_operation(pattern=".*\\.txt$")

        assert result["status"] == "success"
        assert result["matches_found"] >= 2  # sample.txt and test-file_v2.txt
        assert "sample.txt" in result["content"]
        assert "test-file_v2.txt" in result["content"]

    @pytest.mark.asyncio
    async def test_search_files_no_matches(self, search_files_operation, setup_test_files):
        """Test file search with no matches."""
        result = await search_files_operation(pattern=".*\\.nonexistent$")

        assert result["status"] == "success"
        assert result["matches_found"] == 0
        assert "No files found" in result["content"]

    @pytest.mark.asyncio
    async def test_search_files_with_root(self, search_files_operation, setup_test_files):
        """Test file search with specific root directory."""
        result = await search_files_operation(pattern=".*\\.md$", root="subdir")

        assert result["status"] == "success"
        assert result["matches_found"] == 1
        assert "README.md" in result["content"]

    @pytest.mark.asyncio
    async def test_search_files_max_chars(self, search_files_operation, setup_test_files):
        """Test file search with character limit."""
        result = await search_files_operation(pattern=".*", max_chars=50)

        assert result["status"] == "success"
        assert result["total_chars"] > 50
        assert result["truncated"]
        assert len(result["content"]) == 50

    @pytest.mark.asyncio
    async def test_search_files_invalid_regex(self, search_files_operation, setup_test_files):
        """Test file search with invalid regex pattern."""
        result = await search_files_operation(pattern="[invalid")

        assert result["status"] == "error"
        assert "Invalid regex pattern" in result["message"]

    @pytest.mark.asyncio
    async def test_search_files_invalid_root(self, search_files_operation, setup_test_files):
        """Test file search with invalid root directory."""
        result = await search_files_operation(pattern=".*", root="nonexistent")

        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    @pytest.mark.asyncio
    async def test_search_files_outside_root(self, search_files_operation, setup_test_files):
        """Test file search with root outside project directory."""
        result = await search_files_operation(pattern=".*", root="../..")

        assert result["status"] == "error"
        assert "not within the root directory" in result["message"]


class TestSearchTextOperation:
    """Test the SearchTextOperation class."""

    @pytest.mark.asyncio
    async def test_search_text_basic(self, search_text_operation, setup_test_files):
        """Test basic text search functionality."""
        result = await search_text_operation(pattern="search")

        assert result["status"] == "success"
        assert result["matches_found"] >= 3  # Should find in sample.txt, README.md, data.json
        assert "search" in result["content"]
        assert not result["truncated"]

    @pytest.mark.asyncio
    async def test_search_text_specific_files(self, search_text_operation, setup_test_files):
        """Test text search in specific files."""
        result = await search_text_operation(pattern="search", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 2  # Two lines in sample.txt contain "search"
        assert "sample.txt:2:" in result["content"]
        assert "sample.txt:4:" in result["content"]

    @pytest.mark.asyncio
    async def test_search_text_with_context(self, search_text_operation, setup_test_files):
        """Test text search with context lines."""
        result = await search_text_operation(pattern="search", files=["sample.txt"], context=1)

        assert result["status"] == "success"
        assert result["matches_found"] == 2
        assert ">>>" in result["content"]  # Context marker
        assert "1:" in result["content"]  # Context line before first match
        assert "3:" in result["content"]  # Context line after first match

    @pytest.mark.asyncio
    async def test_search_text_case_sensitive(self, search_text_operation, setup_test_files):
        """Test text search is case sensitive by default."""
        result = await search_text_operation(pattern="SEARCH", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 0

    @pytest.mark.asyncio
    async def test_search_text_regex_pattern(self, search_text_operation, setup_test_files):
        """Test text search with regex pattern."""
        result = await search_text_operation(pattern="Line \\d+:", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 5  # All lines in sample.txt match

    @pytest.mark.asyncio
    async def test_search_text_no_matches(self, search_text_operation, setup_test_files):
        """Test text search with no matches."""
        result = await search_text_operation(pattern="nonexistent_pattern")

        assert result["status"] == "success"
        assert result["matches_found"] == 0
        assert "No matches found" in result["content"]

    @pytest.mark.asyncio
    async def test_search_text_max_chars(self, search_text_operation, setup_test_files):
        """Test text search with character limit."""
        result = await search_text_operation(pattern=".", max_chars=100)

        assert result["status"] == "success"
        assert result["total_chars"] > 100
        assert result["truncated"]
        assert len(result["content"]) == 100

    @pytest.mark.asyncio
    async def test_search_text_invalid_regex(self, search_text_operation, setup_test_files):
        """Test text search with invalid regex pattern."""
        result = await search_text_operation(pattern="[invalid")

        assert result["status"] == "error"
        assert "Invalid regex pattern" in result["message"]

    @pytest.mark.asyncio
    async def test_search_text_invalid_file(self, search_text_operation, setup_test_files):
        """Test text search with invalid file."""
        result = await search_text_operation(pattern="test", files=["nonexistent.txt"])

        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    @pytest.mark.asyncio
    async def test_search_text_outside_root(self, search_text_operation, setup_test_files):
        """Test text search with file outside root directory."""
        result = await search_text_operation(pattern="test", files=["../../etc/passwd"])

        assert result["status"] == "error"
        assert "not within the root directory" in result["message"]


class TestReadLinesOperation:
    """Test the ReadLinesOperation class."""

    @pytest.mark.asyncio
    async def test_read_lines_entire_file(self, read_lines_operation, setup_test_files):
        """Test reading entire file."""
        result = await read_lines_operation(file_path="sample.txt")

        assert result["status"] == "success"
        assert result["lines_returned"] == 5
        assert result["total_lines_in_file"] == 5
        assert "Line 1:" in result["content"]
        assert "Line 5:" in result["content"]
        assert not result["truncated"]

    @pytest.mark.asyncio
    async def test_read_lines_range(self, read_lines_operation, setup_test_files):
        """Test reading specific line range."""
        result = await read_lines_operation(file_path="sample.txt", start=2, end=4)

        assert result["status"] == "success"
        assert result["lines_returned"] == 3
        assert result["actual_start"] == 2
        assert result["actual_end"] == 4
        assert "Line 2:" in result["content"]
        assert "Line 3:" in result["content"]
        assert "Line 4:" in result["content"]
        assert "Line 1:" not in result["content"]
        assert "Line 5:" not in result["content"]

    @pytest.mark.asyncio
    async def test_read_lines_start_only(self, read_lines_operation, setup_test_files):
        """Test reading from specific start line to end."""
        result = await read_lines_operation(file_path="sample.txt", start=3)

        assert result["status"] == "success"
        assert result["lines_returned"] == 3
        assert result["actual_start"] == 3
        assert result["actual_end"] == 5
        assert "Line 3:" in result["content"]
        assert "Line 5:" in result["content"]

    @pytest.mark.asyncio
    async def test_read_lines_end_only(self, read_lines_operation, setup_test_files):
        """Test reading from start to specific end line."""
        result = await read_lines_operation(file_path="sample.txt", end=3)

        assert result["status"] == "success"
        assert result["lines_returned"] == 3
        assert result["actual_start"] == 1
        assert result["actual_end"] == 3
        assert "Line 1:" in result["content"]
        assert "Line 3:" in result["content"]
        assert "Line 4:" not in result["content"]

    @pytest.mark.asyncio
    async def test_read_lines_out_of_bounds(self, read_lines_operation, setup_test_files):
        """Test reading lines beyond file length."""
        result = await read_lines_operation(file_path="sample.txt", start=10, end=20)

        assert result["status"] == "success"
        assert result["lines_returned"] == 0
        assert "No lines to display" in result["content"]

    @pytest.mark.asyncio
    async def test_read_lines_negative_start(self, read_lines_operation, setup_test_files):
        """Test reading with negative start line."""
        result = await read_lines_operation(file_path="sample.txt", start=-1)

        assert result["status"] == "error"
        assert "Start line must be at least 1" in result["message"]

    @pytest.mark.asyncio
    async def test_read_lines_end_before_start(self, read_lines_operation, setup_test_files):
        """Test reading with end line before start line."""
        result = await read_lines_operation(file_path="sample.txt", start=4, end=2)

        assert result["status"] == "error"
        assert "End line must be greater than or equal to start line" in result["message"]

    @pytest.mark.asyncio
    async def test_read_lines_max_chars(self, read_lines_operation, setup_test_files):
        """Test reading with character limit."""
        result = await read_lines_operation(file_path="sample.txt", max_chars=50)

        assert result["status"] == "success"
        assert result["total_chars"] > 50
        assert result["truncated"]
        assert len(result["content"]) == 50

    @pytest.mark.asyncio
    async def test_read_lines_nonexistent_file(self, read_lines_operation, setup_test_files):
        """Test reading nonexistent file."""
        result = await read_lines_operation(file_path="nonexistent.txt")

        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    @pytest.mark.asyncio
    async def test_read_lines_directory(self, read_lines_operation, setup_test_files):
        """Test reading a directory instead of file."""
        result = await read_lines_operation(file_path="subdir")

        assert result["status"] == "error"
        assert "directory, not a file" in result["message"]

    @pytest.mark.asyncio
    async def test_read_lines_outside_root(self, read_lines_operation, setup_test_files):
        """Test reading file outside root directory."""
        result = await read_lines_operation(file_path="../../etc/passwd")

        assert result["status"] == "error"
        assert "not within the root directory" in result["message"]

    @pytest.mark.asyncio
    async def test_read_lines_subdirectory(self, read_lines_operation, setup_test_files):
        """Test reading file in subdirectory."""
        subdir_path = os.path.join("subdir", "README.md")
        result = await read_lines_operation(file_path=subdir_path, start=1, end=3)

        assert result["status"] == "success"
        assert result["lines_returned"] == 3
        assert "# Test README" in result["content"]
        assert os.path.normpath(subdir_path) in result["content"]


class TestSearchRegexOperation:
    """Test the SearchRegexOperation class."""

    @pytest.mark.asyncio
    async def test_search_regex_single_file(self, search_regex_operation, setup_test_files):
        """Test regex search in a single file."""
        result = await search_regex_operation(pattern="search", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 2  # Two lines in sample.txt contain "search"
        assert result["files_searched"] == 1
        assert "sample.txt:2: Line 2: This contains the word 'search'" in result["content"]
        assert "sample.txt:4: Line 4: Final line with search term" in result["content"]
        assert not result["truncated"]

    @pytest.mark.asyncio
    async def test_search_regex_multiple_files(self, search_regex_operation, setup_test_files):
        """Test regex search across multiple files."""
        result = await search_regex_operation(pattern="search", files=["sample.txt", "subdir/README.md", "data.json"])

        assert result["status"] == "success"
        assert result["matches_found"] >= 3  # Should find in all three files
        assert result["files_searched"] == 3
        assert "search" in result["content"]
        assert not result["truncated"]

    @pytest.mark.asyncio
    async def test_search_regex_regex_pattern(self, search_regex_operation, setup_test_files):
        """Test regex search with regex pattern."""
        result = await search_regex_operation(pattern="Line \\d+:", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 5  # All lines in sample.txt match this pattern

    @pytest.mark.asyncio
    async def test_search_regex_no_matches(self, search_regex_operation, setup_test_files):
        """Test regex search with no matches."""
        result = await search_regex_operation(pattern="nonexistent_pattern", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 0
        assert "No matches found" in result["content"]

    @pytest.mark.asyncio
    async def test_search_regex_invalid_regex(self, search_regex_operation, setup_test_files):
        """Test regex search with invalid regex pattern."""
        result = await search_regex_operation(pattern="[invalid", files=["sample.txt"])

        assert result["status"] == "error"
        assert "Invalid regex pattern" in result["message"]

    @pytest.mark.asyncio
    async def test_search_regex_invalid_file(self, search_regex_operation, setup_test_files):
        """Test regex search with invalid file."""
        result = await search_regex_operation(pattern="test", files=["nonexistent.txt"])

        assert result["status"] == "error"
        assert "does not exist" in result["message"]

    @pytest.mark.asyncio
    async def test_search_regex_outside_root(self, search_regex_operation, setup_test_files):
        """Test regex search with file outside root directory."""
        result = await search_regex_operation(pattern="test", files=["../../etc/passwd"])

        assert result["status"] == "error"
        assert "not within the root directory" in result["message"]

    @pytest.mark.asyncio
    async def test_search_regex_empty_files_list(self, search_regex_operation, setup_test_files):
        """Test regex search with empty files list."""
        result = await search_regex_operation(pattern="test", files=[])

        assert result["status"] == "error"
        assert "Files list cannot be empty" in result["message"]

    @pytest.mark.asyncio
    async def test_search_regex_max_chars(self, search_regex_operation, setup_test_files):
        """Test regex search with character limit."""
        result = await search_regex_operation(pattern=".", files=["sample.txt"], max_chars=100)

        assert result["status"] == "success"
        assert result["total_chars"] > 100
        assert result["truncated"]
        assert len(result["content"]) == 100

    @pytest.mark.asyncio
    async def test_search_regex_case_sensitive(self, search_regex_operation, setup_test_files):
        """Test regex search is case sensitive by default."""
        result = await search_regex_operation(pattern="SEARCH", files=["sample.txt"])

        assert result["status"] == "success"
        assert result["matches_found"] == 0

    @pytest.mark.asyncio
    async def test_search_regex_directory_not_file(self, search_regex_operation, setup_test_files):
        """Test regex search with directory instead of file."""
        result = await search_regex_operation(pattern="test", files=["subdir"])

        assert result["status"] == "error"
        assert "not a file" in result["message"]
