"""Base class for file operations."""

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar

from git import Repo

from .models import BaseToolParams, ToolModelMixin

# Type variable for the model
T = TypeVar("T", bound=BaseToolParams)


@dataclass
class _Operation(ToolModelMixin[T]):
    root_dir: str
    _root_path: Path = field(init=False, repr=False)
    _repo: Repo = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the root path.

        Raises:
            Exception: If the path does not exist or is not a directory

        """
        self._root_path = Path(self.root_dir)
        if not self._root_path.exists():
            raise Exception(f"Path does not exist: {self.root_dir}")
        if not self._root_path.is_dir():
            raise Exception(f"Path is neither a file nor a directory: {self.root_dir}")
        self._repo_init()

    def _repo_init(self) -> None:
        self._repo = Repo(self._root_path)

    @property
    def docstring(self) -> str:
        """Return the docstring of the class."""
        return self.__call__.__doc__ or "No docstring provided"

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the operation."""

    @abc.abstractmethod
    def self_warpper(self) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

    @abc.abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Perform the operation and return the result.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            A dictionary containing the result of the operation, or a coroutine that will return such a dictionary

        """

    @classmethod
    def get_absolute_path(cls, root_path: Path, path: str) -> Path:
        """Get the absolute path of the given path.

        Args:
            root_path: The root path to use as a base
            path: The path to resolve

        Returns:
            The absolute path

        """
        if Path(path).is_relative_to(root_path):
            return Path(path).resolve()
        return Path(root_path.as_posix() + "/" + path).resolve()

    @classmethod
    def _validate_path_in_root(cls, root_dir: Path, path: str) -> str:
        """Check if the given path is within the root directory.

        Args:
            root_dir: The root directory to check against
            path: The path to validate

        Returns:
            The absolute path as a string if it's within the root directory

        Raises:
            ValueError: If the path is not within the root directory

        """
        root_path = root_dir
        abs_path = cls.get_absolute_path(root_path, path)
        if not abs_path.is_relative_to(root_path):
            raise ValueError(f"Path {path} is not within the root directory: {root_path.as_posix()}")
        return abs_path.as_posix()
