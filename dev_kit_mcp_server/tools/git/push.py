"""Module for pushing changes to a remote git repository."""

from dataclasses import dataclass
from typing import Any, Dict

from ...core import AsyncOperation


@dataclass
class GitPushOperation(AsyncOperation):
    """Class to push changes to a remote git repository."""

    _name = "git_push"

    async def __call__(
        self,
    ) -> Dict[str, Any]:
        """Push changes to a remote git repository.

        Returns:
            A dictionary containing the status of the push operation

        """
        # Handle both model and direct parameter input for backward compatibility
