from datetime import datetime, timedelta
from typing import Optional

import structlog
from github import Github, Auth
from github.Repository import Repository

logger = structlog.get_logger()


class GitHubService:
    """Service for interacting with GitHub."""
    
    def __init__(self, token: str, org: str = "improvado") -> None:
        """Initialize GitHub service.
        
        Args:
            token: GitHub access token
            org: GitHub organization name
        """
        self._token = token
        self._org_name = org
        self._github: Optional[Github] = None
        self._org_instance = None
        logger.info("github_service.initialized", org=org)
    
    def _ensure_initialized(self) -> None:
        """Ensure GitHub client and organization instance are initialized."""
        if self._github is None:
            auth = Auth.Token(self._token)
            self._github = Github(auth=auth)
            self._org_instance = self._github.get_organization(self._org_name)
    
    def _get_repository(self, service_name: str) -> Optional[Repository]:
        """Get repository by service name.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Repository object if found, None otherwise
        """
        try:
            self._ensure_initialized()
            return self._org_instance.get_repo(service_name)
        except Exception as e:
            logger.warning(
                "github_service.repo_not_found",
                service=service_name,
                error=str(e)
            )
            return None
    
    async def check_recent_changes(
        self,
        service_name: str,
        hours: int = 24
    ) -> dict[str, Optional[str]]:
        """Check if there were any changes in the repository in the last N hours.
        
        Args:
            service_name: Name of the service/repository
            hours: Number of hours to look back
            
        Returns:
            Dictionary with change information
        """
        repo = self._get_repository(service_name)
        if not repo:
            return {
                "status": "error",
                "message": f"Repository {service_name} not found",
                "last_commit": None,
                "last_commit_url": None
            }
        
        try:
            # Get commits from the last N hours
            since = datetime.now() - timedelta(hours=hours)
            commits = repo.get_commits(since=since)
            
            # Try to get the latest commit
            try:
                latest_commit = commits[0]
                return {
                    "status": "success",
                    "message": f"Found {commits.totalCount} commits in the last {hours} hours",
                    "last_commit": latest_commit.commit.message,
                    "last_commit_url": latest_commit.html_url
                }
            except IndexError:
                return {
                    "status": "success",
                    "message": f"No commits found in the last {hours} hours",
                    "last_commit": None,
                    "last_commit_url": None
                }
                
        except Exception as e:
            logger.error(
                "github_service.check_changes_error",
                service=service_name,
                error=str(e)
            )
            return {
                "status": "error",
                "message": f"Error checking changes: {str(e)}",
                "last_commit": None,
                "last_commit_url": None
            } 