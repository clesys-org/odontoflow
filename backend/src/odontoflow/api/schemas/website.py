"""Pydantic v2 schemas for Website Builder endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class ServiceItemRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    icon: str = Field(default="", max_length=50)


class CreateWebsiteRequest(BaseModel):
    clinic_name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=100, pattern=r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
    tagline: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    primary_color: str = "#0d9488"
    services: list[ServiceItemRequest] = Field(default_factory=list)
    working_hours_text: Optional[str] = None


class UpdateWebsiteRequest(BaseModel):
    clinic_name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    tagline: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    services: Optional[list[ServiceItemRequest]] = None
    working_hours_text: Optional[str] = None
    social_links: Optional[dict] = None
    seo_title: Optional[str] = Field(default=None, max_length=200)
    seo_description: Optional[str] = Field(default=None, max_length=500)
    google_maps_embed: Optional[str] = None
    booking_enabled: Optional[bool] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class ServiceItemResponse(BaseModel):
    name: str
    description: str
    icon: str


class WebsiteResponse(BaseModel):
    id: str
    clinic_name: str
    slug: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    services: list[ServiceItemResponse]
    working_hours_text: Optional[str] = None
    social_links: dict
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    google_maps_embed: Optional[str] = None
    booking_enabled: bool
    published: bool
    created_at: str
    updated_at: str


class PublicWebsiteResponse(BaseModel):
    """Resposta publica — sem campos internos."""

    clinic_name: str
    slug: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str
    services: list[ServiceItemResponse]
    working_hours_text: Optional[str] = None
    social_links: dict
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    google_maps_embed: Optional[str] = None
    booking_enabled: bool
