"""API Router: Staff endpoints."""
from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_current_user,
    get_production_repo,
    get_staff_repo,
)
from odontoflow.api.schemas.staff import (
    CommissionRuleResponse,
    CreateStaffRequest,
    ProductionEntryResponse,
    ProductionReportResponse,
    RecordProductionRequest,
    StaffListResponse,
    StaffResponse,
    UpdateStaffRequest,
)
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import NotFoundError
from odontoflow.staff.application.commands.manage_staff import (
    CommissionRuleInput,
    CreateStaffCommand,
    UpdateStaffCommand,
)
from odontoflow.staff.application.commands.record_production import RecordProductionCommand
from odontoflow.staff.application.queries.list_staff import ListStaffQuery
from odontoflow.staff.application.queries.staff_production_report import StaffProductionReportQuery

router = APIRouter(
    prefix="/api/v1/staff",
    tags=["staff"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _staff_to_response(member) -> StaffResponse:
    return StaffResponse(
        id=str(member.id),
        tenant_id=str(member.tenant_id),
        user_id=str(member.user_id),
        full_name=member.full_name,
        cro_number=member.cro_number,
        specialty=member.specialty,
        commission_rules=[
            CommissionRuleResponse(
                procedure_category=r.procedure_category,
                commission_type=r.commission_type.value,
                value=r.value,
            )
            for r in member.commission_rules
        ],
        active=member.active,
        created_at=member.created_at.isoformat(),
    )


def _entry_to_response(entry) -> ProductionEntryResponse:
    return ProductionEntryResponse(
        id=str(entry.id),
        staff_id=str(entry.staff_id),
        procedure_description=entry.procedure_description,
        revenue_centavos=entry.revenue_centavos,
        commission_centavos=entry.commission_centavos,
        patient_name=entry.patient_name,
        date=entry.date.isoformat(),
        created_at=entry.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", response_model=StaffResponse, status_code=201)
async def create_staff(
    req: CreateStaffRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_staff_repo),
):
    """Cria novo profissional."""
    rules = [
        CommissionRuleInput(
            procedure_category=r.procedure_category,
            commission_type=r.commission_type,
            value=r.value,
        )
        for r in req.commission_rules
    ]

    cmd = CreateStaffCommand(
        tenant_id=current_user.tenant_id,
        user_id=current_user.user_id,
        full_name=req.full_name,
        cro_number=req.cro_number,
        specialty=req.specialty,
        commission_rules=rules,
    )
    member = await cmd.execute(repo)
    return _staff_to_response(member)


@router.get("", response_model=StaffListResponse)
async def list_staff(
    active_only: bool = Query(True),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_staff_repo),
):
    """Lista profissionais da clinica."""
    query = ListStaffQuery(tenant_id=current_user.tenant_id, active_only=active_only)
    members = await query.execute(repo)
    return StaffListResponse(
        staff=[_staff_to_response(m) for m in members],
        total=len(members),
    )


@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff(
    staff_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_staff_repo),
):
    """Obtem profissional por ID."""
    member = await repo.get_by_id(staff_id)
    if not member or member.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Profissional nao encontrado")
    return _staff_to_response(member)


@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: UUID,
    req: UpdateStaffRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_staff_repo),
):
    """Atualiza profissional."""
    rules = None
    if req.commission_rules is not None:
        rules = [
            CommissionRuleInput(
                procedure_category=r.procedure_category,
                commission_type=r.commission_type,
                value=r.value,
            )
            for r in req.commission_rules
        ]

    cmd = UpdateStaffCommand(
        staff_id=staff_id,
        full_name=req.full_name,
        cro_number=req.cro_number,
        specialty=req.specialty,
        active=req.active,
        commission_rules=rules,
    )
    try:
        member = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Profissional nao encontrado")

    return _staff_to_response(member)


@router.get("/{staff_id}/production", response_model=ProductionReportResponse)
async def staff_production_report(
    staff_id: UUID,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    staff_repo=Depends(get_staff_repo),
    production_repo=Depends(get_production_repo),
):
    """Relatorio de producao de um profissional."""
    member = await staff_repo.get_by_id(staff_id)
    if not member or member.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Profissional nao encontrado")

    sd = date.fromisoformat(start_date) if start_date else None
    ed = date.fromisoformat(end_date) if end_date else None

    query = StaffProductionReportQuery(staff_id=staff_id, start_date=sd, end_date=ed)
    report = await query.execute(production_repo)

    return ProductionReportResponse(
        staff_id=report["staff_id"],
        start_date=report["start_date"],
        end_date=report["end_date"],
        total_revenue_centavos=report["total_revenue_centavos"],
        total_commission_centavos=report["total_commission_centavos"],
        entries_count=report["entries_count"],
        entries=[_entry_to_response(e) for e in report["entries"]],
    )


@router.post("/{staff_id}/production", response_model=ProductionEntryResponse, status_code=201)
async def record_production(
    staff_id: UUID,
    req: RecordProductionRequest,
    current_user: CurrentUser = Depends(get_current_user),
    staff_repo=Depends(get_staff_repo),
    production_repo=Depends(get_production_repo),
):
    """Registra entrada de producao."""
    cmd = RecordProductionCommand(
        staff_id=staff_id,
        tenant_id=current_user.tenant_id,
        procedure_description=req.procedure_description,
        revenue_centavos=req.revenue_centavos,
        patient_name=req.patient_name,
        date=date.fromisoformat(req.date),
        treatment_item_id=UUID(req.treatment_item_id) if req.treatment_item_id else None,
        procedure_category=req.procedure_category,
    )
    try:
        entry = await cmd.execute(staff_repo, production_repo)
    except NotFoundError:
        raise HTTPException(404, "Profissional nao encontrado")

    return _entry_to_response(entry)
