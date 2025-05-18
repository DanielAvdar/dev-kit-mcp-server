"""Base class for GitHub operations."""

import abc
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

# Import Github only for type checking
if TYPE_CHECKING:
    pass

from ..core import AsyncOperation


@dataclass
class GitHubOperation(AsyncOperation):
    """Base class for GitHub operations.

    This class provides a foundation for operations that interact with GitHub repositories.
    It inherits from AsyncOperation and adds specific functionality for GitHub operations.
    """

    token: Optional[str] = None
    github_instance: Optional[Any] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize the GitHub instance.

        If a token is provided, it will be used to authenticate with GitHub.
        Otherwise, an unauthenticated GitHub instance will be created.

        Note:
            The GitHub instance is not created during initialization to avoid
            import errors if PyGithub is not installed. It will be created
            when the operation is called.

        """
        super().__post_init__()
        # We'll initialize github_instance when the operation is called
        self.github_instance = None

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the operation."""

    @abc.abstractmethod
    async def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Perform the GitHub operation and return the result.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            A dictionary containing the result of the operation

        """
