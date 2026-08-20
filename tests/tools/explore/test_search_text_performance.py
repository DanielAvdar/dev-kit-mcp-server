"""Performance tests for SearchTextOperation async implementation."""

import asyncio
import tempfile
import time
from pathlib import Path

import git
import pytest

from dev_kit_mcp_server.tools import SearchTextOperation


@pytest.fixture
def large_test_setup():
    """Create a test environment with many files for performance testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize git repository
        git.Repo.init(temp_dir)

        # Create multiple files with varying content
        files_created = []

        # Create 50 files with content to search
        for i in range(50):
            file_path = Path(temp_dir) / f"test_file_{i:03d}.py"
            with open(file_path, "w") as f:
                f.write(f"# Test file {i}\n")
                f.write("import os\n")
                f.write("import sys\n")
                f.write(f"def function_{i}():\n")
                f.write(f'    """This is function {i}"""\n')
                f.write(f"    return {i}\n")
                f.write("\n")
                f.write("if __name__ == '__main__':\n")
                f.write(f"    print(function_{i}())\n")
                # Add some random content to make files different sizes
                for j in range(i % 10):
                    f.write(f"# Additional line {j} in file {i}\n")
            files_created.append(str(file_path))

        # Also create some larger files
        for i in range(5):
            file_path = Path(temp_dir) / f"large_file_{i}.txt"
            with open(file_path, "w") as f:
                for line_num in range(1000):
                    if line_num % 100 == 0:
                        f.write(f"SEARCH_TARGET line {line_num} in large file {i}\n")
                    else:
                        f.write(f"Regular line {line_num} in large file {i}\n")
            files_created.append(str(file_path))

        yield temp_dir, files_created


@pytest.mark.asyncio
async def test_search_text_performance_many_files(large_test_setup):
    """Test that async search performs well with many files."""
    temp_dir, files_created = large_test_setup

    operation = SearchTextOperation(root_dir=temp_dir)

    # Test searching for a pattern that will be found in many files
    start_time = time.time()
    result = await operation(pattern="import")
    end_time = time.time()

    duration = end_time - start_time

    # Verify the search worked correctly
    assert result["status"] == "success"
    assert result["matches_found"] > 50  # Should find imports in the Python files
    assert result["files_searched"] >= len(files_created)  # Might find additional files like .git files

    # Performance should be reasonable (this is a basic check)
    # With async processing, it should complete within a reasonable time
    assert duration < 5.0  # Should complete within 5 seconds

    print(f"Search of {len(files_created)} files completed in {duration:.3f} seconds")
    print(f"Found {result['matches_found']} matches in {result['files_searched']} files")


@pytest.mark.asyncio
async def test_search_text_performance_specific_files(large_test_setup):
    """Test async search performance with specific files."""
    temp_dir, files_created = large_test_setup

    operation = SearchTextOperation(root_dir=temp_dir)

    # Get relative paths for just the large files
    large_files = [f"large_file_{i}.txt" for i in range(5)]

    start_time = time.time()
    result = await operation(pattern="SEARCH_TARGET", files=large_files)
    end_time = time.time()

    duration = end_time - start_time

    # Verify the search worked correctly
    assert result["status"] == "success"
    assert result["matches_found"] == 50  # 10 matches per file * 5 files
    assert result["files_searched"] == 5

    # Performance check
    assert duration < 2.0  # Should complete quickly for just 5 files

    print(f"Search of 5 large files completed in {duration:.3f} seconds")
    print(f"Found {result['matches_found']} matches")


@pytest.mark.asyncio
async def test_search_text_concurrency_behavior(large_test_setup):
    """Test that the async implementation handles concurrent operations properly."""
    temp_dir, files_created = large_test_setup

    operation = SearchTextOperation(root_dir=temp_dir)

    # Run multiple concurrent searches
    async def search_task(pattern):
        return await operation(pattern=pattern)

    start_time = time.time()
    results = await asyncio.gather(
        search_task("import"), search_task("def"), search_task("return"), return_exceptions=True
    )
    end_time = time.time()

    duration = end_time - start_time

    # Verify all searches completed successfully
    for result in results:
        assert not isinstance(result, Exception)
        assert result["status"] == "success"
        assert result["matches_found"] > 0

    # Concurrent execution should be efficient
    assert duration < 10.0  # Should complete within reasonable time

    print(f"3 concurrent searches completed in {duration:.3f} seconds")


@pytest.mark.asyncio
async def test_search_text_error_handling_async(large_test_setup):
    """Test that async error handling works correctly."""
    temp_dir, files_created = large_test_setup

    operation = SearchTextOperation(root_dir=temp_dir)

    # Test with invalid regex - should handle error gracefully
    result = await operation(pattern="[invalid")
    assert result["status"] == "error"
    assert "Invalid regex pattern" in result["message"]

    # Test with non-existent file
    result = await operation(pattern="test", files=["nonexistent.txt"])
    assert result["status"] == "error"
    assert "does not exist" in result["message"]
