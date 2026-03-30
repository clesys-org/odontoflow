"""Use case — Enviar mensagem para paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.communication.domain.models import (
    Message,
    MessageChannel,
    MessageType,
)
from odontoflow.communication.domain.repositories import (
    MessageRepository,
    MessageTemplateRepository,
)
from odontoflow.shared.domain.errors import NotFoundError, ValidationError


@dataclass
class SendMessageCommand:
    """Input data para envio de mensagem."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    channel: MessageChannel = MessageChannel.WHATSAPP
    message_type: MessageType = MessageType.CUSTOM
    content: Optional[str] = None
    template_id: Optional[UUID] = None
    template_variables: dict[str, str] = field(default_factory=dict)

    async def execute(
        self,
        message_repo: MessageRepository,
        template_repo: Optional[MessageTemplateRepository] = None,
    ) -> Message:
        # Resolve content from template or direct content
        final_content = self.content

        if self.template_id:
            if not template_repo:
                raise ValidationError("Template repository necessario para usar template")
            template = await template_repo.get_by_id(self.template_id)
            if not template:
                raise NotFoundError("MessageTemplate", str(self.template_id))
            final_content = template.render(self.template_variables)

        if not final_content or not final_content.strip():
            raise ValidationError("Conteudo da mensagem e obrigatorio")

        message = Message(
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
            channel=self.channel,
            message_type=self.message_type,
            content=final_content,
        )
        message.send()
        await message_repo.save(message)
        return message
