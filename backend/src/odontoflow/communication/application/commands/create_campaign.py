"""Use case — Criar campanha de mensagens."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import (
    Campaign,
    MessageChannel,
    MessageType,
)
from odontoflow.communication.domain.repositories import (
    CampaignRepository,
    MessageTemplateRepository,
)
from odontoflow.shared.domain.errors import NotFoundError, ValidationError


@dataclass
class CreateCampaignCommand:
    """Input data para criacao de campanha."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    message_type: MessageType = MessageType.CUSTOM
    channel: MessageChannel = MessageChannel.WHATSAPP
    template_id: UUID = field(default=None)
    target_filter: dict = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None

    async def execute(
        self,
        campaign_repo: CampaignRepository,
        template_repo: MessageTemplateRepository,
    ) -> Campaign:
        if not self.name or not self.name.strip():
            raise ValidationError("Nome da campanha e obrigatorio")

        # Validate template exists
        template = await template_repo.get_by_id(self.template_id)
        if not template:
            raise NotFoundError("MessageTemplate", str(self.template_id))

        campaign = Campaign(
            tenant_id=self.tenant_id,
            name=self.name.strip(),
            message_type=self.message_type,
            channel=self.channel,
            template_id=self.template_id,
            target_filter=self.target_filter,
        )

        if self.scheduled_at:
            campaign.schedule(self.scheduled_at)

        await campaign_repo.save(campaign)
        return campaign
