"""Website Builder — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError


@dataclass(frozen=True)
class ServiceItem:
    """Value Object — Servico oferecido pela clinica."""

    name: str = ""
    description: str = ""
    icon: str = ""


@dataclass
class ClinicWebsite(AggregateRoot):
    """Aggregate Root — Site publico da clinica, gerado automaticamente."""

    tenant_id: UUID = field(default=None)
    clinic_name: str = ""
    slug: str = ""
    tagline: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = "#0d9488"
    services: list[ServiceItem] = field(default_factory=list)
    working_hours_text: Optional[str] = None
    social_links: dict = field(default_factory=dict)
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    google_maps_embed: Optional[str] = None
    booking_enabled: bool = True
    published: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def publish(self) -> None:
        """Publica o site da clinica."""
        if not self.clinic_name or not self.clinic_name.strip():
            raise ValidationError("Nome da clinica e obrigatorio para publicar")
        if not self.slug or not self.slug.strip():
            raise ValidationError("Slug e obrigatorio para publicar")
        self.published = True
        self.updated_at = datetime.now(timezone.utc)

    def unpublish(self) -> None:
        """Remove site do ar."""
        self.published = False
        self.updated_at = datetime.now(timezone.utc)

    def toggle_publish(self) -> None:
        """Alterna estado de publicacao."""
        if self.published:
            self.unpublish()
        else:
            self.publish()

    def update_info(
        self,
        clinic_name: Optional[str] = None,
        tagline: Optional[str] = None,
        description: Optional[str] = None,
        phone: Optional[str] = None,
        whatsapp: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        working_hours_text: Optional[str] = None,
        social_links: Optional[dict] = None,
        seo_title: Optional[str] = None,
        seo_description: Optional[str] = None,
        google_maps_embed: Optional[str] = None,
        booking_enabled: Optional[bool] = None,
    ) -> None:
        """Atualiza informacoes do site."""
        if clinic_name is not None:
            if not clinic_name.strip():
                raise ValidationError("Nome da clinica nao pode ser vazio")
            self.clinic_name = clinic_name.strip()
        if tagline is not None:
            self.tagline = tagline
        if description is not None:
            self.description = description
        if phone is not None:
            self.phone = phone
        if whatsapp is not None:
            self.whatsapp = whatsapp
        if email is not None:
            self.email = email
        if address is not None:
            self.address = address
        if logo_url is not None:
            self.logo_url = logo_url
        if primary_color is not None:
            self.primary_color = primary_color
        if working_hours_text is not None:
            self.working_hours_text = working_hours_text
        if social_links is not None:
            self.social_links = social_links
        if seo_title is not None:
            self.seo_title = seo_title
        if seo_description is not None:
            self.seo_description = seo_description
        if google_maps_embed is not None:
            self.google_maps_embed = google_maps_embed
        if booking_enabled is not None:
            self.booking_enabled = booking_enabled
        self.updated_at = datetime.now(timezone.utc)

    def set_services(self, services: list[ServiceItem]) -> None:
        """Define lista de servicos."""
        self.services = services
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class BookingWidget(Entity):
    """Widget de agendamento online — embed no site da clinica."""

    tenant_id: UUID = field(default=None)
    website_id: UUID = field(default=None)
    available_types: list[str] = field(default_factory=lambda: ["consulta", "avaliacao"])
    max_days_ahead: int = 30
    require_phone: bool = True
    active: bool = True

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True
