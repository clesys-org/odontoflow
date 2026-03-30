"""Billing & Finance — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.events import InvoicePaid
from odontoflow.shared.domain.types import InstallmentStatus, InvoiceStatus, PaymentMethod


@dataclass
class Installment(Entity):
    """Parcela de uma fatura."""

    invoice_id: UUID = field(default=None)
    number: int = 1
    due_date: date = field(default=None)
    amount_centavos: int = 0
    payment_method: Optional[PaymentMethod] = None
    status: InstallmentStatus = InstallmentStatus.PENDING
    paid_at: Optional[datetime] = None


@dataclass
class Invoice(AggregateRoot):
    """Aggregate Root — Fatura de cobranca."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    treatment_plan_id: Optional[UUID] = None
    description: str = ""
    total_centavos: int = 0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    installments: list[Installment] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def amount_paid_centavos(self) -> int:
        return sum(
            i.amount_centavos for i in self.installments
            if i.status == InstallmentStatus.PAID
        )

    @property
    def amount_remaining_centavos(self) -> int:
        return self.total_centavos - self.amount_paid_centavos

    def add_installment(self, installment: Installment) -> None:
        installment.invoice_id = self.id
        self.installments.append(installment)

    def pay_installment(self, number: int, method: PaymentMethod) -> Installment:
        installment = next(
            (i for i in self.installments if i.number == number), None
        )
        if not installment:
            raise ValidationError(f"Parcela {number} nao encontrada na fatura")
        if installment.status == InstallmentStatus.PAID:
            raise ValidationError(f"Parcela {number} ja esta paga")

        installment.status = InstallmentStatus.PAID
        installment.payment_method = method
        installment.paid_at = datetime.now(timezone.utc)

        # Auto-update invoice status
        all_paid = all(
            i.status == InstallmentStatus.PAID for i in self.installments
        )
        some_paid = any(
            i.status == InstallmentStatus.PAID for i in self.installments
        )

        if all_paid:
            self.status = InvoiceStatus.PAID
            self.add_event(
                InvoicePaid(
                    invoice_id=self.id,
                    patient_id=self.patient_id,
                    amount_centavos=self.total_centavos,
                    tenant_id=self.tenant_id,
                )
            )
        elif some_paid:
            self.status = InvoiceStatus.PARTIAL

        return installment

    def cancel(self) -> None:
        if self.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
            raise ValidationError(
                f"Fatura nao pode ser cancelada no status {self.status.value}"
            )
        self.status = InvoiceStatus.CANCELLED
