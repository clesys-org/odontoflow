"""Communication Repository Protocols."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.communication.domain.models import (
    Campaign,
    CampaignStatus,
    Message,
    MessageTemplate,
    MessageType,
)


class MessageTemplateRepository(Protocol):
    async def get_by_id(self, template_id: UUID) -> Optional[MessageTemplate]: ...

    async def get_all(
        self,
        tenant_id: UUID,
        message_type: Optional[MessageType] = None,
        active_only: bool = True,
    ) -> list[MessageTemplate]: ...

    async def save(self, template: MessageTemplate) -> None: ...

    async def update(self, template: MessageTemplate) -> None: ...


class MessageRepository(Protocol):
    async def get_by_id(self, message_id: UUID) -> Optional[Message]: ...

    async def get_all(
        self,
        tenant_id: UUID,
        patient_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
    ) -> list[Message]: ...

    async def save(self, message: Message) -> None: ...

    async def update(self, message: Message) -> None: ...


class CampaignRepository(Protocol):
    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]: ...

    async def get_all(
        self,
        tenant_id: UUID,
        status: Optional[CampaignStatus] = None,
    ) -> list[Campaign]: ...

    async def save(self, campaign: Campaign) -> None: ...

    async def update(self, campaign: Campaign) -> None: ...
