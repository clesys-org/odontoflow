"""Query — Listar campanhas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import Campaign, CampaignStatus
from odontoflow.communication.domain.repositories import CampaignRepository


@dataclass
class ListCampaignsQuery:
    """Input data para listagem de campanhas."""

    tenant_id: UUID = field(default=None)
    status: Optional[CampaignStatus] = None

    async def execute(self, repo: CampaignRepository) -> list[Campaign]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            status=self.status,
        )
