"""Query — Obter paciente por ID."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.patient.domain.models import Patient
from odontoflow.patient.domain.repositories import PatientRepository
from odontoflow.shared.domain.errors import NotFoundError


@dataclass
class GetPatientQuery:
    """Retorna um unico paciente pelo ID."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)

    async def execute(self, repo: PatientRepository) -> Patient:
        patient = await repo.get_by_id(self.patient_id)
        if patient is None:
            raise NotFoundError("Paciente", str(self.patient_id))
        return patient
