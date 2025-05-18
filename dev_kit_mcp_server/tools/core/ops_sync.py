"""Base class for file operations."""

import abc
from dataclasses import dataclass
from typing import Any, Callable, Dict

from .file_base import _Operation


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
