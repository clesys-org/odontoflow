"""Query — Listar templates de mensagem."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import MessageTemplate, MessageType
from odontoflow.communication.domain.repositories import MessageTemplateRepository


@dataclass
class ListTemplatesQuery:
    """Input data para listagem de templates."""

    tenant_id: UUID = field(default=None)
    message_type: Optional[MessageType] = None

    async def execute(self, repo: MessageTemplateRepository) -> list[MessageTemplate]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            message_type=self.message_type,
        )
