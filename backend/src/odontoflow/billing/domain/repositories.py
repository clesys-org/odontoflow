"""Billing Repository Protocols."""
from __future__ import annotations

from datetime import date
from typing import Optional, Protocol
from uuid import UUID

from odontoflow.billing.domain.models import Invoice
from odontoflow.shared.domain.types import InvoiceStatus


class InvoiceRepository(Protocol):
    async def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]: ...

    async def get_by_patient(self, patient_id: UUID) -> list[Invoice]: ...

    async def get_all(
        self,
        status: Optional[InvoiceStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[Invoice]: ...

    async def save(self, invoice: Invoice) -> None: ...

    async def update(self, invoice: Invoice) -> None: ...

    async def get_dashboard_data(self) -> dict: ...
