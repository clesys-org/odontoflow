"""API Router: Patient management endpoints."""

from __future__ import annotations

import math
from dataclasses import asdict
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import get_current_user, get_event_bus, get_patient_repo
from odontoflow.api.schemas.patient import (
    AddressFromCEPResponse,
    CreatePatientRequest,
    PatientListResponse,
    PatientResponse,
    UpdatePatientRequest,
)
from odontoflow.patient.application.commands.create_patient import CreatePatientCommand
from odontoflow.patient.application.commands.update_patient import UpdatePatientCommand
from odontoflow.patient.domain.models import Address, InsuranceInfo, Patient, Responsible
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.shared.domain.types import ContactChannel, Gender, MaritalStatus
from odontoflow.shared.event_bus import EventBus

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _format_cpf(cpf: str | None) -> str | None:
    if not cpf or len(cpf) != 11:
        return None
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def _format_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = phone
    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    if len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
    return phone


def _calc_age(birth_date) -> int | None:
    if not birth_date:
        return None
    from datetime import date

    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def _patient_to_response(patient: Patient) -> PatientResponse:
    address_dict = None
    if patient.address:
        address_dict = asdict(patient.address)

    responsible_dict = None
    if patient.responsible:
        responsible_dict = asdict(patient.responsible)

    insurance_dict = None
    if patient.insurance_info:
        d = asdict(patient.insurance_info)
        if d.get("valid_until"):
            d["valid_until"] = str(d["valid_until"])
        insurance_dict = d

    return PatientResponse(
        id=str(patient.id),
        full_name=patient.full_name,
        cpf=patient.cpf,
        cpf_formatted=_format_cpf(patient.cpf),
        birth_date=str(patient.birth_date) if patient.birth_date else None,
        age=_calc_age(patient.birth_date),
        gender=patient.gender.value,
        marital_status=patient.marital_status.value if patient.marital_status else None,
        profession=patient.profession,
        phone=patient.phone,
        phone_formatted=_format_phone(patient.phone),
        whatsapp=patient.whatsapp,
        email=patient.email,
        preferred_channel=patient.preferred_channel.value,
        address=address_dict,
        responsible=responsible_dict,
        insurance_info=insurance_dict,
        referral_source=patient.referral_source,
        tags=patient.tags,
        notes=patient.notes,
        status=patient.status.value,
        is_minor=patient.is_minor,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=PatientListResponse)
async def list_patients(
    q: str | None = Query(None, description="Busca por nome, CPF ou telefone"),
    status: str | None = Query(None, description="Filtro por status (ACTIVE, INACTIVE, ARCHIVED)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
):
    """Lista pacientes da clinica com paginacao e filtro."""
    patients, total = await repo.search(
        query=q or "",
        status=status,
        page=page,
        page_size=page_size,
    )
    total_pages = max(1, math.ceil(total / page_size))

    return PatientListResponse(
        patients=[_patient_to_response(p) for p in patients],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=PatientResponse, status_code=201)
async def create_patient(
    req: CreatePatientRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Cria novo paciente."""
    cmd = CreatePatientCommand(
        tenant_id=current_user.tenant_id,
        full_name=req.full_name,
        cpf=req.cpf,
        birth_date=req.birth_date,
        gender=Gender(req.gender),
        marital_status=MaritalStatus(req.marital_status) if req.marital_status else None,
        profession=req.profession,
        phone=req.phone,
        whatsapp=req.whatsapp,
        email=req.email,
        preferred_channel=ContactChannel(req.preferred_channel),
        address=Address(**req.address.model_dump()) if req.address else None,
        responsible=Responsible(**req.responsible.model_dump()) if req.responsible else None,
        insurance_info=InsuranceInfo(**req.insurance_info.model_dump()) if req.insurance_info else None,
        referral_source=req.referral_source,
        tags=req.tags,
        notes=req.notes,
    )
    try:
        patient = await cmd.execute(repo)
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    # Publish domain events
    for evt in patient.collect_events():
        await event_bus.publish(evt)

    return _patient_to_response(patient)


@router.get("/search", response_model=list[PatientResponse])
async def search_patients(
    q: str = Query(..., min_length=2, description="Busca rapida por nome, CPF ou telefone"),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
):
    """Busca rapida de pacientes (autocomplete)."""
    patients, _ = await repo.search(query=q, page=1, page_size=20)
    return [_patient_to_response(p) for p in patients]


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
):
    """Busca paciente por ID."""
    patient = await repo.get_by_id(patient_id)
    if not patient or patient.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Paciente nao encontrado")
    return _patient_to_response(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    req: UpdatePatientRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Atualiza dados do paciente."""
    # Verifica se paciente pertence ao tenant
    existing = await repo.get_by_id(patient_id)
    if not existing or existing.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Paciente nao encontrado")

    # Build updates dict from non-None request fields
    updates: dict = {}
    if req.full_name is not None:
        updates["full_name"] = req.full_name
    if req.cpf is not None:
        updates["cpf"] = req.cpf
    if req.birth_date is not None:
        updates["birth_date"] = req.birth_date
    if req.gender is not None:
        updates["gender"] = Gender(req.gender)
    if req.marital_status is not None:
        updates["marital_status"] = MaritalStatus(req.marital_status)
    if req.profession is not None:
        updates["profession"] = req.profession
    if req.phone is not None:
        updates["phone"] = req.phone
    if req.whatsapp is not None:
        updates["whatsapp"] = req.whatsapp
    if req.email is not None:
        updates["email"] = req.email
    if req.preferred_channel is not None:
        updates["preferred_channel"] = ContactChannel(req.preferred_channel)
    if req.address is not None:
        updates["address"] = Address(**req.address.model_dump())
    if req.responsible is not None:
        updates["responsible"] = Responsible(**req.responsible.model_dump())
    if req.insurance_info is not None:
        updates["insurance_info"] = InsuranceInfo(**req.insurance_info.model_dump())
    if req.referral_source is not None:
        updates["referral_source"] = req.referral_source
    if req.tags is not None:
        updates["tags"] = req.tags
    if req.notes is not None:
        updates["notes"] = req.notes
    if req.status is not None:
        from odontoflow.shared.domain.types import PatientStatus

        updates["status"] = PatientStatus(req.status)

    cmd = UpdatePatientCommand(
        tenant_id=current_user.tenant_id,
        patient_id=patient_id,
        updates=updates,
    )
    try:
        await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Paciente nao encontrado")
    except ConflictError as e:
        raise HTTPException(409, e.message)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    # Re-fetch to get updated state
    patient = await repo.get_by_id(patient_id)

    # Publish domain events
    for evt in patient.collect_events():
        await event_bus.publish(evt)

    return _patient_to_response(patient)


@router.delete("/{patient_id}", status_code=204)
async def archive_patient(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_patient_repo),
):
    """Arquiva (soft delete) um paciente."""
    patient = await repo.get_by_id(patient_id)
    if not patient or patient.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Paciente nao encontrado")

    patient.archive()
    await repo.update(patient)


# ---------------------------------------------------------------------------
# CEP Lookup (separate prefix)
# ---------------------------------------------------------------------------

cep_router = APIRouter(prefix="/api/v1/address", tags=["address"])


@cep_router.get("/cep/{cep}", response_model=AddressFromCEPResponse)
async def lookup_cep(
    cep: str,
    _current_user: CurrentUser = Depends(get_current_user),
):
    """Consulta endereco pelo CEP via ViaCEP."""
    digits = "".join(c for c in cep if c.isdigit())
    if len(digits) != 8:
        raise HTTPException(422, "CEP deve ter 8 digitos")

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"https://viacep.com.br/ws/{digits}/json/")
            resp.raise_for_status()
        except httpx.HTTPError:
            raise HTTPException(502, "Erro ao consultar ViaCEP")

    data = resp.json()
    if data.get("erro"):
        raise HTTPException(404, "CEP nao encontrado")

    return AddressFromCEPResponse(
        street=data.get("logradouro", ""),
        neighborhood=data.get("bairro", ""),
        city=data.get("localidade", ""),
        state=data.get("uf", ""),
        zip_code=digits,
    )
