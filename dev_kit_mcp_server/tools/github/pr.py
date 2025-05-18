"""Module for interacting with GitHub pull requests."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

# Import GitHub types for type checking only
if TYPE_CHECKING:
    pass

from .base import GitHubOperation


@dataclass
class GitHubPROperation(GitHubOperation):
    """Class to interact with GitHub pull requests."""

    name = "github_pr"

    async def __call__(
        self,
        repo_name: str,
        owner: str,
        pr_number: Optional[int] = None,
        state: str = "open",
    ) -> Dict[str, Any]:
        """Get information about GitHub pull requests.

        Args:
            repo_name: Name of the repository
            owner: Owner of the repository
            pr_number: Number of the pull request to get (default: None, which means get all PRs)
            state: State of the pull requests to get (default: "open")

        Returns:
            A dictionary containing information about the pull requests

        Raises:
            ValueError: If repo_name or owner is not provided
            ImportError: If the PyGithub package is not installed

        """
        # Validate input
        if not repo_name:
            raise ValueError("Repository name must be provided")
        if not owner:
            raise ValueError("Repository owner must be provided")

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
            full_name = f"{owner}/{repo_name}"
            repo = self.github_instance.get_repo(full_name)

            # Get the pull requests
            if pr_number is not None:
                # Get a specific pull request
                pr = repo.get_pull(pr_number)
                return {
                    "status": "success",
                    "message": f"Successfully retrieved PR #{pr.number} from '{repo.full_name}'",
                    "pr": self._format_pr(pr),
                }
            else:
                # Get all pull requests
                prs = []
                for pr in repo.get_pulls(state=state):
                    prs.append(self._format_pr(pr))

                return {
                    "status": "success",
                    "message": f"Successfully retrieved {len(prs)} pull requests from '{repo.full_name}'",
                    "prs": prs,
                }
        except ImportError:
            # Re-raise ImportError to be caught by the caller
            raise
        except Exception as e:
            return {
                "error": f"Error retrieving pull requests: {str(e)}",
                "repo_name": repo_name,
                "owner": owner,
                "pr_number": pr_number,
            }

    def _format_pr(self, pr: Any) -> Dict[str, Any]:
        """Format a pull request for the response.

        Args:
            pr: The pull request to format (github.PullRequest.PullRequest)

        Returns:
            A dictionary containing formatted pull request information

        """
        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            "user": pr.user.login if pr.user else None,
            "head": {
                "ref": pr.head.ref,
                "sha": pr.head.sha,
                "repo": pr.head.repo.full_name if pr.head.repo else None,
            },
            "base": {
                "ref": pr.base.ref,
                "sha": pr.base.sha,
                "repo": pr.base.repo.full_name if pr.base.repo else None,
            },
            "mergeable": pr.mergeable,
            "merged": pr.merged,
            "url": pr.html_url,
        }
