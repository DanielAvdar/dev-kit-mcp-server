"""Module for interacting with GitHub repositories."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

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
    ) -> Dict[str, Any]:
        """Get information about a GitHub repository.

        Returns:
            A dictionary containing information about the repository

        Raises:
            ValueError: If repository information cannot be determined from git remote
            ImportError: If the PyGithub package is not installed

        """
        # Get repo info from git remote
        repo_info = self.get_repo_info()
        if not repo_info:
            raise ValueError("Repository information could not be extracted from git remote")

        owner, repo_name = repo_info

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
