"""Base class for file operations."""

import abc
from dataclasses import dataclass
from typing import Any, Dict

from .file_base import _Operation

# Type variable for the model


@dataclass(unsafe_hash=True, slots=True)
class AsyncOperation(
    _Operation,
):
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
        """Perform the file operation and return the result.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            A dictionary containing the result of the operation

        """
