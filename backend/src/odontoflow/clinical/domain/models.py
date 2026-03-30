"""Clinical Records — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.types import (
    NoteType,
    SurfaceCondition,
    SurfacePosition,
    ToothStatus,
)


@dataclass(frozen=True)
class ToothSurface:
    position: SurfacePosition
    condition: SurfaceCondition = SurfaceCondition.HEALTHY


@dataclass(frozen=True)
class PrescriptionItem:
    medication_name: str = ""
    dosage: str = ""
    frequency: str = ""
    duration: str = ""
    instructions: str = ""


@dataclass
class Anamnesis(Entity):
    patient_record_id: UUID = field(default=None)
    chief_complaint: str = ""
    medical_history: dict = field(default_factory=dict)
    dental_history: dict = field(default_factory=dict)
    created_by: UUID = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signed_at: Optional[datetime] = None
    digital_signature: Optional[dict] = None


@dataclass
class Tooth(Entity):
    patient_record_id: UUID = field(default=None)
    tooth_number: int = 0  # FDI notation
    status: ToothStatus = ToothStatus.PRESENT
    surfaces: list[ToothSurface] = field(default_factory=list)
    notes: Optional[str] = None
    updated_by: UUID = field(default=None)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ClinicalNote(Entity):
    patient_record_id: UUID = field(default=None)
    note_type: NoteType = NoteType.EVOLUTION
    content: str = ""
    tooth_references: list[int] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    created_by: UUID = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signed_at: Optional[datetime] = None
    digital_signature: Optional[dict] = None

    @property
    def is_signed(self) -> bool:
        return self.signed_at is not None


@dataclass
class Prescription(Entity):
    patient_record_id: UUID = field(default=None)
    items: list[PrescriptionItem] = field(default_factory=list)
    created_by: UUID = field(default=None)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConsentForm(Entity):
    patient_record_id: UUID = field(default=None)
    form_type: str = ""
    content: str = ""
    patient_signature: Optional[str] = None  # base64
    signed_at: Optional[datetime] = None


@dataclass
class PatientRecord(AggregateRoot):
    """Aggregate Root — prontuario clinico de um paciente."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    anamnesis: Optional[Anamnesis] = None
    teeth: list[Tooth] = field(default_factory=list)
    notes: list[ClinicalNote] = field(default_factory=list)
    prescriptions: list[Prescription] = field(default_factory=list)
    consent_forms: list[ConsentForm] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def set_anamnesis(self, anamnesis: Anamnesis) -> None:
        self.anamnesis = anamnesis

    def update_tooth(
        self,
        tooth_number: int,
        status: ToothStatus,
        surfaces: list[ToothSurface],
        notes: Optional[str],
        updated_by: UUID,
    ) -> Tooth:
        existing = next(
            (t for t in self.teeth if t.tooth_number == tooth_number), None
        )
        if existing:
            existing.status = status
            existing.surfaces = surfaces
            existing.notes = notes
            existing.updated_by = updated_by
            existing.updated_at = datetime.now(timezone.utc)
            return existing
        tooth = Tooth(
            patient_record_id=self.id,
            tooth_number=tooth_number,
            status=status,
            surfaces=surfaces,
            notes=notes,
            updated_by=updated_by,
        )
        self.teeth.append(tooth)
        return tooth

    def add_note(self, note: ClinicalNote) -> None:
        self.notes.append(note)

    def sign_note(self, note_id: UUID) -> None:
        note = next((n for n in self.notes if n.id == note_id), None)
        if not note:
            raise ValueError(f"Nota {note_id} nao encontrada")
        if note.is_signed:
            raise ValueError("Nota ja assinada (imutavel)")
        note.signed_at = datetime.now(timezone.utc)

    def add_prescription(self, prescription: Prescription) -> None:
        self.prescriptions.append(prescription)

    def add_consent(self, consent: ConsentForm) -> None:
        self.consent_forms.append(consent)

    def get_tooth(self, tooth_number: int) -> Optional[Tooth]:
        return next(
            (t for t in self.teeth if t.tooth_number == tooth_number), None
        )
