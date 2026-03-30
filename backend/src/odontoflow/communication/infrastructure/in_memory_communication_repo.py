"""In-memory implementation of Communication repositories for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import (
    Campaign,
    CampaignStatus,
    Message,
    MessageTemplate,
    MessageType,
)


class InMemoryMessageTemplateRepository:
    """Dict-based message template repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, MessageTemplate] = {}

    async def get_by_id(self, template_id: UUID) -> Optional[MessageTemplate]:
        return self._store.get(template_id)

    async def get_all(
        self,
        tenant_id: UUID,
        message_type: Optional[MessageType] = None,
        active_only: bool = True,
    ) -> list[MessageTemplate]:
        templates = [
            t for t in self._store.values()
            if t.tenant_id == tenant_id
        ]
        if message_type:
            templates = [t for t in templates if t.message_type == message_type]
        if active_only:
            templates = [t for t in templates if t.active]
        return templates

    async def save(self, template: MessageTemplate) -> None:
        self._store[template.id] = template

    async def update(self, template: MessageTemplate) -> None:
        self._store[template.id] = template


class InMemoryMessageRepository:
    """Dict-based message repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Message] = {}

    async def get_by_id(self, message_id: UUID) -> Optional[Message]:
        return self._store.get(message_id)

    async def get_all(
        self,
        tenant_id: UUID,
        patient_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
    ) -> list[Message]:
        messages = [
            m for m in self._store.values()
            if m.tenant_id == tenant_id
        ]
        if patient_id:
            messages = [m for m in messages if m.patient_id == patient_id]
        if campaign_id:
            messages = [m for m in messages if m.campaign_id == campaign_id]
        return messages

    async def save(self, message: Message) -> None:
        self._store[message.id] = message

    async def update(self, message: Message) -> None:
        self._store[message.id] = message


class InMemoryCampaignRepository:
    """Dict-based campaign repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Campaign] = {}

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        return self._store.get(campaign_id)

    async def get_all(
        self,
        tenant_id: UUID,
        status: Optional[CampaignStatus] = None,
    ) -> list[Campaign]:
        campaigns = [
            c for c in self._store.values()
            if c.tenant_id == tenant_id
        ]
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        return campaigns

    async def save(self, campaign: Campaign) -> None:
        self._store[campaign.id] = campaign

    async def update(self, campaign: Campaign) -> None:
        self._store[campaign.id] = campaign
