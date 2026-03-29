"""Use case — Criar paciente."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional
from uuid import UUID

from odontoflow.patient.domain.models import (
    Address,
    InsuranceInfo,
    LGPDConsent,
    Patient,
    Responsible,
)
from odontoflow.patient.domain.repositories import PatientRepository
from odontoflow.shared.domain.errors import ConflictError, ValidationError
from odontoflow.shared.domain.events import PatientCreated
from odontoflow.shared.domain.types import ContactChannel, Gender, MaritalStatus, PatientStatus


@dataclass
class CreatePatientCommand:
    """Input data para criacao de paciente."""

    tenant_id: UUID = field(default=None)
    full_name: str = ""
    cpf: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Gender = Gender.NOT_INFORMED
    marital_status: Optional[MaritalStatus] = None
    profession: Optional[str] = None

    # Contact
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    preferred_channel: ContactChannel = ContactChannel.WHATSAPP

    # Address
    address: Optional[Address] = None

    # Responsible
    responsible: Optional[Responsible] = None

    # Insurance
    insurance_info: Optional[InsuranceInfo] = None

    # Metadata
    referral_source: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    notes: Optional[str] = None

    # LGPD
    ip_address: str = ""

    async def execute(self, repo: PatientRepository) -> Patient:
        # --- Validacoes ---
        if not self.full_name or not self.full_name.strip():
            raise ValidationError("Nome completo e obrigatorio.")

        # CPF unico (se informado)
        if self.cpf:
            existing = await repo.get_by_cpf(self.cpf)
            if existing is not None:
                raise ConflictError(f"Ja existe paciente com CPF {self.cpf}.")

        # Menor de idade precisa de responsavel
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
                age -= 1
            if age < 18 and not self.responsible:
                raise ValidationError(
                    "Paciente menor de idade precisa de um responsavel legal."
                )

        # --- Criacao ---
        now = datetime.now(timezone.utc)

        lgpd_consent = LGPDConsent(
            consented_at=now,
            consent_type="registration",
            ip_address=self.ip_address,
        )

        patient = Patient(
            tenant_id=self.tenant_id,
            full_name=self.full_name.strip(),
            cpf=self.cpf,
            birth_date=self.birth_date,
            gender=self.gender,
            marital_status=self.marital_status,
            profession=self.profession,
            phone=self.phone,
            whatsapp=self.whatsapp,
            email=self.email,
            preferred_channel=self.preferred_channel,
            address=self.address,
            responsible=self.responsible,
            insurance_info=self.insurance_info,
            referral_source=self.referral_source,
            tags=list(self.tags),
            notes=self.notes,
            lgpd_consent=lgpd_consent,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )

        patient.add_event(
            PatientCreated(
                patient_id=patient.id,
                tenant_id=patient.tenant_id,
                full_name=patient.full_name,
            )
        )

        await repo.save(patient)
        return patient
