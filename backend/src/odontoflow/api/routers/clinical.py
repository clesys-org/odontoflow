"""API Router: Clinical Records endpoints."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import get_clinical_repo, get_current_user, get_event_bus
from odontoflow.api.schemas.clinical import (
    AnamnesisResponse,
    ClinicalNoteResponse,
    ConsentFormResponse,
    CreateAnamnesisRequest,
    CreateClinicalNoteRequest,
    CreateConsentRequest,
    CreatePrescriptionRequest,
    NotesListResponse,
    OdontogramResponse,
    PatientRecordResponse,
    PrescriptionItemResponse,
    PrescriptionResponse,
    PrescriptionsListResponse,
    TimelineEntryResponse,
    TimelineResponse,
    ToothResponse,
    ToothSurfaceResponse,
    UpdateToothRequest,
)
from odontoflow.clinical.application.commands.create_anamnesis import (
    CreateAnamnesisCommand,
)
from odontoflow.clinical.application.commands.create_clinical_note import (
    CreateClinicalNoteCommand,
)
from odontoflow.clinical.application.commands.create_prescription import (
    CreatePrescriptionCommand,
)
from odontoflow.clinical.application.commands.update_odontogram import (
    UpdateOdontogramCommand,
)
from odontoflow.clinical.application.queries.get_patient_record import (
    GetPatientRecordQuery,
)
from odontoflow.clinical.application.queries.get_patient_timeline import (
    GetPatientTimelineQuery,
)
from odontoflow.clinical.domain.models import ConsentForm, PrescriptionItem, ToothSurface
from odontoflow.clinical.domain.services import OdontogramService
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.shared.domain.types import (
    NoteType,
    SurfaceCondition,
    SurfacePosition,
    ToothStatus,
)
from odontoflow.shared.event_bus import EventBus

router = APIRouter(
    prefix="/api/v1/patients/{patient_id}/record",
    tags=["clinical"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _anamnesis_to_response(a) -> AnamnesisResponse:
    return AnamnesisResponse(
        id=str(a.id),
        chief_complaint=a.chief_complaint,
        medical_history=a.medical_history,
        dental_history=a.dental_history,
        created_by=str(a.created_by) if a.created_by else None,
        created_at=a.created_at.isoformat(),
        signed_at=a.signed_at.isoformat() if a.signed_at else None,
    )


def _tooth_to_response(t) -> ToothResponse:
    return ToothResponse(
        id=str(t.id),
        tooth_number=t.tooth_number,
        status=t.status.value,
        surfaces=[
            ToothSurfaceResponse(position=s.position.value, condition=s.condition.value)
            for s in t.surfaces
        ],
        notes=t.notes,
        updated_by=str(t.updated_by) if t.updated_by else None,
        updated_at=t.updated_at.isoformat() if t.updated_at else None,
    )


def _note_to_response(n) -> ClinicalNoteResponse:
    return ClinicalNoteResponse(
        id=str(n.id),
        note_type=n.note_type.value,
        content=n.content,
        tooth_references=n.tooth_references,
        attachments=n.attachments,
        is_signed=n.is_signed,
        created_by=str(n.created_by) if n.created_by else None,
        created_at=n.created_at.isoformat(),
        signed_at=n.signed_at.isoformat() if n.signed_at else None,
    )


def _prescription_to_response(rx) -> PrescriptionResponse:
    return PrescriptionResponse(
        id=str(rx.id),
        items=[
            PrescriptionItemResponse(
                medication_name=i.medication_name,
                dosage=i.dosage,
                frequency=i.frequency,
                duration=i.duration,
                instructions=i.instructions,
            )
            for i in rx.items
        ],
        created_by=str(rx.created_by) if rx.created_by else None,
        created_at=rx.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=PatientRecordResponse)
async def get_patient_record(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Obtem prontuario clinico do paciente."""
    query = GetPatientRecordQuery(
        patient_id=patient_id,
        tenant_id=current_user.tenant_id,
    )
    record = await query.execute(repo)
    if not record:
        # Cria prontuario vazio sob demanda
        record = await repo.get_or_create_record(patient_id, current_user.tenant_id)

    return PatientRecordResponse(
        id=str(record.id),
        patient_id=str(record.patient_id),
        anamnesis=_anamnesis_to_response(record.anamnesis) if record.anamnesis else None,
        teeth_count=len(record.teeth),
        notes_count=len(record.notes),
        prescriptions_count=len(record.prescriptions),
        consent_forms_count=len(record.consent_forms),
        created_at=record.created_at.isoformat(),
    )


@router.post("/anamnesis", response_model=AnamnesisResponse, status_code=201)
async def create_anamnesis(
    patient_id: UUID,
    req: CreateAnamnesisRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Cria anamnese do paciente."""
    cmd = CreateAnamnesisCommand(
        patient_id=patient_id,
        tenant_id=current_user.tenant_id,
        chief_complaint=req.chief_complaint,
        medical_history=req.medical_history,
        dental_history=req.dental_history,
        created_by=current_user.user_id,
    )
    try:
        anamnesis = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _anamnesis_to_response(anamnesis)


@router.get("/anamnesis", response_model=AnamnesisResponse)
async def get_anamnesis(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Obtem anamnese do paciente."""
    record = await repo.get_record(patient_id)
    if not record or record.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Prontuario nao encontrado")
    if not record.anamnesis:
        raise HTTPException(404, "Anamnese nao encontrada")
    return _anamnesis_to_response(record.anamnesis)


@router.get("/odontogram", response_model=OdontogramResponse)
async def get_odontogram(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Obtem odontograma completo (32 dentes permanentes)."""
    record = await repo.get_or_create_record(patient_id, current_user.tenant_id)
    teeth = OdontogramService.get_full_odontogram(record)
    return OdontogramResponse(
        teeth=[_tooth_to_response(t) for t in teeth],
        total=len(teeth),
    )


@router.put("/odontogram/{tooth_number}", response_model=ToothResponse)
async def update_tooth(
    patient_id: UUID,
    tooth_number: int,
    req: UpdateToothRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Atualiza um dente no odontograma."""
    surfaces = [
        ToothSurface(
            position=SurfacePosition(s.position),
            condition=SurfaceCondition(s.condition),
        )
        for s in req.surfaces
    ]

    cmd = UpdateOdontogramCommand(
        patient_id=patient_id,
        tenant_id=current_user.tenant_id,
        tooth_number=tooth_number,
        status=ToothStatus(req.status),
        surfaces=surfaces,
        notes=req.notes,
        updated_by=current_user.user_id,
    )
    try:
        tooth = await cmd.execute(repo)
    except ValueError as e:
        raise HTTPException(422, str(e))

    return _tooth_to_response(tooth)


@router.get("/notes", response_model=NotesListResponse)
async def list_notes(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Lista notas clinicas do paciente."""
    record = await repo.get_record(patient_id)
    if not record or record.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Prontuario nao encontrado")

    sorted_notes = sorted(record.notes, key=lambda n: n.created_at, reverse=True)
    return NotesListResponse(
        notes=[_note_to_response(n) for n in sorted_notes],
        total=len(sorted_notes),
    )


@router.post("/notes", response_model=ClinicalNoteResponse, status_code=201)
async def create_note(
    patient_id: UUID,
    req: CreateClinicalNoteRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Cria nota clinica (evolucao, procedimento ou observacao)."""
    cmd = CreateClinicalNoteCommand(
        patient_id=patient_id,
        tenant_id=current_user.tenant_id,
        note_type=NoteType(req.note_type),
        content=req.content,
        tooth_references=req.tooth_references,
        attachments=req.attachments,
        created_by=current_user.user_id,
        sign_immediately=req.sign_immediately,
    )
    try:
        note = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    # Publish domain events (e.g. ClinicalNoteSigned)
    record = await repo.get_record(patient_id)
    if record:
        for evt in record.collect_events():
            await event_bus.publish(evt)

    return _note_to_response(note)


@router.get("/prescriptions", response_model=PrescriptionsListResponse)
async def list_prescriptions(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Lista prescricoes do paciente."""
    record = await repo.get_record(patient_id)
    if not record or record.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Prontuario nao encontrado")

    sorted_rx = sorted(record.prescriptions, key=lambda r: r.created_at, reverse=True)
    return PrescriptionsListResponse(
        prescriptions=[_prescription_to_response(rx) for rx in sorted_rx],
        total=len(sorted_rx),
    )


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=201)
async def create_prescription(
    patient_id: UUID,
    req: CreatePrescriptionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Cria prescricao medica."""
    items = [
        PrescriptionItem(
            medication_name=i.medication_name,
            dosage=i.dosage,
            frequency=i.frequency,
            duration=i.duration,
            instructions=i.instructions,
        )
        for i in req.items
    ]

    cmd = CreatePrescriptionCommand(
        patient_id=patient_id,
        tenant_id=current_user.tenant_id,
        items=items,
        created_by=current_user.user_id,
    )
    try:
        prescription = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _prescription_to_response(prescription)


@router.post("/consent", response_model=ConsentFormResponse, status_code=201)
async def create_consent(
    patient_id: UUID,
    req: CreateConsentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Registra termo de consentimento."""
    from datetime import datetime, timezone

    record = await repo.get_or_create_record(patient_id, current_user.tenant_id)

    consent = ConsentForm(
        patient_record_id=record.id,
        form_type=req.form_type,
        content=req.content,
        patient_signature=req.patient_signature,
        signed_at=datetime.now(timezone.utc) if req.patient_signature else None,
    )

    record.add_consent(consent)
    await repo.save_consent(consent)
    await repo.save_record(record)

    return ConsentFormResponse(
        id=str(consent.id),
        form_type=consent.form_type,
        content=consent.content,
        signed_at=consent.signed_at.isoformat() if consent.signed_at else None,
    )


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline(
    patient_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_clinical_repo),
):
    """Obtem timeline clinica do paciente (CQRS read model)."""
    # Verify tenant access
    record = await repo.get_record(patient_id)
    if record and record.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Prontuario nao encontrado")

    query = GetPatientTimelineQuery(
        patient_id=patient_id,
        page=page,
        page_size=page_size,
    )
    entries, total = await query.execute(repo)

    return TimelineResponse(
        entries=[TimelineEntryResponse(**e) for e in entries],
        total=total,
        page=page,
        page_size=page_size,
    )
