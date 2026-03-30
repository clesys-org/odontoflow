"""Use case — Atualizar site da clinica."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.website.domain.models import ServiceItem
from odontoflow.website.domain.repositories import WebsiteRepository


@dataclass
class ServiceItemInput:
    name: str = ""
    description: str = ""
    icon: str = ""


@dataclass
class UpdateWebsiteCommand:
    """Input data para atualizacao do site."""

    tenant_id: UUID = field(default=None)
    clinic_name: Optional[str] = None
    tagline: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    services: Optional[list[ServiceItemInput]] = None
    working_hours_text: Optional[str] = None
    social_links: Optional[dict] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    google_maps_embed: Optional[str] = None
    booking_enabled: Optional[bool] = None

    async def execute(self, repo: WebsiteRepository):
        website = await repo.get_by_tenant_id(self.tenant_id)
        if not website:
            raise NotFoundError("ClinicWebsite", str(self.tenant_id))

        website.update_info(
            clinic_name=self.clinic_name,
            tagline=self.tagline,
            description=self.description,
            phone=self.phone,
            whatsapp=self.whatsapp,
            email=self.email,
            address=self.address,
            logo_url=self.logo_url,
            primary_color=self.primary_color,
            working_hours_text=self.working_hours_text,
            social_links=self.social_links,
            seo_title=self.seo_title,
            seo_description=self.seo_description,
            google_maps_embed=self.google_maps_embed,
            booking_enabled=self.booking_enabled,
        )

        if self.services is not None:
            service_items = [
                ServiceItem(
                    name=s.name,
                    description=s.description,
                    icon=s.icon,
                )
                for s in self.services
            ]
            website.set_services(service_items)

        await repo.update(website)
        return website
