"""Query — Listar guias TISS."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.insurance.domain.models import TISSRequest, TISSStatus
from odontoflow.insurance.domain.repositories import TISSRequestRepository


@dataclass
class ListTISSRequestsQuery:
    """Input data para listagem de guias TISS."""

    tenant_id: UUID = field(default=None)
    status: Optional[TISSStatus] = None
    patient_id: Optional[UUID] = None

    async def execute(self, repo: TISSRequestRepository) -> list[TISSRequest]:
        return await repo.get_all(
            tenant_id=self.tenant_id,
            status=self.status,
            patient_id=self.patient_id,
        )
