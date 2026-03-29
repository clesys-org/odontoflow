"""In-memory implementation of PatientRepository for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.patient.domain.models import Patient


class InMemoryPatientRepository:
    """Dict-based patient repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, Patient] = {}

    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        return self._store.get(patient_id)

    async def get_by_cpf(self, cpf: str) -> Optional[Patient]:
        for patient in self._store.values():
            if patient.cpf == cpf:
                return patient
        return None

    async def save(self, patient: Patient) -> None:
        self._store[patient.id] = patient

    async def update(self, patient: Patient) -> None:
        self._store[patient.id] = patient

    async def delete(self, patient_id: UUID) -> bool:
        if patient_id in self._store:
            del self._store[patient_id]
            return True
        return False

    async def search(
        self,
        query: str = "",
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Patient], int]:
        """Returns (patients, total_count) for pagination."""
        results = list(self._store.values())

        # Filtro por status
        if status:
            results = [p for p in results if p.status.value == status]

        # Busca textual simples (nome, CPF, telefone, email)
        if query:
            q = query.lower()
            results = [
                p
                for p in results
                if q in (p.full_name or "").lower()
                or q in (p.cpf or "")
                or q in (p.phone or "")
                or q in (p.whatsapp or "")
                or q in (p.email or "").lower()
            ]

        # Ordenar por nome
        results.sort(key=lambda p: (p.full_name or "").lower())

        total = len(results)

        # Paginacao
        start = (page - 1) * page_size
        end = start + page_size
        page_results = results[start:end]

        return page_results, total

    async def count(self) -> int:
        return len(self._store)
