"""Testes dos use cases de Patient."""

import pytest
from uuid import uuid4

from odontoflow.patient.application.commands.create_patient import CreatePatientCommand
from odontoflow.patient.application.commands.update_patient import UpdatePatientCommand
from odontoflow.patient.infrastructure.in_memory_patient_repo import InMemoryPatientRepository
from odontoflow.shared.event_bus import EventBus


class TestCreatePatient:
    @pytest.mark.asyncio
    async def test_create_simple_patient(self):
        repo = InMemoryPatientRepository()
        cmd = CreatePatientCommand(
            tenant_id=uuid4(),
            full_name="Maria Silva",
        )
        patient = await cmd.execute(repo)
        assert patient.full_name == "Maria Silva"
        assert patient.id is not None

    @pytest.mark.asyncio
    async def test_create_with_cpf(self):
        repo = InMemoryPatientRepository()
        cmd = CreatePatientCommand(
            tenant_id=uuid4(),
            full_name="Joao",
            cpf="52998224725",
        )
        patient = await cmd.execute(repo)
        assert patient.cpf == "52998224725"

    @pytest.mark.asyncio
    async def test_duplicate_cpf_raises(self):
        repo = InMemoryPatientRepository()
        tid = uuid4()
        cmd1 = CreatePatientCommand(tenant_id=tid, full_name="A", cpf="52998224725")
        await cmd1.execute(repo)
        cmd2 = CreatePatientCommand(tenant_id=tid, full_name="B", cpf="52998224725")
        with pytest.raises(Exception, match="CPF"):
            await cmd2.execute(repo)

    @pytest.mark.asyncio
    async def test_emits_created_event(self):
        repo = InMemoryPatientRepository()
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        from odontoflow.shared.domain.events import PatientCreated

        bus.subscribe(PatientCreated, handler)

        cmd = CreatePatientCommand(tenant_id=uuid4(), full_name="Test")
        patient = await cmd.execute(repo)

        # Events are collected from the aggregate, then published manually
        for evt in patient.collect_events():
            await bus.publish(evt)

        assert len(received) == 1


class TestUpdatePatient:
    @pytest.mark.asyncio
    async def test_update_name(self):
        repo = InMemoryPatientRepository()
        create = CreatePatientCommand(tenant_id=uuid4(), full_name="Original")
        patient = await create.execute(repo)

        update = UpdatePatientCommand(
            tenant_id=patient.tenant_id,
            patient_id=patient.id,
            updates={"full_name": "Updated"},
        )
        await update.execute(repo)

        refreshed = await repo.get_by_id(patient.id)
        assert refreshed.full_name == "Updated"
