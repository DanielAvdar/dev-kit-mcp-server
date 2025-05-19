"""Base class for GitHub operations."""

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from dev_kit_mcp_server.tools.core import AsyncOperation


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
            # Get the remotes from the git repository
            remotes = self._repo.remotes
            if not remotes:
                return None

            # Try to find a GitHub remote (origin or any other)
            github_remote = None
            for remote in remotes:
                if "github.com" in remote.url:
                    github_remote = remote
                    break

            if not github_remote:
                return None

            # Extract owner and repo name from the remote URL
            url = github_remote.url
            if url.startswith("git@github.com:"):
                # SSH URL format: git@github.com:owner/repo.git
                path = url.split("git@github.com:")[1]
            elif url.startswith("https://github.com/"):
                # HTTPS URL format: https://github.com/owner/repo.git
                path = url.split("https://github.com/")[1]
            else:
                return None

            # Remove .git suffix if present
            if path.endswith(".git"):
                path = path[:-4]

            # Split into owner and repo name
            parts = path.split("/")
            if len(parts) >= 2:
                owner = parts[0]
                repo_name = parts[1]

                # Initialize GitHub instance if not already initialized
                if self.github_instance is None:
                    try:
                        from github import Github

                        if self.token:
                            self.github_instance = Github(self.token)
                        else:
                            self.github_instance = Github()
                    except ImportError:
                        # If PyGithub is not installed, fall back to the extracted info
                        return (owner, repo_name)

                try:
                    # Get the repository using PyGithub
                    full_name = f"{owner}/{repo_name}"
                    repo = self.github_instance.get_repo(full_name)

                    # Use the Repository object to get owner and repo name
                    return (repo.owner.login, repo.name)
                except Exception:
                    # If there's an error getting the repository, fall back to the extracted info
                    return (owner, repo_name)

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
