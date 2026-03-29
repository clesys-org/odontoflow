"""Use case — Agendar consulta."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from odontoflow.scheduling.domain.models import (
    Appointment,
    AppointmentType,
    BookingSource,
    PlannedProcedure,
    TimeSlot,
)
from odontoflow.scheduling.domain.repositories import AppointmentRepository, ProviderScheduleRepository
from odontoflow.scheduling.domain.services import SchedulingService
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.shared.domain.events import AppointmentBooked
from odontoflow.shared.event_bus import EventBus


@dataclass
class BookAppointmentCommand:
    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    start_at: datetime = field(default=None)
    duration_minutes: int = 30
    appointment_type_name: str = "consulta"
    appointment_type_color: str = "#3b82f6"
    notes: Optional[str] = None
    source: BookingSource = BookingSource.RECEPTIONIST
    procedures: list[dict] = field(default_factory=list)
    patient_name: str = ""
    provider_name: str = ""

    async def execute(
        self,
        appointment_repo: AppointmentRepository,
        schedule_repo: ProviderScheduleRepository,
        event_bus: EventBus,
    ) -> Appointment:
        if not self.patient_id or not self.provider_id or not self.start_at:
            raise ValidationError("patient_id, provider_id e start_at sao obrigatorios")

        if self.duration_minutes < 10 or self.duration_minutes > 240:
            raise ValidationError("Duracao deve ser entre 10 e 240 minutos")

        # Build time slot
        end_at = self.start_at + timedelta(minutes=self.duration_minutes)
        new_slot = TimeSlot(start=self.start_at, end=end_at)

        # Get provider schedule for conflict check
        schedule = await schedule_repo.get_by_provider(self.provider_id)

        # Get existing appointments for conflict check
        day_start = self.start_at.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        existing = await appointment_repo.get_by_date_range(
            self.provider_id, day_start, day_end,
        )

        overbooking = schedule.overbooking_limit if schedule else 0
        if SchedulingService.check_conflict(existing, new_slot, overbooking):
            raise ConflictError("Horario ja ocupado. Escolha outro horario.")

        # Create appointment
        appointment = Appointment(
            tenant_id=self.tenant_id,
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            time_slot=new_slot,
            appointment_type=AppointmentType(
                name=self.appointment_type_name,
                default_duration=self.duration_minutes,
                color=self.appointment_type_color,
            ),
            procedures_planned=[PlannedProcedure(**p) for p in self.procedures],
            notes=self.notes,
            source=self.source,
            patient_name=self.patient_name,
            provider_name=self.provider_name,
        )

        appointment.add_event(AppointmentBooked(
            appointment_id=appointment.id,
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            start_time=self.start_at,
            tenant_id=self.tenant_id,
        ))

        await appointment_repo.save(appointment)

        # Publish events
        for event in appointment.collect_events():
            await event_bus.publish(event)

        return appointment
