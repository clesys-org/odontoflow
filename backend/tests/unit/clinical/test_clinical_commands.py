"""Testes dos use cases de Clinical Records."""

import pytest
from uuid import uuid4

from odontoflow.clinical.application.commands.create_anamnesis import (
    CreateAnamnesisCommand,
)
from odontoflow.clinical.application.commands.create_clinical_note import (
    CreateClinicalNoteCommand,
)
from odontoflow.clinical.application.commands.create_prescription import (
    CreatePrescriptionCommand,
)
from odontoflow.clinical.application.commands.update_odontogram import (
    UpdateOdontogramCommand,
)
from odontoflow.clinical.domain.models import PrescriptionItem, ToothSurface
from odontoflow.clinical.infrastructure.in_memory_clinical_repo import (
    InMemoryClinicalRepository,
)
from odontoflow.shared.domain.errors import ValidationError
from odontoflow.shared.domain.types import (
    NoteType,
    SurfaceCondition,
    SurfacePosition,
    ToothStatus,
)


class TestCreateAnamnesis:
    @pytest.mark.asyncio
    async def test_create_anamnesis(self):
        repo = InMemoryClinicalRepository()
        cmd = CreateAnamnesisCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            chief_complaint="Dor no dente 36",
            medical_history={"alergias": ["penicilina"]},
            dental_history={"ultima_visita": "2024-01-15"},
            created_by=uuid4(),
        )
        anamnesis = await cmd.execute(repo)
        assert anamnesis.chief_complaint == "Dor no dente 36"
        assert anamnesis.medical_history == {"alergias": ["penicilina"]}
        assert anamnesis.id is not None

    @pytest.mark.asyncio
    async def test_create_anamnesis_empty_complaint_raises(self):
        repo = InMemoryClinicalRepository()
        cmd = CreateAnamnesisCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            chief_complaint="",
            created_by=uuid4(),
        )
        with pytest.raises(ValidationError, match="Queixa principal"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_anamnesis_saved_in_record(self):
        repo = InMemoryClinicalRepository()
        pid = uuid4()
        tid = uuid4()
        cmd = CreateAnamnesisCommand(
            patient_id=pid,
            tenant_id=tid,
            chief_complaint="Sensibilidade",
            created_by=uuid4(),
        )
        await cmd.execute(repo)

        record = await repo.get_record(pid)
        assert record is not None
        assert record.anamnesis is not None
        assert record.anamnesis.chief_complaint == "Sensibilidade"


class TestUpdateOdontogram:
    @pytest.mark.asyncio
    async def test_update_tooth(self):
        repo = InMemoryClinicalRepository()
        cmd = UpdateOdontogramCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            tooth_number=11,
            status=ToothStatus.PRESENT,
            surfaces=[
                ToothSurface(
                    position=SurfacePosition.MESIAL,
                    condition=SurfaceCondition.CARIES,
                ),
            ],
            notes="Carie na mesial",
            updated_by=uuid4(),
        )
        tooth = await cmd.execute(repo)
        assert tooth.tooth_number == 11
        assert tooth.status == ToothStatus.PRESENT
        assert len(tooth.surfaces) == 1

    @pytest.mark.asyncio
    async def test_invalid_tooth_number_raises(self):
        repo = InMemoryClinicalRepository()
        cmd = UpdateOdontogramCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            tooth_number=99,  # invalido
            status=ToothStatus.PRESENT,
            updated_by=uuid4(),
        )
        with pytest.raises(ValueError, match="invalido"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_update_same_tooth_twice(self):
        repo = InMemoryClinicalRepository()
        pid = uuid4()
        tid = uuid4()
        dentist = uuid4()

        cmd1 = UpdateOdontogramCommand(
            patient_id=pid, tenant_id=tid,
            tooth_number=21, status=ToothStatus.PRESENT,
            surfaces=[], updated_by=dentist,
        )
        await cmd1.execute(repo)

        cmd2 = UpdateOdontogramCommand(
            patient_id=pid, tenant_id=tid,
            tooth_number=21, status=ToothStatus.IMPLANT,
            surfaces=[], notes="Implante", updated_by=dentist,
        )
        tooth = await cmd2.execute(repo)
        assert tooth.status == ToothStatus.IMPLANT

        record = await repo.get_record(pid)
        assert len(record.teeth) == 1


class TestCreateClinicalNote:
    @pytest.mark.asyncio
    async def test_create_note(self):
        repo = InMemoryClinicalRepository()
        cmd = CreateClinicalNoteCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            note_type=NoteType.EVOLUTION,
            content="Paciente relata melhora",
            created_by=uuid4(),
        )
        note = await cmd.execute(repo)
        assert note.content == "Paciente relata melhora"
        assert note.note_type == NoteType.EVOLUTION
        assert note.is_signed is False

    @pytest.mark.asyncio
    async def test_create_note_empty_content_raises(self):
        repo = InMemoryClinicalRepository()
        cmd = CreateClinicalNoteCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            content="",
            created_by=uuid4(),
        )
        with pytest.raises(ValidationError, match="Conteudo"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_create_note_with_immediate_sign(self):
        repo = InMemoryClinicalRepository()
        cmd = CreateClinicalNoteCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            content="Procedimento realizado",
            note_type=NoteType.PROCEDURE,
            created_by=uuid4(),
            sign_immediately=True,
        )
        note = await cmd.execute(repo)
        assert note.is_signed is True
        assert note.signed_at is not None

    @pytest.mark.asyncio
    async def test_signed_note_emits_event(self):
        repo = InMemoryClinicalRepository()
        pid = uuid4()
        tid = uuid4()
        cmd = CreateClinicalNoteCommand(
            patient_id=pid,
            tenant_id=tid,
            content="Nota assinada",
            created_by=uuid4(),
            sign_immediately=True,
        )
        await cmd.execute(repo)

        record = await repo.get_record(pid)
        events = record.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "ClinicalNoteSigned"


class TestCreatePrescription:
    @pytest.mark.asyncio
    async def test_create_prescription(self):
        repo = InMemoryClinicalRepository()
        cmd = CreatePrescriptionCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            items=[
                PrescriptionItem(
                    medication_name="Amoxicilina",
                    dosage="500mg",
                    frequency="8/8h",
                    duration="7 dias",
                ),
                PrescriptionItem(
                    medication_name="Ibuprofeno",
                    dosage="400mg",
                    frequency="6/6h",
                    duration="3 dias",
                ),
            ],
            created_by=uuid4(),
        )
        rx = await cmd.execute(repo)
        assert len(rx.items) == 2
        assert rx.items[0].medication_name == "Amoxicilina"

    @pytest.mark.asyncio
    async def test_empty_items_raises(self):
        repo = InMemoryClinicalRepository()
        cmd = CreatePrescriptionCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            items=[],
            created_by=uuid4(),
        )
        with pytest.raises(ValidationError, match="ao menos um item"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_empty_medication_name_raises(self):
        repo = InMemoryClinicalRepository()
        cmd = CreatePrescriptionCommand(
            patient_id=uuid4(),
            tenant_id=uuid4(),
            items=[PrescriptionItem(medication_name="", dosage="500mg")],
            created_by=uuid4(),
        )
        with pytest.raises(ValidationError, match="Nome do medicamento"):
            await cmd.execute(repo)

    @pytest.mark.asyncio
    async def test_prescription_saved_in_record(self):
        repo = InMemoryClinicalRepository()
        pid = uuid4()
        tid = uuid4()
        cmd = CreatePrescriptionCommand(
            patient_id=pid,
            tenant_id=tid,
            items=[PrescriptionItem(medication_name="Dipirona", dosage="1g")],
            created_by=uuid4(),
        )
        await cmd.execute(repo)

        record = await repo.get_record(pid)
        assert len(record.prescriptions) == 1
