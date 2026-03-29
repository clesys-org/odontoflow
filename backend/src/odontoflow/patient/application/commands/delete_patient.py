"""Use case — Excluir paciente (soft delete / arquivamento)."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.patient.domain.repositories import PatientRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class DeletePatientCommand:
    """Soft delete — arquiva o paciente em vez de remover fisicamente (LGPD)."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)

    async def execute(self, repo: PatientRepository) -> None:
        patient = await repo.get_by_id(self.patient_id)
        if patient is None:
            raise NotFoundError("Paciente", str(self.patient_id))

        patient.archive()
        await repo.update(patient)
