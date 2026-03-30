"""Use case — Cancelar fatura."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.billing.domain.repositories import InvoiceRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class CancelInvoiceCommand:
    """Input data para cancelamento de fatura."""

    invoice_id: UUID = field(default=None)

    async def execute(self, repo: InvoiceRepository) -> Invoice:
        invoice = await repo.get_by_id(self.invoice_id)
        if not invoice:
            raise NotFoundError("Invoice", str(self.invoice_id))

        invoice.cancel()
        await repo.update(invoice)
        return invoice
