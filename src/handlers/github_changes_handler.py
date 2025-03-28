from typing import Any, Optional

import structlog

from core.config import settings
from handlers.base import BaseHandler
from models.events import OpsgenieEvent
from services.github.service import GitHubService
from utils.alert_parser import parse_alert_info


logger = structlog.get_logger()


class GitHubChangesHandler(BaseHandler):
    """Handler for checking recent GitHub changes when health check fails."""
    
    def __init__(self) -> None:
        """Initialize handler."""
        self.github_service: Optional[GitHubService] = None
    
    def _ensure_github_service(self) -> None:
        """Ensure GitHub service is initialized."""
        if not settings.github_token:
            raise ValueError("GitHub token is not configured")
        if self.github_service is None:
            self.github_service = GitHubService(token=settings.github_token)
    
    async def handle(self, event: OpsgenieEvent) -> dict[str, Any]:
        """Handle the event by checking for recent GitHub changes.
        
        Args:
            event: The Opsgenie event to handle
            
        Returns:
            Dictionary containing processing results
        """
        try:
            self._ensure_github_service()
            
            # Extract labels from description
            description_lines = event.alert.description.split('\n')
            labels_section = False
            labels: dict[str, str] = {}
            
            for line in description_lines:
                if line.strip() == "Labels:":
                    labels_section = True
                    continue
                if labels_section and line.startswith("- "):
                    try:
                        key, value = line.replace("- ", "").split(" = ")
                        labels[key.strip()] = value.strip()
                    except ValueError:
                        continue
                elif labels_section and not line.startswith("- "):
                    break
            
            # Parse alert information
            alert_info = parse_alert_info(event.alert.description, labels)
            
            logger.info(
                "github_changes_handler.checking_changes",
                service=alert_info.service_name,
                environment=alert_info.environment,
                cluster=alert_info.cluster
            )
            
            # Check for recent changes
            changes = await self.github_service.check_recent_changes(
                alert_info.service_name
            )
            
            return {
                "status": "processed",
                "handler": "github_changes",
                "alert_info": {
                    "service": alert_info.service_name,
                    "environment": alert_info.environment,
                    "domain": alert_info.domain,
                    "cluster": alert_info.cluster,
                    "health_endpoint": alert_info.health_endpoint
                },
                "github_changes": changes
            }
            
        except Exception as e:
            logger.exception(
                "github_changes_handler.processing_error",
                error=str(e),
                alert_id=event.alert.alert_id
            )
            return {
                "status": "error",
                "handler": "github_changes",
                "error": str(e)
            } 