"""In-memory implementation of InvoiceRepository for testing."""
from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.shared.domain.types import InstallmentStatus, InvoiceStatus


class InMemoryInvoiceRepository:
    """Dict-based invoice repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Invoice] = {}

    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        return self._store.get(invoice_id)

    async def get_by_patient(self, patient_id: UUID) -> list[Invoice]:
        return [
            inv for inv in self._store.values()
            if inv.patient_id == patient_id
        ]

    async def get_all(
        self,
        status: Optional[InvoiceStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[Invoice]:
        invoices = list(self._store.values())
        if status:
            invoices = [inv for inv in invoices if inv.status == status]
        if date_from:
            invoices = [
                inv for inv in invoices
                if inv.created_at.date() >= date_from
            ]
        if date_to:
            invoices = [
                inv for inv in invoices
                if inv.created_at.date() <= date_to
            ]
        return invoices

    async def save(self, invoice: Invoice) -> None:
        self._store[invoice.id] = invoice

    async def update(self, invoice: Invoice) -> None:
        self._store[invoice.id] = invoice

    async def get_dashboard_data(self) -> dict:
        """Calcula totais financeiros a partir dos dados em memoria."""
        invoices = list(self._store.values())

        total_receita = 0
        total_a_receber = 0

        for inv in invoices:
            if inv.status == InvoiceStatus.CANCELLED:
                continue
            paid = sum(
                i.amount_centavos for i in inv.installments
                if i.status == InstallmentStatus.PAID
            )
            pending = sum(
                i.amount_centavos for i in inv.installments
                if i.status != InstallmentStatus.PAID
            )
            total_receita += paid
            total_a_receber += pending

        return {
            "receita_centavos": total_receita,
            "a_receber_centavos": total_a_receber,
            "total_faturas": len(invoices),
        }
