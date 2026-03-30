"""In-memory implementation of Website repository for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.website.domain.models import ClinicWebsite


class InMemoryWebsiteRepository:
    """Dict-based website repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, ClinicWebsite] = {}

    async def get_by_id(self, website_id: UUID) -> Optional[ClinicWebsite]:
        return self._store.get(website_id)

    async def get_by_tenant_id(self, tenant_id: UUID) -> Optional[ClinicWebsite]:
        for website in self._store.values():
            if website.tenant_id == tenant_id:
                return website
        return None

    async def get_by_slug(self, slug: str) -> Optional[ClinicWebsite]:
        for website in self._store.values():
            if website.slug == slug and website.published:
                return website
        return None

    async def save(self, website: ClinicWebsite) -> None:
        self._store[website.id] = website

    async def update(self, website: ClinicWebsite) -> None:
        self._store[website.id] = website
