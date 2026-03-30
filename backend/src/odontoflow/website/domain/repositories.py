"""Website Repository Protocols."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.website.domain.models import ClinicWebsite


class WebsiteRepository(Protocol):
    async def get_by_id(self, website_id: UUID) -> Optional[ClinicWebsite]: ...

    async def get_by_tenant_id(self, tenant_id: UUID) -> Optional[ClinicWebsite]: ...

    async def get_by_slug(self, slug: str) -> Optional[ClinicWebsite]: ...

    async def save(self, website: ClinicWebsite) -> None: ...

    async def update(self, website: ClinicWebsite) -> None: ...
