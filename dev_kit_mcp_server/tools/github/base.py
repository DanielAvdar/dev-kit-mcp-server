"""Base class for GitHub operations."""

import abc
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

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

    def get_repo_info(self) -> Optional[Tuple[str, str]]:
        """Extract owner and repo name from git remote.

        Returns:
            A tuple containing (owner, repo_name) if a GitHub remote is found, None otherwise.

        """
        try:
            # Get the repository
            repo = self._repo

            # Get the origin remote
            try:
                origin = repo.remote("origin")

                # Get the URL of the remote
                url = origin.url

                # Extract owner and repo name from the URL
                # Handle different URL formats:
                # - https://github.com/owner/repo.git
                # - git@github.com:owner/repo.git
                if "github.com" in url:
                    if url.startswith("https://"):
                        match = re.search(r"github\.com/([^/]+)/([^/.]+)", url)
                    else:  # SSH format
                        match = re.search(r"github\.com:([^/]+)/([^/.]+)", url)

                    if match:
                        owner = match.group(1)
                        repo_name = match.group(2)

                        # Initialize GitHub instance if not already initialized
                        if self.github_instance is None:
                            try:
                                from github import Github

                                if self.token:
                                    self.github_instance = Github(self.token)
                                else:
                                    self.github_instance = Github()
                            except ImportError:
                                # If PyGithub is not installed, fall back to regex extraction
                                return owner, repo_name

                        try:
                            # Get the repository using PyGithub
                            full_name = f"{owner}/{repo_name}"
                            github_repo = self.github_instance.get_repo(full_name)

                            # Use Repository class to extract owner and repo_name
                            return github_repo.owner.login, github_repo.name
                        except Exception:
                            # If there's an error getting the repository, fall back to regex extraction
                            return owner, repo_name
            except ValueError:
                # Remote doesn't exist
                pass

            return None
        except Exception:
            return None

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
