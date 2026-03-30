"""Query — Relatorio de producao de profissional."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from odontoflow.staff.domain.models import ProductionEntry
from odontoflow.staff.domain.repositories import ProductionRepository


@dataclass
class StaffProductionReportQuery:
    staff_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    async def execute(self, repo: ProductionRepository) -> dict:
        entries = await repo.get_by_staff(
            self.staff_id, self.start_date, self.end_date
        )

        total_revenue = sum(e.revenue_centavos for e in entries)
        total_commission = sum(e.commission_centavos for e in entries)

        return {
            "staff_id": str(self.staff_id),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_revenue_centavos": total_revenue,
            "total_commission_centavos": total_commission,
            "entries_count": len(entries),
            "entries": entries,
        }
