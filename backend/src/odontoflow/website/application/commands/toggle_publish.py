"""Use case — Alternar publicacao do site da clinica."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.website.domain.repositories import WebsiteRepository


@dataclass
class TogglePublishCommand:
    """Input data para alternar publicacao."""

    tenant_id: UUID = field(default=None)

    async def execute(self, repo: WebsiteRepository):
        website = await repo.get_by_tenant_id(self.tenant_id)
        if not website:
            raise NotFoundError("ClinicWebsite", str(self.tenant_id))

        website.toggle_publish()
        await repo.update(website)
        return website
