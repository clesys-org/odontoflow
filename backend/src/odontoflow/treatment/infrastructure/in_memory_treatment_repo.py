"""In-memory implementation of Treatment repositories for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.treatment.domain.models import ProcedureCatalog, TreatmentPlan


class InMemoryTreatmentPlanRepository:
    """Dict-based treatment plan repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, TreatmentPlan] = {}

    async def get_by_id(self, plan_id: UUID) -> Optional[TreatmentPlan]:
        return self._store.get(plan_id)

    async def get_by_patient(self, patient_id: UUID) -> list[TreatmentPlan]:
        return [
            p for p in self._store.values()
            if p.patient_id == patient_id
        ]

    async def save(self, plan: TreatmentPlan) -> None:
        self._store[plan.id] = plan

    async def update(self, plan: TreatmentPlan) -> None:
        self._store[plan.id] = plan

    async def delete(self, plan_id: UUID) -> None:
        self._store.pop(plan_id, None)


class InMemoryProcedureCatalogRepository:
    """Dict-based procedure catalog repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, ProcedureCatalog] = {}

    async def get_by_id(self, procedure_id: UUID) -> Optional[ProcedureCatalog]:
        return self._store.get(procedure_id)

    async def get_by_tuss_code(self, tuss_code: str) -> Optional[ProcedureCatalog]:
        return next(
            (p for p in self._store.values() if p.tuss_code == tuss_code),
            None,
        )

    async def get_all(self, category: Optional[str] = None) -> list[ProcedureCatalog]:
        procedures = list(self._store.values())
        if category:
            procedures = [p for p in procedures if p.category == category]
        return procedures

    async def save(self, procedure: ProcedureCatalog) -> None:
        self._store[procedure.id] = procedure

    async def update(self, procedure: ProcedureCatalog) -> None:
        self._store[procedure.id] = procedure
