"""Use case — Criar nota clinica (evolucao/procedimento/observacao)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.clinical.domain.models import ClinicalNote
from odontoflow.clinical.domain.repositories import ClinicalRepository
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.events import ClinicalNoteSigned
from odontoflow.shared.domain.types import NoteType


@dataclass
class CreateClinicalNoteCommand:
    """Input data para criacao de nota clinica."""

    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    note_type: NoteType = NoteType.EVOLUTION
    content: str = ""
    tooth_references: list[int] = field(default_factory=list)
    attachments: list[dict] = field(default_factory=list)
    created_by: UUID = field(default=None)
    sign_immediately: bool = False

    async def execute(self, repo: ClinicalRepository) -> ClinicalNote:
        if not self.content or not self.content.strip():
            raise ValidationError("Conteudo da nota e obrigatorio.")

        record = await repo.get_or_create_record(self.patient_id, self.tenant_id)

        note = ClinicalNote(
            patient_record_id=record.id,
            note_type=self.note_type,
            content=self.content.strip(),
            tooth_references=list(self.tooth_references),
            attachments=list(self.attachments),
            created_by=self.created_by,
        )

        record.add_note(note)

        if self.sign_immediately:
            record.sign_note(note.id)
            record.add_event(
                ClinicalNoteSigned(
                    patient_record_id=record.id,
                    note_id=note.id,
                    provider_id=self.created_by,
                    tenant_id=self.tenant_id,
                )
            )

        await repo.save_note(note)
        await repo.save_record(record)

        return note
