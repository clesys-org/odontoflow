"""Query — Obter prontuario completo do paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.clinical.domain.models import PatientRecord
from odontoflow.clinical.domain.repositories import ClinicalRepository


@dataclass
class GetPatientRecordQuery:
    """Input data para consulta de prontuario."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)

    async def execute(self, repo: ClinicalRepository) -> Optional[PatientRecord]:
        record = await repo.get_record(self.patient_id)
        if record and record.tenant_id != self.tenant_id:
            return None
        return record
