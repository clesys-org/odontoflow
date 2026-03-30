"""Use case — Criar fatura."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID

from odontoflow.billing.domain.models import Installment, Invoice
from odontoflow.billing.domain.repositories import InvoiceRepository
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.types import InvoiceStatus


@dataclass
class InstallmentInput:
    number: int = 1
    due_date: date = field(default=None)
    amount_centavos: int = 0


@dataclass
class CreateInvoiceCommand:
    """Input data para criacao de fatura."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    treatment_plan_id: Optional[UUID] = None
    description: str = ""
    total_centavos: int = 0
    installments: list[InstallmentInput] = field(default_factory=list)

    async def execute(self, repo: InvoiceRepository) -> Invoice:
        if not self.description or not self.description.strip():
            raise ValidationError("Descricao da fatura e obrigatoria.")
        if self.total_centavos <= 0:
            raise ValidationError("Valor total deve ser maior que zero.")

        invoice = Invoice(
            patient_id=self.patient_id,
            tenant_id=self.tenant_id,
            treatment_plan_id=self.treatment_plan_id,
            description=self.description.strip(),
            total_centavos=self.total_centavos,
            status=InvoiceStatus.SENT,
        )

        for inst_input in self.installments:
            installment = Installment(
                invoice_id=invoice.id,
                number=inst_input.number,
                due_date=inst_input.due_date,
                amount_centavos=inst_input.amount_centavos,
            )
            invoice.add_installment(installment)

        await repo.save(invoice)
        return invoice
