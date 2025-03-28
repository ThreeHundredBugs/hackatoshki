from abc import ABC, abstractmethod
from typing import Any

from models.events import OpsgenieEvent


class BaseHandler(ABC):
    """Base class for all event handlers."""

    @abstractmethod
    async def handle(self, event: OpsgenieEvent) -> dict[str, Any]:
        """Process the event.
        
        Args:
            event: The Opsgenie event to process.
            
        Returns:
            A dictionary containing the processing result.
        """
        pass 