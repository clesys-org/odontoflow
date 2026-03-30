"""Communication — Domain Models."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError


class MessageChannel(str, Enum):
    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    EMAIL = "EMAIL"


class MessageStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class MessageType(str, Enum):
    APPOINTMENT_REMINDER = "APPOINTMENT_REMINDER"
    APPOINTMENT_CONFIRMATION = "APPOINTMENT_CONFIRMATION"
    BIRTHDAY_GREETING = "BIRTHDAY_GREETING"
    RECALL_CHECKUP = "RECALL_CHECKUP"
    PAYMENT_REMINDER = "PAYMENT_REMINDER"
    CUSTOM = "CUSTOM"


class CampaignStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass
class MessageTemplate(Entity):
    """Template reutilizavel para mensagens — suporta placeholders."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    message_type: MessageType = MessageType.CUSTOM
    channel: MessageChannel = MessageChannel.WHATSAPP
    content: str = ""  # supports {{patient_name}}, {{date}}, {{time}}
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def render(self, variables: dict[str, str]) -> str:
        """Substitui placeholders no conteudo do template."""
        rendered = self.content
        for key, value in variables.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return rendered

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True


@dataclass
class Message(AggregateRoot):
    """Aggregate Root — Mensagem enviada a um paciente."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    channel: MessageChannel = MessageChannel.WHATSAPP
    message_type: MessageType = MessageType.CUSTOM
    content: str = ""  # rendered content (placeholders replaced)
    status: MessageStatus = MessageStatus.PENDING
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    campaign_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def send(self) -> None:
        """Marca mensagem como enviada (PENDING -> SENT)."""
        if self.status != MessageStatus.PENDING:
            raise ValidationError(
                f"Mensagem nao pode ser enviada no status {self.status.value}"
            )
        if not self.content or not self.content.strip():
            raise ValidationError("Conteudo da mensagem e obrigatorio")
        self.status = MessageStatus.SENT
        self.sent_at = datetime.now(timezone.utc)

    def mark_delivered(self) -> None:
        """Marca mensagem como entregue (SENT -> DELIVERED)."""
        if self.status != MessageStatus.SENT:
            raise ValidationError(
                f"Mensagem precisa estar SENT para marcar entregue, status atual: {self.status.value}"
            )
        self.status = MessageStatus.DELIVERED
        self.delivered_at = datetime.now(timezone.utc)

    def mark_failed(self, error: str) -> None:
        """Marca mensagem como falha."""
        if not error or not error.strip():
            raise ValidationError("Mensagem de erro e obrigatoria")
        self.status = MessageStatus.FAILED
        self.error_message = error.strip()


@dataclass
class Campaign(AggregateRoot):
    """Aggregate Root — Campanha de mensagens em massa."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    message_type: MessageType = MessageType.CUSTOM
    channel: MessageChannel = MessageChannel.WHATSAPP
    template_id: UUID = field(default=None)
    target_filter: dict = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None  # None = send now
    messages_total: int = 0
    messages_sent: int = 0
    messages_failed: int = 0
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def schedule(self, scheduled_at: datetime) -> None:
        """Agenda a campanha para envio futuro."""
        if self.status != CampaignStatus.DRAFT:
            raise ValidationError(
                f"Campanha precisa estar DRAFT para agendar, status atual: {self.status.value}"
            )
        self.scheduled_at = scheduled_at
        self.status = CampaignStatus.SCHEDULED

    def execute(self) -> None:
        """Inicia execucao da campanha."""
        if self.status not in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED):
            raise ValidationError(
                f"Campanha nao pode ser executada no status {self.status.value}"
            )
        self.status = CampaignStatus.RUNNING

    def record_sent(self) -> None:
        """Registra uma mensagem enviada com sucesso."""
        self.messages_sent += 1

    def record_failed(self) -> None:
        """Registra uma mensagem que falhou."""
        self.messages_failed += 1

    def complete(self) -> None:
        """Marca campanha como concluida."""
        if self.status != CampaignStatus.RUNNING:
            raise ValidationError(
                f"Campanha precisa estar RUNNING para concluir, status atual: {self.status.value}"
            )
        self.status = CampaignStatus.COMPLETED

    def cancel(self) -> None:
        """Cancela campanha."""
        if self.status in (CampaignStatus.COMPLETED, CampaignStatus.CANCELLED):
            raise ValidationError(
                f"Campanha nao pode ser cancelada no status {self.status.value}"
            )
        self.status = CampaignStatus.CANCELLED
