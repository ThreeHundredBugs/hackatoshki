from typing import Any, Optional
import structlog
from opsgenie_sdk import (
    AlertApi,
    Configuration,
    ApiClient,
    AddNoteToAlertPayload,
)

logger = structlog.get_logger()


class OpsgenieService:
    """Service for interacting with Opsgenie API."""
    
    def __init__(self, api_key: str) -> None:
        """Initialize Opsgenie service.
        
        Args:
            api_key: Opsgenie API key
        """
        self._api_key = api_key
        self._alert_api: Optional[AlertApi] = None
        logger.info("opsgenie_service.initialized")
    
    def _ensure_initialized(self) -> None:
        """Ensure Opsgenie client is initialized."""
        if self._alert_api is None:
            configuration = Configuration()
            configuration.api_key['Authorization'] = self._api_key
            api_client = ApiClient(configuration=configuration)
            self._alert_api = AlertApi(api_client=api_client)
    
    async def add_note(self, alert_id: str, note: str, user: str) -> dict[str, Any]:
        """Add a note to an alert.
        
        Args:
            alert_id: ID of the alert
            note: Note text to add
            user: User who is adding the note
            
        Returns:
            Dictionary containing the response from Opsgenie
            
        Raises:
            Exception: If there is an error adding the note
        """
        try:
            self._ensure_initialized()
            
            payload = AddNoteToAlertPayload(
                user=user,
                note=note,
            )
            
            response = self._alert_api.add_note_to_alert(
                identifier=alert_id,
                identifier_type="id",
                add_note_to_alert_payload=payload,
            )
            
            logger.info(
                "opsgenie_service.note_added",
                alert_id=alert_id,
                result=response.request_id,
            )
            
            return {
                "status": "success",
                "request_id": response.request_id,
            }
            
        except Exception as e:
            logger.exception(
                "opsgenie_service.add_note_error",
                alert_id=alert_id,
                error=str(e),
            )
            return {
                "status": "error",
                "error": str(e),
            } 