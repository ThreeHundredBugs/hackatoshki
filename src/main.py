from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from core.config import settings
from handlers.stub_handler import StubHandler
from models.events import OpsgenieEvent
from handlers.github_changes_handler import GitHubChangesHandler
from services.opsgenie.service import OpsgenieService


# Configure structured logging
logger = structlog.get_logger()

app = FastAPI(
    title="Event Processor",
    description="Service to process Opsgenie events via integration",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize handlers and services
stub_handler = StubHandler()
github_changes_handler = GitHubChangesHandler()
opsgenie_service = OpsgenieService(api_key=settings.opsgenie_api_key)


def verify_api_key(x_actions_auth: str = Header(None)) -> None:
    """Verify the API key from the request header."""
    if not x_actions_auth:
        raise HTTPException(status_code=401, detail="API key is missing")
    if x_actions_auth != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.post("/api/v1/webhook")
async def webhook(
    request: Request,
    event: OpsgenieEvent,
) -> JSONResponse:
    """Handle Opsgenie webhook events.
    
    Args:
        request: The FastAPI request object.
        event: The Opsgenie event payload.
        
    Returns:
        JSON response with processing result.
    """
    verify_api_key(request.headers.get('X-Actions-Auth'))
    
    # Log the incoming event
    logger.info(
        "webhook.received_event",
        action=event.action,
        alert_id=event.alert.alert_id,
        integration=event.integration_name,
        client_host=request.client.host if request.client else None,
    )
    
    try:
        # For now, use the stub handler for all events
        result = await stub_handler.handle(event)
        
        # Add a note to the alert with the processing result
        note = f"Event processed by {result['handler']} handler with status: {result['status']}"
        if result.get('error'):
            note += f"\nError: {result['error']}"
        
        note_result = await opsgenie_service.add_note(
            alert_id=event.alert.alert_id,
            note=note,
        )
        
        # Include note result in the response
        result['note_result'] = note_result
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.exception(
            "webhook.processing_error",
            action=event.action,
            alert_id=event.alert.alert_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Error processing event: {str(e)}",
        ) 