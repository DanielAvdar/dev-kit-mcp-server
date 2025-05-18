"""Base class for file operations."""

import abc
from dataclasses import dataclass
from typing import Any, Callable, Dict, TypeVar

from .file_base import _Operation
from .models import BaseToolParams

# Type variable for the model
T = TypeVar("T", bound=BaseToolParams)


@dataclass(unsafe_hash=True, slots=True)
class AsyncOperation(
    _Operation[T],
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

        # Create a unified wrapper function that can handle all cases
        async def self_wrapper(
            param: Any = None,
            param2: Any = None,
            param3: Any = None,
        ) -> Dict[str, Any]:
            """Execute the operation with the given parameters.

            Args:
                param: The primary parameter for the operation
                param2: Secondary parameter (used in some operations)
                param3: Tertiary parameter (used in some operations)

            Returns:
                A dictionary containing the result of the operation

            Raises:
                ValueError: If the parameters are invalid for the operation

            """
            # Handle different cases based on the signature of __call__
            if len(params) == 1 and params[0].name == "model_or_commands":
                # Special case for ExecMakeTarget
                if param is None:
                    raise ValueError("Commands parameter cannot be None")

                # Handle both list and dictionary input
                if isinstance(param, dict) and "commands" in param:
                    commands = param["commands"]
                elif isinstance(param, list):
                    commands = param
                else:
                    raise ValueError("Expected a list of commands or a dictionary with a 'commands' key")

                # Create a model with the commands
                model_data = {"commands": commands}
                model = self.model_class(**model_data)
                return await self.__call__(model)

            elif len(params) == 1 and params[0].name == "model_or_path":
                # Special case for CreateDirOperation
                if param is None:
                    raise ValueError("Path parameter cannot be None")

                # Create a model with the path
                model_data = {"path": param}
                model = self.model_class(**model_data)
                return await self.__call__(model)

            elif len(params) == 3 and params[0].name == "model_or_message":
                # Special case for GitCommitOperation
                if param is None:
                    raise ValueError("Message parameter cannot be None")

                # Create a model with the message, files, and all_files
                model_data = {
                    "message": param,
                    "files": param2 or None,
                    "all_files": param3 or False,
                }
                model = self.model_class(**model_data)
                return await self.__call__(model)

            else:
                # Default case - create a model with the parameter as the first field
                model_fields = getattr(self.model_class, "__annotations__", {})
                if model_fields and param is not None:
                    first_field = next(iter(model_fields))
                    model_data = {first_field: param}
                    model = self.model_class(**model_data)
                else:
                    # Fallback to an empty model
                    model = self.model_class()

                return await self.__call__(model)

        self_wrapper.__name__ = self.name
        self_wrapper.__doc__ = self.__call__.__doc__

        return self_wrapper
