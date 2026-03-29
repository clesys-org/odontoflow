"""Patient Repository Protocol."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.patient.domain.models import Patient


class PatientRepository(Protocol):
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]: ...
    async def get_by_cpf(self, cpf: str) -> Optional[Patient]: ...
    async def save(self, patient: Patient) -> None: ...
    async def update(self, patient: Patient) -> None: ...
    async def delete(self, patient_id: UUID) -> bool: ...
    async def search(
        self,
        query: str = "",
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Patient], int]:
        """Returns (patients, total_count) for pagination."""
        ...
    async def count(self) -> int: ...
