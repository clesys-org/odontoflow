"""Query — Dashboard financeiro."""
from __future__ import annotations

from dataclasses import dataclass

from odontoflow.billing.domain.repositories import InvoiceRepository


@dataclass
class FinanceDashboardQuery:
    """Retorna totais financeiros (receita, a receber, a pagar)."""

    async def execute(self, repo: InvoiceRepository) -> dict:
        return await repo.get_dashboard_data()
