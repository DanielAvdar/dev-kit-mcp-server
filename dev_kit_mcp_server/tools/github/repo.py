"""Module for interacting with GitHub repositories."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

# Import GitHub types for type checking only
if TYPE_CHECKING:
    pass

from .base import GitHubOperation


@dataclass
class GitHubRepoOperation(GitHubOperation):
    """Class to interact with GitHub repositories."""

    name = "github_repo"

    async def __call__(
        self,
        repo_name: str,
        owner: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get information about a GitHub repository.

        Args:
            repo_name: Name of the repository
            owner: Owner of the repository (default: None, which means the authenticated user)

        Returns:
            A dictionary containing information about the repository

        Raises:
            ValueError: If repo_name is not provided
            ImportError: If the PyGithub package is not installed

        """
        # Validate input
        if not repo_name:
            raise ValueError("Repository name must be provided")

        try:
            # Import Github here to handle import errors
            try:
                from github import Github
            except ImportError as err:
                raise ImportError(
                    "The PyGithub package is not installed. Please install it with 'pip install PyGithub'."
                ) from err

            # Initialize GitHub instance if not already initialized
            if self.github_instance is None:
                if self.token:
                    self.github_instance = Github(self.token)
                else:
                    self.github_instance = Github()

            # Get the repository
            if owner:
                full_name = f"{owner}/{repo_name}"
                repo = self.github_instance.get_repo(full_name)
            else:
                # Try to get the repository from the authenticated user
                user = self.github_instance.get_user()
                repo = user.get_repo(repo_name)

            # Return repository information
            return {
                "status": "success",
                "message": f"Successfully retrieved repository information for '{repo.full_name}'",
                "repo": {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "open_issues": repo.open_issues_count,
                    "default_branch": repo.default_branch,
                    "private": repo.private,
                },
            }
        except ImportError:
            # Re-raise ImportError to be caught by the caller
            raise
        except Exception as e:
            return {
                "error": f"Error retrieving repository information: {str(e)}",
                "repo_name": repo_name,
                "owner": owner,
            }
