"""Testes do Clinical Records domain."""

import pytest
from uuid import uuid4

from odontoflow.clinical.domain.models import (
    Anamnesis,
    ClinicalNote,
    ConsentForm,
    PatientRecord,
    Prescription,
    PrescriptionItem,
    Tooth,
    ToothSurface,
)
from odontoflow.clinical.domain.services import OdontogramService
from odontoflow.shared.domain.types import (
    NoteType,
    SurfaceCondition,
    SurfacePosition,
    ToothStatus,
)


class TestPatientRecord:
    def test_create_record(self):
        pid = uuid4()
        tid = uuid4()
        record = PatientRecord(patient_id=pid, tenant_id=tid)
        assert record.patient_id == pid
        assert record.tenant_id == tid
        assert record.anamnesis is None
        assert record.teeth == []
        assert record.notes == []
        assert record.prescriptions == []
        assert record.consent_forms == []

    def test_set_anamnesis(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        anamnesis = Anamnesis(
            patient_record_id=record.id,
            chief_complaint="Dor de dente",
            created_by=uuid4(),
        )
        record.set_anamnesis(anamnesis)
        assert record.anamnesis is not None
        assert record.anamnesis.chief_complaint == "Dor de dente"

    def test_add_note(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        note = ClinicalNote(
            patient_record_id=record.id,
            note_type=NoteType.EVOLUTION,
            content="Paciente estavel",
            created_by=uuid4(),
        )
        record.add_note(note)
        assert len(record.notes) == 1
        assert record.notes[0].content == "Paciente estavel"

    def test_add_prescription(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        rx = Prescription(
            patient_record_id=record.id,
            items=[PrescriptionItem(medication_name="Amoxicilina", dosage="500mg")],
            created_by=uuid4(),
        )
        record.add_prescription(rx)
        assert len(record.prescriptions) == 1

    def test_add_consent(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        consent = ConsentForm(
            patient_record_id=record.id,
            form_type="tratamento_endodontico",
            content="Eu autorizo...",
        )
        record.add_consent(consent)
        assert len(record.consent_forms) == 1


class TestToothUpdate:
    def test_add_new_tooth(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        dentist = uuid4()
        tooth = record.update_tooth(
            tooth_number=11,
            status=ToothStatus.PRESENT,
            surfaces=[
                ToothSurface(position=SurfacePosition.MESIAL, condition=SurfaceCondition.CARIES),
            ],
            notes="Carie na mesial",
            updated_by=dentist,
        )
        assert tooth.tooth_number == 11
        assert tooth.status == ToothStatus.PRESENT
        assert len(tooth.surfaces) == 1
        assert tooth.surfaces[0].condition == SurfaceCondition.CARIES
        assert len(record.teeth) == 1

    def test_update_existing_tooth(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        dentist = uuid4()

        # Primeiro cria
        record.update_tooth(
            tooth_number=21,
            status=ToothStatus.PRESENT,
            surfaces=[],
            notes=None,
            updated_by=dentist,
        )

        # Depois atualiza
        tooth = record.update_tooth(
            tooth_number=21,
            status=ToothStatus.IMPLANT,
            surfaces=[
                ToothSurface(position=SurfacePosition.OCLUSAL, condition=SurfaceCondition.CROWN),
            ],
            notes="Implante realizado",
            updated_by=dentist,
        )

        assert tooth.status == ToothStatus.IMPLANT
        assert tooth.notes == "Implante realizado"
        # Nao deve duplicar
        assert len(record.teeth) == 1

    def test_get_tooth(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        record.update_tooth(
            tooth_number=36,
            status=ToothStatus.PRESENT,
            surfaces=[],
            notes=None,
            updated_by=uuid4(),
        )
        found = record.get_tooth(36)
        assert found is not None
        assert found.tooth_number == 36

        not_found = record.get_tooth(99)
        assert not_found is None


class TestNoteSigning:
    def test_sign_note(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        note = ClinicalNote(
            patient_record_id=record.id,
            content="Nota de evolucao",
            created_by=uuid4(),
        )
        record.add_note(note)
        assert note.is_signed is False

        record.sign_note(note.id)
        assert note.is_signed is True
        assert note.signed_at is not None

    def test_sign_already_signed_raises(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        note = ClinicalNote(
            patient_record_id=record.id,
            content="Nota",
            created_by=uuid4(),
        )
        record.add_note(note)
        record.sign_note(note.id)

        with pytest.raises(ValueError, match="imutavel"):
            record.sign_note(note.id)

    def test_sign_nonexistent_note_raises(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        with pytest.raises(ValueError, match="nao encontrada"):
            record.sign_note(uuid4())


class TestOdontogramService:
    def test_full_odontogram_returns_32_teeth(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        teeth = OdontogramService.get_full_odontogram(record)
        assert len(teeth) == 32

    def test_full_odontogram_includes_existing_teeth(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        dentist = uuid4()
        record.update_tooth(
            tooth_number=11,
            status=ToothStatus.ABSENT,
            surfaces=[],
            notes="Extraido",
            updated_by=dentist,
        )

        teeth = OdontogramService.get_full_odontogram(record)
        assert len(teeth) == 32

        tooth_11 = next(t for t in teeth if t.tooth_number == 11)
        assert tooth_11.status == ToothStatus.ABSENT
        assert tooth_11.notes == "Extraido"

    def test_full_odontogram_default_teeth_are_healthy(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        teeth = OdontogramService.get_full_odontogram(record)

        for tooth in teeth:
            assert tooth.status == ToothStatus.PRESENT
            assert len(tooth.surfaces) == 5
            for surface in tooth.surfaces:
                assert surface.condition == SurfaceCondition.HEALTHY

    def test_full_odontogram_correct_numbers(self):
        record = PatientRecord(patient_id=uuid4(), tenant_id=uuid4())
        teeth = OdontogramService.get_full_odontogram(record)
        numbers = [t.tooth_number for t in teeth]

        # Quadrante 1: 11-18
        for n in range(11, 19):
            assert n in numbers
        # Quadrante 2: 21-28
        for n in range(21, 29):
            assert n in numbers
        # Quadrante 3: 31-38
        for n in range(31, 39):
            assert n in numbers
        # Quadrante 4: 41-48
        for n in range(41, 49):
            assert n in numbers


class TestToothSurface:
    def test_frozen(self):
        s = ToothSurface(position=SurfacePosition.MESIAL, condition=SurfaceCondition.HEALTHY)
        with pytest.raises(AttributeError):
            s.condition = SurfaceCondition.CARIES


class TestPrescriptionItem:
    def test_frozen(self):
        item = PrescriptionItem(medication_name="Ibuprofeno", dosage="400mg")
        with pytest.raises(AttributeError):
            item.medication_name = "Paracetamol"
