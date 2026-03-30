"""Use case — Executar item do plano de tratamento."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.treatment.domain.models import TreatmentItem, TreatmentPlan
from odontoflow.treatment.domain.repositories import TreatmentPlanRepository


@dataclass
class ExecuteItemCommand:
    """Input data para execucao de item."""

    plan_id: UUID = field(default=None)
    item_id: UUID = field(default=None)
    executed_by: str = ""

    async def execute(self, repo: TreatmentPlanRepository) -> TreatmentPlan:
        plan = await repo.get_by_id(self.plan_id)
        if not plan:
            raise NotFoundError("TreatmentPlan", str(self.plan_id))

        plan.execute_item(self.item_id, self.executed_by)
        await repo.update(plan)
        return plan
