"""In-memory repository implementations for Scheduling."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from odontoflow.scheduling.domain.models import Appointment, ProviderSchedule
from odontoflow.shared.domain.types import AppointmentStatus


class InMemoryAppointmentRepository:
    def __init__(self) -> None:
        self._appointments: dict[UUID, Appointment] = {}

    async def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        return self._appointments.get(appointment_id)

    async def save(self, appointment: Appointment) -> None:
        self._appointments[appointment.id] = appointment

    async def update(self, appointment: Appointment) -> None:
        self._appointments[appointment.id] = appointment

    async def get_by_date_range(
        self, provider_id: UUID, start: datetime, end: datetime,
    ) -> list[Appointment]:
        return [
            a for a in self._appointments.values()
            if a.provider_id == provider_id
            and a.time_slot
            and a.time_slot.start >= start
            and a.time_slot.start < end
            and a.status not in (AppointmentStatus.CANCELLED,)
        ]

    async def get_by_patient(self, patient_id: UUID) -> list[Appointment]:
        return [
            a for a in self._appointments.values()
            if a.patient_id == patient_id
        ]

    async def get_day_schedule(self, provider_id: UUID, day: date) -> list[Appointment]:
        day_start = datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        return await self.get_by_date_range(provider_id, day_start, day_end)


class InMemoryProviderScheduleRepository:
    def __init__(self) -> None:
        self._schedules: dict[UUID, ProviderSchedule] = {}

    async def get_by_provider(self, provider_id: UUID) -> Optional[ProviderSchedule]:
        return self._schedules.get(provider_id)

    async def save(self, schedule: ProviderSchedule) -> None:
        self._schedules[schedule.provider_id] = schedule

    async def update(self, schedule: ProviderSchedule) -> None:
        self._schedules[schedule.provider_id] = schedule

    async def get_all(self) -> list[ProviderSchedule]:
        return list(self._schedules.values())
