"""Use case — Atualizar paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from uuid import UUID

from odontoflow.patient.domain.repositories import PatientRepository
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError


@dataclass
class UpdatePatientCommand:
    """Input data para atualizacao de paciente."""

    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    updates: dict[str, Any] = field(default_factory=dict)

    async def execute(self, repo: PatientRepository) -> None:
        patient = await repo.get_by_id(self.patient_id)
        if patient is None:
            raise NotFoundError("Paciente", str(self.patient_id))

        # Se CPF esta sendo alterado, validar unicidade
        new_cpf = self.updates.get("cpf")
        if new_cpf and new_cpf != patient.cpf:
            existing = await repo.get_by_cpf(new_cpf)
            if existing is not None and existing.id != self.patient_id:
                raise ConflictError(f"Ja existe paciente com CPF {new_cpf}.")

        # Validar full_name se estiver sendo alterado
        new_name = self.updates.get("full_name")
        if new_name is not None and not new_name.strip():
            raise ValidationError("Nome completo nao pode ficar vazio.")

        # Campos protegidos que nao podem ser alterados via update generico
        protected = {"id", "tenant_id", "created_at", "_domain_events"}
        safe_updates = {
            k: v for k, v in self.updates.items() if k not in protected
        }

        patient.update_info(**safe_updates)
        await repo.update(patient)
