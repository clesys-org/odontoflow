"""Use case — Criar site da clinica."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.errors import ConflictError, ValidationError
from odontoflow.website.domain.models import ClinicWebsite, ServiceItem
from odontoflow.website.domain.repositories import WebsiteRepository


@dataclass
class ServiceItemInput:
    name: str = ""
    description: str = ""
    icon: str = ""


@dataclass
class CreateWebsiteCommand:
    """Input data para criacao do site da clinica."""

    tenant_id: UUID = field(default=None)
    clinic_name: str = ""
    slug: str = ""
    tagline: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    primary_color: str = "#0d9488"
    services: list[ServiceItemInput] = field(default_factory=list)
    working_hours_text: Optional[str] = None

    async def execute(self, repo: WebsiteRepository) -> ClinicWebsite:
        if not self.clinic_name or not self.clinic_name.strip():
            raise ValidationError("Nome da clinica e obrigatorio")
        if not self.slug or not self.slug.strip():
            raise ValidationError("Slug e obrigatorio")
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", self.slug):
            raise ValidationError(
                "Slug deve conter apenas letras minusculas, numeros e hifens"
            )

        # Check tenant already has a website
        existing = await repo.get_by_tenant_id(self.tenant_id)
        if existing:
            raise ConflictError("Clinica ja possui um site cadastrado")

        services = [
            ServiceItem(
                name=s.name,
                description=s.description,
                icon=s.icon,
            )
            for s in self.services
        ]

        website = ClinicWebsite(
            tenant_id=self.tenant_id,
            clinic_name=self.clinic_name.strip(),
            slug=self.slug.strip(),
            tagline=self.tagline,
            description=self.description,
            phone=self.phone,
            whatsapp=self.whatsapp,
            email=self.email,
            address=self.address,
            primary_color=self.primary_color,
            services=services,
            working_hours_text=self.working_hours_text,
        )
        await repo.save(website)
        return website
