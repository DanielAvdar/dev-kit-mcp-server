"""Tests for file operations."""

import os
from pathlib import Path
from typing import Tuple

import pytest

from py_code.tools import CreateDirOperation, FileOperation, MoveDirOperation, RemoveFileOperation


@pytest.fixture
def temp_root_dir(tmp_path) -> str:
    """Create a temporary directory for testing."""
    return Path(tmp_path).as_posix()


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


@pytest.fixture(
    params=[
        "test_file.txt",
        "/test_file.txt",
        "./test_file.txt",
        "new_folder",
        "/new_folder",
        "./new_folder",
        "examples/test_relative_path/examples/test_relative_path/examples/../test_relative_path",
    ]
)
def valid_rel_path(request) -> str:
    """Fixture to provide a relative path for testing."""
    return request.param


@pytest.fixture(
    params=[
        False,
        True,
    ]
)
def as_abs(request) -> bool:
    """Fixture to provide a boolean for absolute path testing."""
    return request.param


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

    @pytest.mark.skip(reason="Test for is OS dependent")

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

    @pytest.mark.skip(reason="Test for is OS dependent")

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

    @pytest.mark.skip(reason="Test for is OS dependent")

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

    def test_valid_rel_path_conversion(
        self,
        valid_rel_path: str,
        as_abs: bool,
        temp_root_dir: str,
    ) -> None:
        """Test removing a file using a relative path."""
        # Arrange
        root_path = Path(temp_root_dir)
        abs_path = Path(temp_root_dir + "/" + valid_rel_path).resolve()
        assert abs_path.is_relative_to(root_path)
        assert temp_root_dir in abs_path.as_posix()
        assert root_path.as_posix() in abs_path.as_posix()
        if as_abs:
            valid_rel_path = abs_path.as_posix()
        fun_abs_path = FileOperation.get_absolute_path(root_path, abs_path.as_posix())
        fun_path = FileOperation.get_absolute_path(root_path, valid_rel_path)

        assert fun_abs_path == fun_path

    def test_invalid_path(
        self,
        valid_rel_path: str,
        temp_root_dir: str,
    ) -> None:
        """Test removing a file using an invalid path."""
        root_path = Path(temp_root_dir)
        invalid = f"./../{valid_rel_path}"
        valid_rel_path = FileOperation._validate_path_in_root(root_path, valid_rel_path)
        with pytest.raises(ValueError):
            FileOperation._validate_path_in_root(root_path, invalid)

    def test_tools_path(
        self,
        valid_rel_path: str,
        as_abs: bool,
        remove_operation: RemoveFileOperation,
        create_operation: CreateDirOperation,
        move_operation: MoveDirOperation,
    ) -> None:
        """Test removing a file using an invalid path."""
        root_path = remove_operation._root_path
        assert remove_operation._root_path == create_operation._root_path
        assert remove_operation._root_path == move_operation._root_path
        fun_path = FileOperation.get_absolute_path(root_path, valid_rel_path)
        path = valid_rel_path
        if as_abs:
            path = fun_path.as_posix()
        res_creat = create_operation(path)
        assert res_creat.get("status") == "success"
        assert fun_path.exists()
        res_create_folder = create_operation("some_folder")
        assert res_create_folder.get("status") == "success"
        res_move = move_operation(path, f"some_folder/{valid_rel_path}")
        assert not fun_path.exists()
        assert res_move.get("status") == "success"

        res_remove = remove_operation("some_folder")
        assert res_remove.get("status") == "success"
        assert not fun_path.exists()
        invalid = f"./../{valid_rel_path}"
        invalid_res = remove_operation(invalid)
        assert "error" in invalid_res
        assert "not within the root directory" in invalid_res.get("error", "")
        invalid_res = create_operation(invalid)
        assert "error" in invalid_res
        invalid_res = move_operation(invalid, "some_folder")
        assert "error" in invalid_res
