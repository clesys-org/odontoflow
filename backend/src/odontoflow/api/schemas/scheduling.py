"""Pydantic v2 schemas for Scheduling endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BookAppointmentRequest(BaseModel):
    patient_id: str
    provider_id: str
    start_at: str = Field(description="ISO 8601 datetime")
    duration_minutes: int = 30
    appointment_type: str = "consulta"
    type_color: str = "#3b82f6"
    notes: Optional[str] = None
    procedures: list[dict] = []


class UpdateStatusRequest(BaseModel):
    action: str = Field(description="confirm, start, complete, cancel, no_show")
    reason: Optional[str] = None


class AvailableSlotResponse(BaseModel):
    start: str
    end: str
    duration_minutes: int


class AppointmentResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str
    provider_id: str
    provider_name: str
    start_at: str
    end_at: str
    duration_minutes: int
    status: str
    appointment_type: str
    type_color: str
    notes: Optional[str] = None
    source: str
    cancellation_reason: Optional[str] = None
    created_at: str


class DayScheduleResponse(BaseModel):
    date: str
    provider_id: str
    provider_name: str
    appointments: list[AppointmentResponse]
    available_slots: list[AvailableSlotResponse]


class ProviderScheduleRequest(BaseModel):
    working_hours: list[dict]
    breaks: list[dict] = []
    overbooking_limit: int = 0


class ProviderResponse(BaseModel):
    id: str
    name: str
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    color: str
    active: bool = True
