"""Integration events between bounded contexts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from odontoflow.shared.domain.entity import DomainEvent


@dataclass
class PatientCreated(DomainEvent):
    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)
    full_name: str = ""


@dataclass
class PatientUpdated(DomainEvent):
    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)


@dataclass
class AppointmentBooked(DomainEvent):
    appointment_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    start_time: datetime = field(default=None)
    tenant_id: UUID = field(default=None)


@dataclass
class AppointmentCancelled(DomainEvent):
    appointment_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    reason: str = ""
    tenant_id: UUID = field(default=None)


@dataclass
class AppointmentCompleted(DomainEvent):
    appointment_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)


@dataclass
class PatientNoShow(DomainEvent):
    appointment_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)


@dataclass
class TreatmentPlanApproved(DomainEvent):
    plan_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    total_value_centavos: int = 0
    tenant_id: UUID = field(default=None)


@dataclass
class TreatmentItemCompleted(DomainEvent):
    plan_id: UUID = field(default=None)
    item_id: UUID = field(default=None)
    procedure_code: str = ""
    tenant_id: UUID = field(default=None)


@dataclass
class ClinicalNoteSigned(DomainEvent):
    patient_record_id: UUID = field(default=None)
    note_id: UUID = field(default=None)
    provider_id: UUID = field(default=None)
    tenant_id: UUID = field(default=None)


@dataclass
class InvoicePaid(DomainEvent):
    invoice_id: UUID = field(default=None)
    patient_id: UUID = field(default=None)
    amount_centavos: int = 0
    tenant_id: UUID = field(default=None)
