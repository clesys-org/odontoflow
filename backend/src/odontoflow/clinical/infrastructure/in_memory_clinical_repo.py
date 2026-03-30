"""In-memory implementation of ClinicalRepository for testing."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from odontoflow.clinical.domain.models import (
    Anamnesis,
    ClinicalNote,
    ConsentForm,
    PatientRecord,
    Prescription,
    Tooth,
)


class InMemoryClinicalRepository:
    """Dict-based clinical repository — uso exclusivo em testes."""

    def __init__(self) -> None:
        self._store: dict[UUID, PatientRecord] = {}  # keyed by patient_id

    async def get_or_create_record(
        self, patient_id: UUID, tenant_id: UUID
    ) -> PatientRecord:
        if patient_id not in self._store:
            record = PatientRecord(patient_id=patient_id, tenant_id=tenant_id)
            self._store[patient_id] = record
        return self._store[patient_id]

    async def get_record(self, patient_id: UUID) -> Optional[PatientRecord]:
        return self._store.get(patient_id)

    async def save_record(self, record: PatientRecord) -> None:
        self._store[record.patient_id] = record

    async def save_anamnesis(self, anamnesis: Anamnesis) -> None:
        # Persisted via save_record (aggregate consistency)
        pass

    async def save_tooth(self, tooth: Tooth) -> None:
        # Persisted via save_record (aggregate consistency)
        pass

    async def save_note(self, note: ClinicalNote) -> None:
        # Persisted via save_record (aggregate consistency)
        pass

    async def save_prescription(self, prescription: Prescription) -> None:
        # Persisted via save_record (aggregate consistency)
        pass

    async def save_consent(self, consent: ConsentForm) -> None:
        # Persisted via save_record (aggregate consistency)
        pass

    async def get_timeline(
        self,
        patient_id: UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """Monta timeline a partir do prontuario em memoria."""
        record = self._store.get(patient_id)
        if not record:
            return [], 0

        entries: list[dict] = []

        # Anamnese
        if record.anamnesis:
            entries.append(
                {
                    "type": "anamnesis",
                    "id": str(record.anamnesis.id),
                    "summary": record.anamnesis.chief_complaint,
                    "created_at": record.anamnesis.created_at.isoformat(),
                    "created_by": str(record.anamnesis.created_by)
                    if record.anamnesis.created_by
                    else None,
                }
            )

        # Notas clinicas
        for note in record.notes:
            entries.append(
                {
                    "type": "note",
                    "id": str(note.id),
                    "note_type": note.note_type.value,
                    "summary": note.content[:100],
                    "is_signed": note.is_signed,
                    "created_at": note.created_at.isoformat(),
                    "created_by": str(note.created_by) if note.created_by else None,
                }
            )

        # Prescricoes
        for rx in record.prescriptions:
            med_names = [i.medication_name for i in rx.items]
            entries.append(
                {
                    "type": "prescription",
                    "id": str(rx.id),
                    "summary": ", ".join(med_names),
                    "created_at": rx.created_at.isoformat(),
                    "created_by": str(rx.created_by) if rx.created_by else None,
                }
            )

        # Consentimentos
        for consent in record.consent_forms:
            entries.append(
                {
                    "type": "consent",
                    "id": str(consent.id),
                    "summary": consent.form_type,
                    "signed": consent.signed_at is not None,
                    "created_at": (consent.signed_at or consent.signed_at)
                    if consent.signed_at
                    else None,
                }
            )

        # Ordenar por data (mais recente primeiro)
        entries.sort(
            key=lambda e: e.get("created_at") or "",
            reverse=True,
        )

        total = len(entries)
        start = (page - 1) * page_size
        end = start + page_size

        return entries[start:end], total
