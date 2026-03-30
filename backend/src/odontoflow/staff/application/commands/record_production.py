"""Command — Registrar producao de profissional."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.staff.domain.models import ProductionEntry
from odontoflow.staff.domain.repositories import ProductionRepository, StaffRepository


@dataclass
class RecordProductionCommand:
    staff_id: UUID
    tenant_id: UUID
    procedure_description: str
    revenue_centavos: int
    patient_name: str
    date: date
    treatment_item_id: Optional[UUID] = None
    procedure_category: Optional[str] = None

    async def execute(
        self,
        staff_repo: StaffRepository,
        production_repo: ProductionRepository,
    ) -> ProductionEntry:
        member = await staff_repo.get_by_id(self.staff_id)
        if not member:
            raise NotFoundError("StaffMember", str(self.staff_id))

        commission = member.get_commission_for(
            self.procedure_category, self.revenue_centavos
        )

        entry = ProductionEntry(
            id=uuid4(),
            staff_id=self.staff_id,
            tenant_id=self.tenant_id,
            treatment_item_id=self.treatment_item_id,
            procedure_description=self.procedure_description,
            revenue_centavos=self.revenue_centavos,
            commission_centavos=commission,
            patient_name=self.patient_name,
            date=self.date,
        )
        await production_repo.save(entry)
        return entry
