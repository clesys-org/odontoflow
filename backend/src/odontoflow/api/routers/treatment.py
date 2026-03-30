"""API Router: Treatment Plan endpoints."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_current_user,
    get_event_bus,
    get_procedure_catalog_repo,
    get_treatment_plan_repo,
)
from odontoflow.api.schemas.treatment import (
    AddProcedureRequest,
    ApprovePlanRequest,
    CreateTreatmentPlanRequest,
    ExecuteItemRequest,
    ProcedureCatalogResponse,
    ProceduresListResponse,
    TreatmentItemResponse,
    TreatmentPlanResponse,
    TreatmentPlanSummaryResponse,
    TreatmentPlansListResponse,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import ConflictError, NotFoundError, ValidationError
from odontoflow.shared.event_bus import EventBus
from odontoflow.treatment.application.commands.approve_plan import ApprovePlanCommand
from odontoflow.treatment.application.commands.create_treatment_plan import (
    CreateTreatmentPlanCommand,
    TreatmentItemInput,
)
from odontoflow.treatment.application.commands.execute_item import ExecuteItemCommand
from odontoflow.treatment.application.commands.manage_catalog import AddProcedureCommand
from odontoflow.treatment.application.queries.get_plan import GetPlanQuery
from odontoflow.treatment.application.queries.list_plans import ListPlansQuery
from odontoflow.treatment.application.queries.list_procedures import ListProceduresQuery

router = APIRouter(
    prefix="/api/v1/treatment",
    tags=["treatment"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _item_to_response(item) -> TreatmentItemResponse:
    return TreatmentItemResponse(
        id=str(item.id),
        phase_number=item.phase_number,
        phase_name=item.phase_name,
        procedure_id=str(item.procedure_id) if item.procedure_id else None,
        tuss_code=item.tuss_code,
        description=item.description,
        tooth_number=item.tooth_number,
        surface=item.surface,
        quantity=item.quantity,
        unit_price_centavos=item.unit_price_centavos,
        status=item.status.value,
        executed_at=item.executed_at.isoformat() if item.executed_at else None,
        executed_by=item.executed_by,
        sort_order=item.sort_order,
    )


def _plan_to_response(plan) -> TreatmentPlanResponse:
    return TreatmentPlanResponse(
        id=str(plan.id),
        patient_id=str(plan.patient_id),
        provider_id=str(plan.provider_id),
        title=plan.title,
        status=plan.status.value,
        items=[_item_to_response(i) for i in plan.items],
        total_value_centavos=plan.total_value_centavos,
        discount_centavos=plan.discount_centavos,
        approved_at=plan.approved_at.isoformat() if plan.approved_at else None,
        approved_by=plan.approved_by,
        created_at=plan.created_at.isoformat(),
    )


def _plan_to_summary(plan) -> TreatmentPlanSummaryResponse:
    return TreatmentPlanSummaryResponse(
        id=str(plan.id),
        patient_id=str(plan.patient_id),
        title=plan.title,
        status=plan.status.value,
        items_count=len(plan.items),
        total_value_centavos=plan.total_value_centavos,
        created_at=plan.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Treatment Plan Endpoints
# ---------------------------------------------------------------------------


@router.post("/plans", response_model=TreatmentPlanResponse, status_code=201)
async def create_plan(
    req: CreateTreatmentPlanRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_treatment_plan_repo),
):
    """Cria plano de tratamento."""
    items = [
        TreatmentItemInput(
            phase_number=i.phase_number,
            phase_name=i.phase_name,
            procedure_id=UUID(i.procedure_id) if i.procedure_id else None,
            tuss_code=i.tuss_code,
            description=i.description,
            tooth_number=i.tooth_number,
            surface=i.surface,
            quantity=i.quantity,
            unit_price_centavos=i.unit_price_centavos,
            sort_order=i.sort_order,
        )
        for i in req.items
    ]

    cmd = CreateTreatmentPlanCommand(
        patient_id=current_user.user_id,  # sera substituido pelo patient_id real
        provider_id=current_user.user_id,
        tenant_id=current_user.tenant_id,
        title=req.title,
        items=items,
        discount_centavos=req.discount_centavos,
    )
    try:
        plan = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _plan_to_response(plan)


@router.get("/plans/{plan_id}", response_model=TreatmentPlanResponse)
async def get_plan(
    plan_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_treatment_plan_repo),
):
    """Obtem plano de tratamento por ID."""
    query = GetPlanQuery(plan_id=plan_id)
    plan = await query.execute(repo)
    if not plan or plan.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Plano de tratamento nao encontrado")
    return _plan_to_response(plan)


@router.get("/patients/{patient_id}/plans", response_model=TreatmentPlansListResponse)
async def list_patient_plans(
    patient_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_treatment_plan_repo),
):
    """Lista planos de tratamento de um paciente."""
    query = ListPlansQuery(patient_id=patient_id)
    plans = await query.execute(repo)
    plans = [p for p in plans if p.tenant_id == current_user.tenant_id]
    return TreatmentPlansListResponse(
        plans=[_plan_to_summary(p) for p in plans],
        total=len(plans),
    )


@router.post("/plans/{plan_id}/approve", response_model=TreatmentPlanResponse)
async def approve_plan(
    plan_id: UUID,
    req: ApprovePlanRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_treatment_plan_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Aprova plano de tratamento."""
    cmd = ApprovePlanCommand(plan_id=plan_id, approved_by=req.approved_by)
    try:
        plan = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Plano de tratamento nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    for evt in plan.collect_events():
        await event_bus.publish(evt)

    return _plan_to_response(plan)


@router.post("/plans/{plan_id}/items/{item_id}/execute", response_model=TreatmentPlanResponse)
async def execute_item(
    plan_id: UUID,
    item_id: UUID,
    req: ExecuteItemRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_treatment_plan_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Executa item do plano de tratamento."""
    cmd = ExecuteItemCommand(
        plan_id=plan_id,
        item_id=item_id,
        executed_by=req.executed_by,
    )
    try:
        plan = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Plano de tratamento nao encontrado")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    for evt in plan.collect_events():
        await event_bus.publish(evt)

    return _plan_to_response(plan)


# ---------------------------------------------------------------------------
# Procedure Catalog Endpoints
# ---------------------------------------------------------------------------


@router.post("/procedures", response_model=ProcedureCatalogResponse, status_code=201)
async def add_procedure(
    req: AddProcedureRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_procedure_catalog_repo),
):
    """Adiciona procedimento ao catalogo."""
    cmd = AddProcedureCommand(
        tuss_code=req.tuss_code,
        description=req.description,
        category=req.category,
        default_price_centavos=req.default_price_centavos,
    )
    try:
        procedure = await cmd.execute(repo)
    except (ValidationError, ConflictError) as e:
        raise HTTPException(422, e.message)

    return ProcedureCatalogResponse(
        id=str(procedure.id),
        tuss_code=procedure.tuss_code,
        description=procedure.description,
        category=procedure.category,
        default_price_centavos=procedure.default_price_centavos,
        active=procedure.active,
    )


@router.get("/procedures", response_model=ProceduresListResponse)
async def list_procedures(
    category: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_procedure_catalog_repo),
):
    """Lista procedimentos do catalogo."""
    query = ListProceduresQuery(category=category)
    procedures = await query.execute(repo)
    return ProceduresListResponse(
        procedures=[
            ProcedureCatalogResponse(
                id=str(p.id),
                tuss_code=p.tuss_code,
                description=p.description,
                category=p.category,
                default_price_centavos=p.default_price_centavos,
                active=p.active,
            )
            for p in procedures
        ],
        total=len(procedures),
    )
