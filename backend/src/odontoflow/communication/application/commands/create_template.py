"""Use case — Criar template de mensagem."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.communication.domain.models import (
    MessageChannel,
    MessageTemplate,
    MessageType,
)
from odontoflow.communication.domain.repositories import MessageTemplateRepository
from odontoflow.shared.domain.errors import ValidationError


@dataclass
class CreateTemplateCommand:
    """Input data para criacao de template."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    message_type: MessageType = MessageType.CUSTOM
    channel: MessageChannel = MessageChannel.WHATSAPP
    content: str = ""

    async def execute(self, repo: MessageTemplateRepository) -> MessageTemplate:
        if not self.name or not self.name.strip():
            raise ValidationError("Nome do template e obrigatorio")
        if not self.content or not self.content.strip():
            raise ValidationError("Conteudo do template e obrigatorio")

        template = MessageTemplate(
            tenant_id=self.tenant_id,
            name=self.name.strip(),
            message_type=self.message_type,
            channel=self.channel,
            content=self.content.strip(),
        )
        await repo.save(template)
        return template
