"""Module for interacting with GitHub issues."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

# Import GitHub types for type checking only
if TYPE_CHECKING:
    pass

from .base import GitHubOperation


@dataclass
class GitHubIssueOperation(GitHubOperation):
    """Class to interact with GitHub issues."""

    name = "github_issue"

    async def __call__(
        self,
        repo_name: str,
        owner: str,
        issue_number: Optional[int] = None,
        state: str = "open",
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get information about GitHub issues.

        Args:
            repo_name: Name of the repository
            owner: Owner of the repository
            issue_number: Number of the issue to get (default: None, which means get all issues)
            state: State of the issues to get (default: "open")
            labels: Labels to filter issues by (default: None)

        Returns:
            A dictionary containing information about the issues

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

            # Get the issues
            if issue_number is not None:
                # Get a specific issue
                issue = repo.get_issue(issue_number)
                return {
                    "status": "success",
                    "message": f"Successfully retrieved issue #{issue.number} from '{repo.full_name}'",
                    "issue": self._format_issue(issue),
                }
            else:
                # Get all issues
                issues = []
                for issue in repo.get_issues(state=state, labels=labels):
                    issues.append(self._format_issue(issue))

                return {
                    "status": "success",
                    "message": f"Successfully retrieved {len(issues)} issues from '{repo.full_name}'",
                    "issues": issues,
                }
        except ImportError:
            # Re-raise ImportError to be caught by the caller
            raise
        except Exception as e:
            return {
                "error": f"Error retrieving issues: {str(e)}",
                "repo_name": repo_name,
                "owner": owner,
                "issue_number": issue_number,
            }

    def _format_issue(self, issue: Any) -> Dict[str, Any]:
        """Format an issue for the response.

        Args:
            issue: The issue to format (github.Issue.Issue)

        Returns:
            A dictionary containing formatted issue information

        """
        return {
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "labels": [label.name for label in issue.labels],
            "assignees": [assignee.login for assignee in issue.assignees],
            "url": issue.html_url,
        }
