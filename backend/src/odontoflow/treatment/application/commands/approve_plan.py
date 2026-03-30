"""Use case — Aprovar plano de tratamento."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.treatment.domain.models import TreatmentPlan
from odontoflow.treatment.domain.repositories import TreatmentPlanRepository


@dataclass
class ApprovePlanCommand:
    """Input data para aprovacao de plano."""

    plan_id: UUID = field(default=None)
    approved_by: str = ""

    async def execute(self, repo: TreatmentPlanRepository) -> TreatmentPlan:
        plan = await repo.get_by_id(self.plan_id)
        if not plan:
            raise NotFoundError("TreatmentPlan", str(self.plan_id))

        plan.approve(by=self.approved_by)
        await repo.update(plan)
        return plan
