"""Use case — Executar campanha de mensagens."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.communication.domain.repositories import CampaignRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class ExecuteCampaignCommand:
    """Input data para execucao de campanha."""

    campaign_id: UUID = field(default=None)

    async def execute(self, repo: CampaignRepository):
        campaign = await repo.get_by_id(self.campaign_id)
        if not campaign:
            raise NotFoundError("Campaign", str(self.campaign_id))

        campaign.execute()
        await repo.update(campaign)
        return campaign
