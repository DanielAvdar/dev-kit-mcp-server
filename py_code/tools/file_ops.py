"""Module for file operation base classes used by the tools."""

import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict


@dataclass
class _Operation:
    root_dir: str
    _root_path: Path = field(init=False, repr=False)

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
        """Perform the operation and return the result."""

    @classmethod
    def get_absolute_path(cls, root_path: Path, path: str) -> Path:
        """Get the absolute path of the given path.

        Args:
            root_path: The root path to use as a base
            path: The path to resolve

        Returns:
            The absolute path

        """
        if Path(path).is_absolute():
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
        if root_path.as_posix() not in abs_path.as_posix():
            raise ValueError(f"Path is not within the root directory: {root_path.as_posix()}")
        return abs_path.as_posix()


@dataclass(unsafe_hash=True, slots=True)
class FileOperation(_Operation):
    """Base class for file operations.

    This class provides a foundation for operations that work with files and directories.
    It inherits from _Operation and adds specific functionality for file operations.
    """

    @abc.abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Perform the file operation and return the result."""

    # @abc.abstractmethod
    #
    # def self_warpper(self, ) -> Callable:
    #     """Wrap the operation in a self-contained function."""
    #     # def w_func(*args: Optional[Tuple], **kwargs: Optional[dict]) -> Dict[str, Any]:
    #     #     return self.__call__(*args, **kwargs)
    #     # w_func.__name__ = self.name
    #     # return w_func
    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """

        def self_wrapper(
            path: str,
        ) -> Dict[str, Any]:
            """Run file operations.

            Args:
                path: Path to the file or folder to operate on

            Returns:
                A dictionary containing the operation result

            """
            return self.__call__(path)

        self_wrapper.__name__ = self.name

        return self_wrapper


@dataclass(unsafe_hash=True, slots=True)
class AsyncOperation(_Operation):
    """Base class for asynchronous operations.

    This class provides a foundation for operations that need to be executed asynchronously.
    It inherits from _Operation and adds specific functionality for async operations.
    """

    @abc.abstractmethod
    async def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform the file operation and return the result."""

    @abc.abstractmethod
    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """
