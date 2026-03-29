"""Query — Buscar pacientes com paginacao."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.patient.domain.models import Patient
from odontoflow.patient.domain.repositories import PatientRepository


@dataclass
class SearchPatientsQuery:
    """Busca pacientes por nome, CPF, telefone ou email."""

    tenant_id: UUID = field(default=None)
    query: str = ""
    status: Optional[str] = None
    page: int = 1
    page_size: int = 20

    async def execute(self, repo: PatientRepository) -> tuple[list[Patient], int]:
        """Retorna (lista_pacientes, total_count) para paginacao."""
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 20
        if self.page_size > 100:
            self.page_size = 100

        patients, total = await repo.search(
            query=self.query.strip(),
            status=self.status,
            page=self.page,
            page_size=self.page_size,
        )
        return patients, total
