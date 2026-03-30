"""Query — Listar faturas."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.billing.domain.repositories import InvoiceRepository
from odontoflow.shared.domain.types import InvoiceStatus


@dataclass
class ListInvoicesQuery:
    """Input data para listagem de faturas."""

    patient_id: Optional[UUID] = None
    status: Optional[InvoiceStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    async def execute(self, repo: InvoiceRepository) -> list[Invoice]:
        if self.patient_id:
            return await repo.get_by_patient(self.patient_id)
        return await repo.get_all(
            status=self.status,
            date_from=self.date_from,
            date_to=self.date_to,
        )
