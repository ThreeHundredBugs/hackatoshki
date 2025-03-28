from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Opsgenie Event Processor",
    description="Service to process Opsgenie events via webhook integration",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/health')
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {'status': 'healthy'} 