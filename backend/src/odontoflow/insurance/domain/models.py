"""Insurance (TISS/Convenios) — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError


class TISSStatus(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"
    BILLED = "BILLED"
    PAID = "PAID"
    GLOSA = "GLOSA"  # rejected by insurance


@dataclass(frozen=True)
class TISSItem:
    """Value Object — Item de uma guia TISS."""

    tuss_code: str = ""
    description: str = ""
    tooth_number: Optional[int] = None
    quantity: int = 1
    authorized_quantity: Optional[int] = None


@dataclass
class InsuranceProvider(Entity):
    """Operadora / Convenio odontologico."""

    tenant_id: UUID = field(default=None)
    name: str = ""
    ans_code: str = ""
    active: bool = True

    def deactivate(self) -> None:
        self.active = False

    def activate(self) -> None:
        self.active = True


@dataclass
class TISSRequest(AggregateRoot):
    """Aggregate Root — Guia de Tratamento Odontologico (GTO)."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    insurance_provider_id: UUID = field(default=None)
    treatment_plan_id: Optional[UUID] = None
    items: list[TISSItem] = field(default_factory=list)
    status: TISSStatus = TISSStatus.PENDING
    authorization_number: Optional[str] = None
    submitted_at: Optional[datetime] = None
    authorized_at: Optional[datetime] = None
    denied_reason: Optional[str] = None
    billed_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    paid_amount_centavos: int = 0
    glosa_amount_centavos: int = 0
    glosa_reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def submit(self) -> None:
        """Envia guia para a operadora."""
        if self.status != TISSStatus.PENDING:
            raise ValidationError(
                f"Guia nao pode ser enviada no status {self.status.value}"
            )
        if not self.items:
            raise ValidationError("Guia precisa ter ao menos um item")
        self.submitted_at = datetime.now(timezone.utc)

    def authorize(self, authorization_number: str) -> None:
        """Autoriza guia pela operadora."""
        if self.status not in (TISSStatus.PENDING,):
            raise ValidationError(
                f"Guia nao pode ser autorizada no status {self.status.value}"
            )
        if not authorization_number or not authorization_number.strip():
            raise ValidationError("Numero de autorizacao e obrigatorio")
        self.status = TISSStatus.AUTHORIZED
        self.authorization_number = authorization_number.strip()
        self.authorized_at = datetime.now(timezone.utc)

    def deny(self, reason: str) -> None:
        """Nega guia pela operadora."""
        if self.status not in (TISSStatus.PENDING,):
            raise ValidationError(
                f"Guia nao pode ser negada no status {self.status.value}"
            )
        if not reason or not reason.strip():
            raise ValidationError("Motivo da negativa e obrigatorio")
        self.status = TISSStatus.DENIED
        self.denied_reason = reason.strip()

    def bill(self) -> None:
        """Fatura guia para cobranca."""
        if self.status != TISSStatus.AUTHORIZED:
            raise ValidationError(
                f"Guia precisa estar AUTHORIZED para faturar, status atual: {self.status.value}"
            )
        self.status = TISSStatus.BILLED
        self.billed_at = datetime.now(timezone.utc)

    def record_payment(
        self,
        paid_amount_centavos: int,
        glosa_amount_centavos: int = 0,
        glosa_reason: Optional[str] = None,
    ) -> None:
        """Registra pagamento recebido da operadora."""
        if self.status != TISSStatus.BILLED:
            raise ValidationError(
                f"Guia precisa estar BILLED para registrar pagamento, status atual: {self.status.value}"
            )
        if paid_amount_centavos < 0:
            raise ValidationError("Valor pago nao pode ser negativo")

        self.paid_amount_centavos = paid_amount_centavos
        self.paid_at = datetime.now(timezone.utc)

        if glosa_amount_centavos > 0:
            self.glosa_amount_centavos = glosa_amount_centavos
            self.glosa_reason = glosa_reason.strip() if glosa_reason else None
            self.status = TISSStatus.GLOSA
        else:
            self.status = TISSStatus.PAID
