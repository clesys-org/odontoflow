"""Patient Management — Domain Models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot
from odontoflow.shared.domain.events import PatientCreated, PatientUpdated
from odontoflow.shared.domain.types import ContactChannel, Gender, MaritalStatus, PatientStatus


@dataclass(frozen=True)
class Address:
    street: str = ""
    number: str = ""
    complement: str = ""
    neighborhood: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""  # CEP digits only


@dataclass(frozen=True)
class Responsible:
    """Responsavel legal (para menores de idade)."""
    name: str = ""
    cpf: str = ""
    relationship: str = ""
    phone: str = ""


@dataclass(frozen=True)
class InsuranceInfo:
    provider_name: str = ""
    plan_name: str = ""
    card_number: str = ""
    valid_until: Optional[date] = None


@dataclass(frozen=True)
class LGPDConsent:
    consented_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    consent_type: str = "registration"
    ip_address: str = ""


@dataclass
class Patient(AggregateRoot):
    """Aggregate Root — paciente da clinica."""
    tenant_id: UUID = field(default=None)
    full_name: str = ""
    cpf: Optional[str] = None  # digits only (11 chars)
    birth_date: Optional[date] = None
    gender: Gender = Gender.NOT_INFORMED
    marital_status: Optional[MaritalStatus] = None
    profession: Optional[str] = None

    # Contact
    phone: Optional[str] = None  # digits only
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    preferred_channel: ContactChannel = ContactChannel.WHATSAPP

    # Address
    address: Optional[Address] = None

    # Responsible (for minors)
    responsible: Optional[Responsible] = None

    # Insurance
    insurance_info: Optional[InsuranceInfo] = None

    # Metadata
    referral_source: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    notes: Optional[str] = None

    # LGPD
    lgpd_consent: Optional[LGPDConsent] = None

    # Status
    status: PatientStatus = PatientStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_minor(self) -> bool:
        if not self.birth_date:
            return False
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age < 18

    def update_info(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                object.__setattr__(self, key, value)
        self.updated_at = datetime.now(timezone.utc)
        self.add_event(PatientUpdated(patient_id=self.id, tenant_id=self.tenant_id))

    def archive(self) -> None:
        self.status = PatientStatus.ARCHIVED
        self.updated_at = datetime.now(timezone.utc)

    def reactivate(self) -> None:
        self.status = PatientStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
