"""Query — Slots disponiveis para agendamento."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from odontoflow.scheduling.domain.models import TimeSlot
from odontoflow.scheduling.domain.repositories import AppointmentRepository, ProviderScheduleRepository
from odontoflow.scheduling.domain.services import SchedulingService


@dataclass
class GetAvailableSlotsQuery:
    provider_id: UUID = field(default=None)
    target_date: date = field(default=None)
    duration: int = 30

    async def execute(
        self,
        appointment_repo: AppointmentRepository,
        schedule_repo: ProviderScheduleRepository,
    ) -> list[TimeSlot]:
        schedule = await schedule_repo.get_by_provider(self.provider_id)
        if not schedule:
            return []

        appointments = await appointment_repo.get_day_schedule(
            self.provider_id, self.target_date,
        )

        return SchedulingService.get_available_slots(
            schedule, appointments, self.target_date, self.duration,
        )
