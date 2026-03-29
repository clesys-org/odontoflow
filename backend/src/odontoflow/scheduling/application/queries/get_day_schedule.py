"""Query — Agenda do dia para um provider."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from odontoflow.scheduling.domain.models import Appointment, TimeSlot
from odontoflow.scheduling.domain.repositories import AppointmentRepository, ProviderScheduleRepository
from odontoflow.scheduling.domain.services import SchedulingService


@dataclass
class DayScheduleResult:
    appointments: list[Appointment]
    available_slots: list[TimeSlot]


@dataclass
class GetDayScheduleQuery:
    provider_id: UUID = field(default=None)
    target_date: date = field(default=None)
    slot_duration: int = 30

    async def execute(
        self,
        appointment_repo: AppointmentRepository,
        schedule_repo: ProviderScheduleRepository,
    ) -> DayScheduleResult:
        appointments = await appointment_repo.get_day_schedule(
            self.provider_id, self.target_date,
        )

        schedule = await schedule_repo.get_by_provider(self.provider_id)
        available = []
        if schedule:
            available = SchedulingService.get_available_slots(
                schedule, appointments, self.target_date, self.slot_duration,
            )

        return DayScheduleResult(
            appointments=sorted(appointments, key=lambda a: a.time_slot.start if a.time_slot else a.created_at),
            available_slots=available,
        )
