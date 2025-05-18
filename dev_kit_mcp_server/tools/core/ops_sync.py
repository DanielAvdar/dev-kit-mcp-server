"""Base class for file operations."""

import abc
from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar

from .file_base import _Operation
from .models import BaseToolParams

# Type variable for the model
T = TypeVar("T", bound=BaseToolParams)


@dataclass(unsafe_hash=True, slots=True)
class FileOperation(
    _Operation[T],
):
    """Base class for file operations.

    This class provides a foundation for operations that work with files and directories.
    It inherits from _Operation and adds specific functionality for file operations.
    """

    @abc.abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Perform the file operation and return the result.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            A dictionary containing the result of the operation

        """

    def self_warpper(
        self,
    ) -> Callable:
        """Return the self wrapper function.

        Returns:
            A callable function that wraps the __call__ method

        """
        # For backward compatibility with existing code and tests
        # We need to create a wrapper that matches the original signature
        # of the __call__ method for each specific tool

        # Get the original __call__ method's signature
        import inspect

        sig = inspect.signature(self.__call__)
        params = list(sig.parameters.values())[1:]  # Skip 'self'

        # Create a wrapper function with the same signature
        if len(params) == 1 and params[0].name == "model_or_path":
            # Special case for file operations that take a path
            def self_wrapper(param: Any = None) -> Dict[str, Any]:
                """Execute the operation with the given parameters.

                Args:
                    param: The path to operate on

                Returns:
                    A dictionary containing the result of the operation

                Raises:
                    ValueError: If param is None

                """
                if param is None:
                    raise ValueError("Path parameter cannot be None")
                return self.__call__(param)

        else:
            # Default case - create a wrapper with a single parameter
            # that matches the first field of the model
            model_fields = getattr(self.model_class, "__annotations__", {})
            if model_fields:
                first_field = next(iter(model_fields))

                def self_wrapper(param: Any = None) -> Dict[str, Any]:
                    """Execute the operation with the given parameter.

                    Args:
                        param: The parameter for the operation

                    Returns:
                        A dictionary containing the result of the operation

                    """
                    if param is None:
                        model = self.model_class()
                    else:
                        # Create a model with the parameter as the first field
                        model_data = {first_field: param}
                        model = self.model_class(**model_data)
                    return self.__call__(model)

            else:
                # Fallback to a no-parameter wrapper
                def self_wrapper(param: Any = None) -> Dict[str, Any]:
                    """Execute the operation.

                    Args:
                        param: Optional parameter (not used)

                    Returns:
                        A dictionary containing the result of the operation

                    """
                    model = self.model_class()
                    return self.__call__(model)

        self_wrapper.__name__ = self.name
        self_wrapper.__doc__ = self.__call__.__doc__

        return self_wrapper
