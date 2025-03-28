from typing import Any

import structlog

from src.handlers.base import BaseHandler
from src.models.events import OpsgenieEvent

logger = structlog.get_logger()


class StubHandler(BaseHandler):
    """Stub handler for testing purposes."""

    async def handle(self, event: OpsgenieEvent) -> dict[str, Any]:
        """Log the event and return a stub response."""
        logger.info(
            "stub_handler.received_event",
            action=event.action,
            alert_id=event.alert.alert_id,
            integration=event.integration_name,
        )
        
        return {
            "status": "processed",
            "handler": "stub",
            "event_action": event.action,
            "alert_id": event.alert.alert_id,
        } 