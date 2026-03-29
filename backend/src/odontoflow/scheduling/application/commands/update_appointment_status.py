"""Use case — Atualizar status de agendamento."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from odontoflow.scheduling.domain.repositories import AppointmentRepository
from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.shared.domain.events import AppointmentCancelled, AppointmentCompleted, PatientNoShow
from odontoflow.shared.event_bus import EventBus


@dataclass
class UpdateAppointmentStatusCommand:
    appointment_id: UUID = field(default=None)
    action: str = ""  # confirm, start, complete, cancel, no_show
    reason: Optional[str] = None

    async def execute(
        self,
        repo: AppointmentRepository,
        event_bus: EventBus,
    ) -> None:
        appointment = await repo.get_by_id(self.appointment_id)
        if not appointment:
            raise NotFoundError("Agendamento", str(self.appointment_id))

        try:
            if self.action == "confirm":
                appointment.confirm()
            elif self.action == "start":
                appointment.start_service()
            elif self.action == "complete":
                appointment.complete()
                appointment.add_event(AppointmentCompleted(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    provider_id=appointment.provider_id,
                    tenant_id=appointment.tenant_id,
                ))
            elif self.action == "cancel":
                appointment.cancel(self.reason or "")
                appointment.add_event(AppointmentCancelled(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    reason=self.reason or "",
                    tenant_id=appointment.tenant_id,
                ))
            elif self.action == "no_show":
                appointment.mark_no_show()
                appointment.add_event(PatientNoShow(
                    appointment_id=appointment.id,
                    patient_id=appointment.patient_id,
                    tenant_id=appointment.tenant_id,
                ))
            else:
                raise ValidationError(f"Acao invalida: {self.action}")
        except ValueError as e:
            raise ValidationError(str(e))

        await repo.update(appointment)

        for event in appointment.collect_events():
            await event_bus.publish(event)
