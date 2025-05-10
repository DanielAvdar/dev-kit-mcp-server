"""Tests for file operations."""

import os
import tempfile
from typing import Generator, Tuple

import pytest

from py_code.tools.code_editing import CreateDirOperation, MoveDirOperation, RemoveFileOperation


@pytest.fixture
def temp_root_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def create_operation(temp_root_dir: str) -> CreateDirOperation:
    """Create a CreateDirOperation instance with a temporary root directory."""
    return CreateDirOperation(root_dir=temp_root_dir)


@pytest.fixture
def move_operation(temp_root_dir: str) -> MoveDirOperation:
    """Create a MoveDirOperation instance with a temporary root directory."""
    return MoveDirOperation(root_dir=temp_root_dir)


@pytest.fixture
def remove_operation(temp_root_dir: str) -> RemoveFileOperation:
    """Create a RemoveFileOperation instance with a temporary root directory."""
    return RemoveFileOperation(root_dir=temp_root_dir)


@pytest.fixture
def setup_test_files(temp_root_dir: str) -> Tuple[str, str, str]:
    """Set up test files and directories.

    Returns:
        Tuple containing paths to a test directory, a test file, and a non-existent path
    """
    # Create a test directory
    test_dir = os.path.join(temp_root_dir, "test_dir")
    os.makedirs(test_dir)

    # Create a test file
    test_file = os.path.join(temp_root_dir, "test_file.txt")
    with open(test_file, "w") as f:
        f.write("Test content")

    # Path to a non-existent file
    non_existent = os.path.join(temp_root_dir, "non_existent")

    return test_dir, test_file, non_existent


class TestCreateDirOperation:
    """Tests for CreateDirOperation."""

    def test_create_folder_success(self, create_operation: CreateDirOperation, temp_root_dir: str) -> None:
        """Test creating a folder successfully."""
        # Arrange
        new_folder = os.path.join(temp_root_dir, "new_folder")

        # Act
        result = create_operation(new_folder)

        # Assert
        assert result.get("status") == "success"
        assert os.path.exists(new_folder)
        assert os.path.isdir(new_folder)

    def test_create_folder_nested(self, create_operation: CreateDirOperation, temp_root_dir: str) -> None:
        """Test creating a nested folder successfully."""
        # Arrange
        nested_folder = os.path.join(temp_root_dir, "parent", "child", "grandchild")

        # Act
        result = create_operation(nested_folder)

        # Assert
        assert result.get("status") == "success"
        assert os.path.exists(nested_folder)
        assert os.path.isdir(nested_folder)

    def test_create_folder_already_exists(
        self, create_operation: CreateDirOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test creating a folder that already exists."""
        # Arrange
        test_dir, _, _ = setup_test_files

        # Act
        result = create_operation(test_dir)

        # Assert
        assert "error" in result
        assert "already exists" in result.get("error", "")

    def test_create_folder_outside_root(self, create_operation: CreateDirOperation) -> None:
        """Test creating a folder outside the root directory."""
        # Arrange
        outside_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "outside_folder"))

        # Act
        result = create_operation(outside_folder)

        # Assert
        assert "error" in result
        assert "not within the root directory" in result.get("error", "")
        assert not os.path.exists(outside_folder)


class TestMoveDirOperation:
    """Tests for MoveDirOperation."""

    def test_move_folder_success(
        self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str], temp_root_dir: str
    ) -> None:
        """Test moving a folder successfully."""
        # Arrange
        test_dir, _, _ = setup_test_files
        new_location = os.path.join(temp_root_dir, "moved_dir")

        # Act
        result = move_operation(test_dir, new_location)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_dir)
        assert os.path.exists(new_location)
        assert os.path.isdir(new_location)

    def test_move_file_success(
        self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str], temp_root_dir: str
    ) -> None:
        """Test moving a file successfully."""
        # Arrange
        _, test_file, _ = setup_test_files
        new_location = os.path.join(temp_root_dir, "moved_file.txt")

        # Act
        result = move_operation(test_file, new_location)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_file)
        assert os.path.exists(new_location)
        assert os.path.isfile(new_location)

        # Check content
        with open(new_location, "r") as f:
            content = f.read()
        assert content == "Test content"

    def test_move_source_not_exists(
        self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str], temp_root_dir: str
    ) -> None:
        """Test moving a non-existent source."""
        # Arrange
        _, _, non_existent = setup_test_files
        new_location = os.path.join(temp_root_dir, "should_not_exist")

        # Act
        result = move_operation(non_existent, new_location)

        # Assert
        assert "error" in result
        assert "does not exist" in result.get("error", "")
        assert not os.path.exists(new_location)

    def test_move_destination_exists(
        self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test moving to a destination that already exists."""
        # Arrange
        test_dir, test_file, _ = setup_test_files

        # Act
        result = move_operation(test_dir, test_file)

        # Assert
        assert "error" in result
        assert "already exists" in result.get("error", "")
        assert os.path.exists(test_dir)
        assert os.path.exists(test_file)

    def test_move_outside_root(self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str]) -> None:
        """Test moving to a destination outside the root directory."""
        # Arrange
        test_dir, _, _ = setup_test_files
        outside_location = os.path.abspath(os.path.join(os.path.dirname(__file__), "outside_folder"))

        # Act
        result = move_operation(test_dir, outside_location)

        # Assert
        assert "error" in result
        assert "not within the root directory" in result.get("error", "")
        assert os.path.exists(test_dir)
        assert not os.path.exists(outside_location)


class TestRemoveFileOperation:
    """Tests for RemoveFileOperation."""

    def test_remove_folder_success(
        self, remove_operation: RemoveFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test removing a folder successfully."""
        # Arrange
        test_dir, _, _ = setup_test_files

        # Act
        result = remove_operation(test_dir)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_dir)

    def test_remove_file_success(
        self, remove_operation: RemoveFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test removing a file successfully."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Act
        result = remove_operation(test_file)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_file)

    def test_remove_non_existent(
        self, remove_operation: RemoveFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test removing a non-existent path."""
        # Arrange
        _, _, non_existent = setup_test_files

        # Act
        result = remove_operation(non_existent)

        # Assert
        assert "error" in result
        assert "does not exist" in result.get("error", "")

    def test_remove_outside_root(self, remove_operation: RemoveFileOperation) -> None:
        """Test removing a path outside the root directory."""
        # Arrange
        outside_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "outside_file.txt"))

        # Create the file temporarily to ensure it exists
        try:
            with open(outside_path, "w") as f:
                f.write("Should not be removed")

            # Act
            result = remove_operation(outside_path)

            # Assert
            assert "error" in result
            assert "not within the root directory" in result.get("error", "")
            assert os.path.exists(outside_path)
        finally:
            # Clean up
            if os.path.exists(outside_path):
                os.remove(outside_path)

    @pytest.mark.parametrize(
        "rel_path",
        ["/test_file.txt", "./test_file.txt", "new_folder"],
    )
    def test_rel_path(
        self,
        rel_path: str,
        remove_operation: RemoveFileOperation,
        create_operation: CreateDirOperation,
        move_operation: MoveDirOperation,
    ) -> None:
        """Test removing a file using a relative path."""
        # Arrange
        abs_path = remove_operation._root_path / rel_path
        fun_abs_path = remove_operation.get_absolute_path(abs_path.as_posix())
        fun_path = remove_operation.get_absolute_path(rel_path)
        assert fun_abs_path == fun_path
        create_operation(rel_path)
        assert abs_path.exists()
        res_remove = remove_operation(rel_path)
        assert res_remove.get("status") == "success"
        with pytest.raises(Exception):
            remove_operation(f"../{rel_path}")
