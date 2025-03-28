from typing import Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    name: str
    type: str


class Alert(BaseModel):
    alert_id: str = Field(alias="alertId")
    message: str
    tags: list[str]
    tiny_id: str = Field(alias="tinyId")
    alias: str
    created_at: int = Field(alias="createdAt")
    updated_at: int = Field(alias="updatedAt")
    username: str
    user_id: str = Field(alias="userId")
    entity: str
    description: Optional[str] = None
    priority: Optional[str] = None
    note: Optional[str] = None


class OpsgenieEvent(BaseModel):
    """Opsgenie webhook event model."""
    action: str
    integration_id: str = Field(alias="integrationId")
    integration_name: str = Field(alias="integrationName")
    source: Source
    alert: Alert

    class Config:
        populate_by_name = True 