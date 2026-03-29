"""Testes dos use cases de Scheduling."""
import pytest
from datetime import datetime, time, date, timezone
from uuid import uuid4
from odontoflow.scheduling.application.commands.book_appointment import BookAppointmentCommand
from odontoflow.scheduling.application.commands.update_appointment_status import UpdateAppointmentStatusCommand
from odontoflow.scheduling.domain.models import ProviderSchedule, WorkingHours
from odontoflow.scheduling.infrastructure.in_memory_scheduling_repo import (
    InMemoryAppointmentRepository, InMemoryProviderScheduleRepository
)
from odontoflow.shared.event_bus import EventBus

class TestBookAppointment:
    @pytest.mark.asyncio
    async def test_book_successfully(self):
        apt_repo = InMemoryAppointmentRepository()
        sched_repo = InMemoryProviderScheduleRepository()
        bus = EventBus()

        provider_id = uuid4()
        schedule = ProviderSchedule(
            provider_id=provider_id,
            working_hours=[WorkingHours(day_of_week=1, start_time=time(8, 0), end_time=time(18, 0))]
        )
        await sched_repo.save(schedule)

        cmd = BookAppointmentCommand(
            tenant_id=uuid4(),
            patient_id=uuid4(),
            provider_id=provider_id,
            start_at=datetime(2026, 4, 7, 9, 0, tzinfo=timezone.utc),
            duration_minutes=30,
        )
        apt = await cmd.execute(apt_repo, sched_repo, bus)
        assert apt.id is not None
        assert apt.time_slot.duration_minutes == 30

    @pytest.mark.asyncio
    async def test_conflict_raises(self):
        apt_repo = InMemoryAppointmentRepository()
        sched_repo = InMemoryProviderScheduleRepository()
        bus = EventBus()

        provider_id = uuid4()
        tenant_id = uuid4()
        schedule = ProviderSchedule(
            provider_id=provider_id,
            working_hours=[WorkingHours(day_of_week=1, start_time=time(8, 0), end_time=time(18, 0))]
        )
        await sched_repo.save(schedule)

        # Book first
        cmd1 = BookAppointmentCommand(
            tenant_id=tenant_id, patient_id=uuid4(), provider_id=provider_id,
            start_at=datetime(2026, 4, 7, 9, 0, tzinfo=timezone.utc),
        )
        await cmd1.execute(apt_repo, sched_repo, bus)

        # Book same slot
        cmd2 = BookAppointmentCommand(
            tenant_id=tenant_id, patient_id=uuid4(), provider_id=provider_id,
            start_at=datetime(2026, 4, 7, 9, 0, tzinfo=timezone.utc),
        )
        with pytest.raises(Exception, match="ocupado"):
            await cmd2.execute(apt_repo, sched_repo, bus)

class TestUpdateStatus:
    @pytest.mark.asyncio
    async def test_confirm(self):
        apt_repo = InMemoryAppointmentRepository()
        sched_repo = InMemoryProviderScheduleRepository()
        bus = EventBus()

        provider_id = uuid4()
        await sched_repo.save(ProviderSchedule(
            provider_id=provider_id,
            working_hours=[WorkingHours(day_of_week=1, start_time=time(8, 0), end_time=time(18, 0))]
        ))

        book = BookAppointmentCommand(
            tenant_id=uuid4(), patient_id=uuid4(), provider_id=provider_id,
            start_at=datetime(2026, 4, 7, 10, 0, tzinfo=timezone.utc),
        )
        apt = await book.execute(apt_repo, sched_repo, bus)

        cmd = UpdateAppointmentStatusCommand(appointment_id=apt.id, action="confirm")
        await cmd.execute(apt_repo, bus)

        updated = await apt_repo.get_by_id(apt.id)
        assert updated.status.value == "CONFIRMED"
