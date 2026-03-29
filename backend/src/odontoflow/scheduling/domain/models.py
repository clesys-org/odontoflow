"""Scheduling Bounded Context — Domain Models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot, Entity
from odontoflow.shared.domain.types import AppointmentStatus


class BookingSource(str, Enum):
    RECEPTIONIST = "RECEPTIONIST"
    ONLINE = "ONLINE"
    WHATSAPP = "WHATSAPP"


@dataclass(frozen=True)
class TimeSlot:
    start: datetime
    end: datetime

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)

    def overlaps(self, other: TimeSlot) -> bool:
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class AppointmentType:
    name: str = "consulta"
    default_duration: int = 30
    color: str = "#3b82f6"


@dataclass(frozen=True)
class PlannedProcedure:
    tuss_code: str = ""
    description: str = ""
    tooth_number: Optional[int] = None


@dataclass(frozen=True)
class WorkingHours:
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    slot_duration: int = 30


@dataclass(frozen=True)
class BreakPeriod:
    start_time: time
    end_time: time


@dataclass
class BlockedSlot(Entity):
    provider_id: UUID = field(default=None)
    start_at: datetime = field(default=None)
    end_at: datetime = field(default=None)
    reason: str = ""


@dataclass
class Appointment(AggregateRoot):
    tenant_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    time_slot: Optional[TimeSlot] = None
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    appointment_type: AppointmentType = field(default_factory=lambda: AppointmentType())
    procedures_planned: list[PlannedProcedure] = field(default_factory=list)
    notes: Optional[str] = None
    source: BookingSource = BookingSource.RECEPTIONIST
    cancellation_reason: Optional[str] = None
    patient_name: str = ""
    provider_name: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def confirm(self) -> None:
        if self.status != AppointmentStatus.SCHEDULED:
            raise ValueError("Apenas agendamentos podem ser confirmados")
        self.status = AppointmentStatus.CONFIRMED
        self.updated_at = datetime.now(timezone.utc)

    def start_service(self) -> None:
        if self.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED):
            raise ValueError("Consulta nao pode ser iniciada neste estado")
        self.status = AppointmentStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc)

    def complete(self) -> None:
        if self.status != AppointmentStatus.IN_PROGRESS:
            raise ValueError("Apenas consultas em andamento podem ser finalizadas")
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def cancel(self, reason: str = "") -> None:
        if self.status in (AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED):
            raise ValueError("Consulta ja finalizada ou cancelada")
        self.status = AppointmentStatus.CANCELLED
        self.cancellation_reason = reason
        self.updated_at = datetime.now(timezone.utc)

    def mark_no_show(self) -> None:
        if self.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED):
            raise ValueError("Apenas agendamentos podem ser marcados como falta")
        self.status = AppointmentStatus.NO_SHOW
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class ProviderSchedule(AggregateRoot):
    provider_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    provider_name: str = ""
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    color: str = "#3b82f6"
    working_hours: list[WorkingHours] = field(default_factory=list)
    breaks: list[BreakPeriod] = field(default_factory=list)
    blocked_slots: list[BlockedSlot] = field(default_factory=list)
    overbooking_limit: int = 0
