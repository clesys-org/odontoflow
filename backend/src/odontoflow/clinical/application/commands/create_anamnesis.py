"""Use case — Criar anamnese do paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.clinical.domain.models import Anamnesis, PatientRecord
from odontoflow.clinical.domain.repositories import ClinicalRepository
from odontoflow.shared.domain.errors import ValidationError


@dataclass
class CreateAnamnesisCommand:
    """Input data para criacao de anamnese."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    chief_complaint: str = ""
    medical_history: dict = field(default_factory=dict)
    dental_history: dict = field(default_factory=dict)
    created_by: UUID = field(default=None)

    async def execute(self, repo: ClinicalRepository) -> Anamnesis:
        if not self.chief_complaint or not self.chief_complaint.strip():
            raise ValidationError("Queixa principal e obrigatoria.")

        record = await repo.get_or_create_record(self.patient_id, self.tenant_id)

        anamnesis = Anamnesis(
            patient_record_id=record.id,
            chief_complaint=self.chief_complaint.strip(),
            medical_history=dict(self.medical_history),
            dental_history=dict(self.dental_history),
            created_by=self.created_by,
        )

        record.set_anamnesis(anamnesis)
        await repo.save_anamnesis(anamnesis)
        await repo.save_record(record)

        return anamnesis
