"""Use case — Atualizar dente no odontograma."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.clinical.domain.models import Tooth, ToothSurface
from odontoflow.clinical.domain.repositories import ClinicalRepository
from odontoflow.shared.domain.types import ToothStatus
from odontoflow.shared.domain.value_objects import ToothNumber


@dataclass
class UpdateOdontogramCommand:
    """Input data para atualizar um dente no odontograma."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    tooth_number: int = 0
    status: ToothStatus = ToothStatus.PRESENT
    surfaces: list[ToothSurface] = field(default_factory=list)
    notes: Optional[str] = None
    updated_by: UUID = field(default=None)

    async def execute(self, repo: ClinicalRepository) -> Tooth:
        # Valida numero do dente via Value Object
        ToothNumber(self.tooth_number)

        record = await repo.get_or_create_record(self.patient_id, self.tenant_id)

        tooth = record.update_tooth(
            tooth_number=self.tooth_number,
            status=self.status,
            surfaces=self.surfaces,
            notes=self.notes,
            updated_by=self.updated_by,
        )

        await repo.save_tooth(tooth)
        await repo.save_record(record)

        return tooth
