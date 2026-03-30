"""Query — Obter site publico da clinica (sem autenticacao)."""
from __future__ import annotations

from dataclasses import dataclass

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.website.domain.models import ClinicWebsite
from odontoflow.website.domain.repositories import WebsiteRepository


@dataclass
class GetPublicWebsiteQuery:
    """Input data para obtencao do site publico via slug."""

    slug: str = ""

    async def execute(self, repo: WebsiteRepository) -> ClinicWebsite:
        website = await repo.get_by_slug(self.slug)
        if not website:
            raise NotFoundError("ClinicWebsite", self.slug)
        return website
