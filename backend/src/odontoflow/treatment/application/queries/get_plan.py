"""Query — Obter plano de tratamento por ID."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.treatment.domain.models import TreatmentPlan
from odontoflow.treatment.domain.repositories import TreatmentPlanRepository


@dataclass
class GetPlanQuery:
    """Input data para consulta de plano."""

    plan_id: UUID = field(default=None)

    async def execute(self, repo: TreatmentPlanRepository) -> Optional[TreatmentPlan]:
        return await repo.get_by_id(self.plan_id)
