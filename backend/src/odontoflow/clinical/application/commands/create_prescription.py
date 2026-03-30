"""Use case — Criar prescricao medica."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from odontoflow.clinical.domain.models import Prescription, PrescriptionItem
from odontoflow.clinical.domain.repositories import ClinicalRepository
from odontoflow.shared.domain.errors import ValidationError


@dataclass
class CreatePrescriptionCommand:
    """Input data para criacao de prescricao."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    items: list[PrescriptionItem] = field(default_factory=list)
    created_by: UUID = field(default=None)

    async def execute(self, repo: ClinicalRepository) -> Prescription:
        if not self.items:
            raise ValidationError("Prescricao deve conter ao menos um item.")

        for item in self.items:
            if not item.medication_name or not item.medication_name.strip():
                raise ValidationError("Nome do medicamento e obrigatorio.")

        record = await repo.get_or_create_record(self.patient_id, self.tenant_id)

        prescription = Prescription(
            patient_record_id=record.id,
            items=list(self.items),
            created_by=self.created_by,
        )

        record.add_prescription(prescription)

        await repo.save_prescription(prescription)
        await repo.save_record(record)

        return prescription
