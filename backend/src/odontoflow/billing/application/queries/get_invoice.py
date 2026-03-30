"""Query — Obter fatura por ID."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.billing.domain.repositories import InvoiceRepository


@dataclass
class GetInvoiceQuery:
    """Input data para consulta de fatura."""

    invoice_id: UUID = field(default=None)

    async def execute(self, repo: InvoiceRepository) -> Optional[Invoice]:
        return await repo.get_by_id(self.invoice_id)
