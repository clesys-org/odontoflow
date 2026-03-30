"""Query — Listar mensagens."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import Message
from odontoflow.communication.domain.repositories import MessageRepository


@dataclass
class ListMessagesQuery:
    """Input data para listagem de mensagens."""

    tenant_id: UUID = field(default=None)
    patient_id: Optional[UUID] = None

    async def execute(self, repo: MessageRepository) -> list[Message]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
        )
