"""Testes do Patient domain."""

import pytest
from datetime import date, datetime, timezone

from odontoflow.patient.domain.models import Patient, Address, LGPDConsent, Responsible
from odontoflow.shared.domain.types import Gender, PatientStatus


class TestPatient:
    def test_create_patient(self):
        p = Patient(full_name="Joao Silva", cpf="52998224725")
        assert p.full_name == "Joao Silva"
        assert p.status == PatientStatus.ACTIVE

    def test_is_minor_true(self):
        p = Patient(full_name="Crianca", birth_date=date(2015, 1, 1))
        assert p.is_minor is True

    def test_is_minor_false(self):
        p = Patient(full_name="Adulto", birth_date=date(1990, 1, 1))
        assert p.is_minor is False

    def test_archive(self):
        p = Patient(full_name="Test")
        p.archive()
        assert p.status == PatientStatus.ARCHIVED

    def test_reactivate(self):
        p = Patient(full_name="Test")
        p.archive()
        p.reactivate()
        assert p.status == PatientStatus.ACTIVE

    def test_update_emits_event(self):
        p = Patient(full_name="Test")
        p.update_info(full_name="Updated")
        events = p.collect_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "PatientUpdated"


class TestAddress:
    def test_frozen(self):
        a = Address(street="Rua A", city="SP", state="SP", zip_code="01234567")
        with pytest.raises(AttributeError):
            a.street = "Rua B"
