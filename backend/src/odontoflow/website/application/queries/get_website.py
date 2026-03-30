"""Query — Obter site da clinica (autenticado)."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.website.domain.models import ClinicWebsite
from odontoflow.website.domain.repositories import WebsiteRepository


@dataclass
class GetWebsiteQuery:
    """Input data para obtencao do site da clinica."""

    tenant_id: UUID = field(default=None)

    async def execute(self, repo: WebsiteRepository) -> ClinicWebsite:
        website = await repo.get_by_tenant_id(self.tenant_id)
        if not website:
            raise NotFoundError("ClinicWebsite", str(self.tenant_id))
        return website
