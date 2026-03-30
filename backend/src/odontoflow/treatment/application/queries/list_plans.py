"""Query — Listar planos de tratamento de um paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.treatment.domain.models import TreatmentPlan
from odontoflow.treatment.domain.repositories import TreatmentPlanRepository


@dataclass
class ListPlansQuery:
    """Input data para listagem de planos."""

    patient_id: UUID = field(default=None)

    async def execute(self, repo: TreatmentPlanRepository) -> list[TreatmentPlan]:
        return await repo.get_by_patient(self.patient_id)
