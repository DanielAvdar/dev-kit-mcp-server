"""Tests for file operations."""

import os
from pathlib import Path
from typing import Tuple

import pytest

from dev_kit_mcp_server.tools import (
    CreateDirOperation,
    EditFileOperation,
    MoveDirOperation,
    RemoveFileOperation,
    RenameOperation,
)
from dev_kit_mcp_server.tools.core import FileOperation


@pytest.fixture(scope="function")
def temp_root_dir(temp_dir) -> str:
    """Create a temporary directory for testing."""
    return temp_dir


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
def rename_operation(temp_root_dir: str) -> RenameOperation:
    """Create a RenameOperation instance with a temporary root directory."""
    return RenameOperation(root_dir=temp_root_dir)


@pytest.fixture
def edit_operation(temp_root_dir: str) -> EditFileOperation:
    """Create an EditFileOperation instance with a temporary root directory."""
    return EditFileOperation(root_dir=temp_root_dir)


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

        with pytest.raises(FileExistsError):
            create_operation(test_dir)

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

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Source path does not exist"):
            move_operation(non_existent, new_location)

        # Verify destination was not created
        assert not os.path.exists(new_location)

    def test_move_destination_exists(
        self, move_operation: MoveDirOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test moving to a destination that already exists."""
        # Arrange
        test_dir, test_file, _ = setup_test_files

        # Act & Assert
        with pytest.raises(FileExistsError, match="Destination path already exists"):
            move_operation(test_dir, test_file)

        # Verify both paths still exist
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

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            remove_operation(non_existent)

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
        with pytest.raises(ValueError):
            remove_operation(invalid)
        with pytest.raises(ValueError):
            create_operation(invalid)
        with pytest.raises(ValueError):
            move_operation(invalid, "some_folder")


class TestEditFileOperation:
    """Tests for EditFileOperation."""

    def test_edit_file_success(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str], temp_root_dir: str
    ) -> None:
        """Test editing a file successfully."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        # Act
        result = edit_operation(test_file, 2, 4, "New Line 2\nNew Line 3")

        # Assert
        assert result["status"] == "success"
        assert f"Successfully edited file: {test_file}" in result["message"]
        assert result["path"] == test_file
        assert result["start_line"] == 2
        assert result["end_line"] == 4
        assert result["text_length"] == len("New Line 2\nNew Line 3")

        # Check the file content
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Line 1\nNew Line 2\nNew Line 3\nLine 5\n"

    def test_edit_file_append(self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]) -> None:
        """Test appending to a file by setting start_line beyond the end of the file."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Act
        result = edit_operation(test_file, 4, 4, "Line 4\nLine 5")

        # Assert
        assert result["status"] == "success"

        # Check the file content
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n"

    def test_edit_file_invalid_start_line(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test editing a file with an invalid start line."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Act & Assert
        with pytest.raises(ValueError, match="Start line must be at least 1"):
            edit_operation(test_file, 0, 2, "New content")

    def test_edit_file_invalid_end_line(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test editing a file with an invalid end line."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Act & Assert
        with pytest.raises(ValueError, match="End line must be greater than or equal to start line"):
            edit_operation(test_file, 3, 1, "New content")

    def test_edit_file_start_line_beyond_file(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test editing a file with a start line beyond the end of the file."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Act & Assert
        with pytest.raises(ValueError, match="Start line .* is beyond the end of the file"):
            edit_operation(test_file, 10, 12, "New content")

    def test_edit_file_end_line_beyond_file(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test editing a file with an end line beyond the end of the file."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create a test file with multiple lines
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # Act
        result = edit_operation(test_file, 2, 10, "New Line 2")

        # Assert
        assert result["status"] == "success"

        # Check the file content
        with open(test_file, "r") as f:
            content = f.read()
        assert content == "Line 1\nNew Line 2\n"

    def test_edit_nonexistent_file(
        self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test editing a non-existent file."""
        # Arrange
        _, _, non_existent = setup_test_files

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            edit_operation(non_existent, 1, 2, "New content")

    def test_edit_directory(self, edit_operation: EditFileOperation, setup_test_files: Tuple[str, str, str]) -> None:
        """Test editing a directory."""
        # Arrange
        test_dir, _, _ = setup_test_files

        # Act & Assert
        with pytest.raises(IsADirectoryError, match="Path is a directory, not a file"):
            edit_operation(test_dir, 1, 2, "New content")

    @pytest.mark.skip(reason="Test is OS dependent")
    def test_edit_outside_root(self, edit_operation: EditFileOperation) -> None:
        """Test editing a file outside the root directory."""
        # Arrange
        outside_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "outside_file.txt"))

        # Create the file temporarily to ensure it exists
        try:
            with open(outside_path, "w") as f:
                f.write("Should not be edited")

            # Act & Assert
            with pytest.raises(ValueError, match="not within the root directory"):
                edit_operation(outside_path, 1, 1, "New content")

            # Verify the file was not edited
            with open(outside_path, "r") as f:
                content = f.read()
            assert content == "Should not be edited"
        finally:
            # Clean up
            if os.path.exists(outside_path):
                os.remove(outside_path)


class TestRenameOperation:
    """Tests for RenameOperation."""

    def test_rename_file_success(
        self, rename_operation: RenameOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test renaming a file successfully."""
        # Arrange
        _, test_file, _ = setup_test_files
        new_name = "renamed_file.txt"

        # Get the parent directory
        parent_dir = os.path.dirname(test_file)
        expected_new_path = os.path.join(parent_dir, new_name)

        # Act
        result = rename_operation(test_file, new_name)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_file)
        assert os.path.exists(expected_new_path)
        assert os.path.isfile(expected_new_path)

        # Check content
        with open(expected_new_path, "r") as f:
            content = f.read()
        assert content == "Test content"

    def test_rename_folder_success(
        self, rename_operation: RenameOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test renaming a folder successfully."""
        # Arrange
        test_dir, _, _ = setup_test_files
        new_name = "renamed_dir"

        # Get the parent directory
        parent_dir = os.path.dirname(test_dir)
        expected_new_path = os.path.join(parent_dir, new_name)

        # Act
        result = rename_operation(test_dir, new_name)

        # Assert
        assert result.get("status") == "success"
        assert not os.path.exists(test_dir)
        assert os.path.exists(expected_new_path)
        assert os.path.isdir(expected_new_path)

    def test_rename_non_existent(
        self, rename_operation: RenameOperation, setup_test_files: Tuple[str, str, str]
    ) -> None:
        """Test renaming a non-existent path."""
        # Arrange
        _, _, non_existent = setup_test_files
        new_name = "should_not_exist"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            rename_operation(non_existent, new_name)

    def test_rename_to_existing_name(
        self, rename_operation: RenameOperation, setup_test_files: Tuple[str, str, str], temp_root_dir: str
    ) -> None:
        """Test renaming to a name that already exists."""
        # Arrange
        _, test_file, _ = setup_test_files

        # Create another file with the target name
        existing_name = "existing_file.txt"
        existing_path = os.path.join(os.path.dirname(test_file), existing_name)
        with open(existing_path, "w") as f:
            f.write("Existing content")

        # Act & Assert
        with pytest.raises(FileExistsError, match="A file or folder with the name .* already exists"):
            rename_operation(test_file, existing_name)

        # Verify files still exist
        assert os.path.exists(test_file)
        assert os.path.exists(existing_path)

    @pytest.mark.skip(reason="Test is OS dependent")
    def test_rename_outside_root(self, rename_operation: RenameOperation) -> None:
        """Test renaming a path outside the root directory."""
        # Arrange
        outside_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "outside_file.txt"))
        new_name = "renamed_outside_file.txt"

        # Create the file temporarily to ensure it exists
        try:
            with open(outside_path, "w") as f:
                f.write("Should not be renamed")

            # Act
            result = rename_operation(outside_path, new_name)

            # Assert
            assert "error" in result
            assert "not within the root directory" in result.get("error", "")
            assert os.path.exists(outside_path)
        finally:
            # Clean up
            if os.path.exists(outside_path):
                os.remove(outside_path)
