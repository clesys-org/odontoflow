"""Pydantic v2 schemas for Communication endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CreateTemplateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    message_type: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=2000)


class SendMessageRequest(BaseModel):
    patient_id: str
    channel: str = Field(min_length=1)
    message_type: str = Field(min_length=1)
    content: Optional[str] = None
    template_id: Optional[str] = None
    template_variables: dict[str, str] = Field(default_factory=dict)


class CreateCampaignRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    message_type: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    template_id: str
    target_filter: dict = Field(default_factory=dict)
    scheduled_at: Optional[str] = None  # ISO datetime


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TemplateResponse(BaseModel):
    id: str
    name: str
    message_type: str
    channel: str
    content: str
    active: bool
    created_at: str


class TemplatesListResponse(BaseModel):
    templates: list[TemplateResponse]
    total: int


class MessageResponse(BaseModel):
    id: str
    patient_id: str
    channel: str
    message_type: str
    content: str
    status: str
    sent_at: Optional[str] = None
    delivered_at: Optional[str] = None
    error_message: Optional[str] = None
    campaign_id: Optional[str] = None
    created_at: str


class MessagesListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int


class CampaignResponse(BaseModel):
    id: str
    name: str
    message_type: str
    channel: str
    template_id: str
    target_filter: dict
    scheduled_at: Optional[str] = None
    messages_total: int
    messages_sent: int
    messages_failed: int
    status: str
    created_at: str


class CampaignsListResponse(BaseModel):
    campaigns: list[CampaignResponse]
    total: int
