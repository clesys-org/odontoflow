"""Clinical Repository Protocol."""
from __future__ import annotations

from typing import Optional, Protocol
from uuid import UUID

from odontoflow.clinical.domain.models import (
    Anamnesis,
    ClinicalNote,
    ConsentForm,
    PatientRecord,
    Prescription,
    Tooth,
)


class ClinicalRepository(Protocol):
    async def get_or_create_record(
        self, patient_id: UUID, tenant_id: UUID
    ) -> PatientRecord: ...

    async def get_record(self, patient_id: UUID) -> Optional[PatientRecord]: ...

    async def save_record(self, record: PatientRecord) -> None: ...

    async def save_anamnesis(self, anamnesis: Anamnesis) -> None: ...

    async def save_tooth(self, tooth: Tooth) -> None: ...

    async def save_note(self, note: ClinicalNote) -> None: ...

    async def save_prescription(self, prescription: Prescription) -> None: ...

    async def save_consent(self, consent: ConsentForm) -> None: ...

    async def get_timeline(
        self,
        patient_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Returns (timeline_entries, total_count) for pagination."""
        ...
