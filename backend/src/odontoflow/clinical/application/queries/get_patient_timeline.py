"""Query — Obter timeline clinica do paciente (CQRS read model)."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.clinical.domain.repositories import ClinicalRepository


@dataclass
class GetPatientTimelineQuery:
    """Input data para consulta de timeline clinica."""

    patient_id: UUID = field(default=None)
    page: int = 1
    page_size: int = 20

    async def execute(self, repo: ClinicalRepository) -> tuple[list[dict], int]:
        """Returns (timeline_entries, total_count)."""
        return await repo.get_timeline(
            patient_id=self.patient_id,
            page=self.page,
            page_size=self.page_size,
        )
