"""API Router: Insurance (TISS/Convenios) endpoints."""
from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_current_user,
    get_insurance_provider_repo,
    get_tiss_request_repo,
)
from odontoflow.api.schemas.insurance import (
    AuthorizeTISSRequest,
    CreateInsuranceProviderRequest,
    DenyTISSRequest,
    InsuranceProviderResponse,
    InsuranceProvidersListResponse,
    RecordTISSPaymentRequest,
    SubmitTISSRequest,
    TISSItemResponse,
    TISSRequestResponse,
    TISSRequestSummaryResponse,
    TISSRequestsListResponse,
)
from odontoflow.insurance.application.commands.authorize_tiss import AuthorizeTISSCommand
from odontoflow.insurance.application.commands.bill_tiss import BillTISSCommand
from odontoflow.insurance.application.commands.deny_tiss import DenyTISSCommand
from odontoflow.insurance.application.commands.record_tiss_payment import RecordTISSPaymentCommand
from odontoflow.insurance.application.commands.submit_tiss import (
    SubmitTISSCommand,
    TISSItemInput,
)
from odontoflow.insurance.application.queries.list_insurance_providers import (
    ListInsuranceProvidersQuery,
)
from odontoflow.insurance.application.queries.list_tiss_requests import ListTISSRequestsQuery
from odontoflow.insurance.domain.models import InsuranceProvider, TISSStatus
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import NotFoundError, ValidationError

router = APIRouter(
    prefix="/api/v1",
    tags=["insurance"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _provider_to_response(provider: InsuranceProvider) -> InsuranceProviderResponse:
    return InsuranceProviderResponse(
        id=str(provider.id),
        name=provider.name,
        ans_code=provider.ans_code,
        active=provider.active,
    )


def _tiss_item_to_response(item) -> TISSItemResponse:
    return TISSItemResponse(
        tuss_code=item.tuss_code,
        description=item.description,
        tooth_number=item.tooth_number,
        quantity=item.quantity,
        authorized_quantity=item.authorized_quantity,
    )


def _tiss_to_response(req) -> TISSRequestResponse:
    return TISSRequestResponse(
        id=str(req.id),
        patient_id=str(req.patient_id),
        provider_id=str(req.provider_id),
        insurance_provider_id=str(req.insurance_provider_id),
        treatment_plan_id=str(req.treatment_plan_id) if req.treatment_plan_id else None,
        items=[_tiss_item_to_response(i) for i in req.items],
        status=req.status.value,
        authorization_number=req.authorization_number,
        submitted_at=req.submitted_at.isoformat() if req.submitted_at else None,
        authorized_at=req.authorized_at.isoformat() if req.authorized_at else None,
        denied_reason=req.denied_reason,
        billed_at=req.billed_at.isoformat() if req.billed_at else None,
        paid_at=req.paid_at.isoformat() if req.paid_at else None,
        paid_amount_centavos=req.paid_amount_centavos,
        glosa_amount_centavos=req.glosa_amount_centavos,
        glosa_reason=req.glosa_reason,
        created_at=req.created_at.isoformat(),
    )


def _tiss_to_summary(req) -> TISSRequestSummaryResponse:
    return TISSRequestSummaryResponse(
        id=str(req.id),
        patient_id=str(req.patient_id),
        insurance_provider_id=str(req.insurance_provider_id),
        status=req.status.value,
        items_count=len(req.items),
        paid_amount_centavos=req.paid_amount_centavos,
        glosa_amount_centavos=req.glosa_amount_centavos,
        created_at=req.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Insurance Providers
# ---------------------------------------------------------------------------


@router.post(
    "/insurance-providers",
    response_model=InsuranceProviderResponse,
    status_code=201,
)
async def create_insurance_provider(
    req: CreateInsuranceProviderRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_insurance_provider_repo),
):
    """Cadastra operadora de convenio."""
    provider = InsuranceProvider(
        tenant_id=current_user.tenant_id,
        name=req.name,
        ans_code=req.ans_code,
    )
    await repo.save(provider)
    return _provider_to_response(provider)


@router.get(
    "/insurance-providers",
    response_model=InsuranceProvidersListResponse,
)
async def list_insurance_providers(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_insurance_provider_repo),
):
    """Lista operadoras de convenio."""
    query = ListInsuranceProvidersQuery(tenant_id=current_user.tenant_id)
    providers = await query.execute(repo)
    return InsuranceProvidersListResponse(
        providers=[_provider_to_response(p) for p in providers],
        total=len(providers),
    )


# ---------------------------------------------------------------------------
# TISS Requests
# ---------------------------------------------------------------------------


@router.post(
    "/tiss-requests",
    response_model=TISSRequestResponse,
    status_code=201,
)
async def submit_tiss_request(
    req: SubmitTISSRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Submete guia TISS (GTO)."""
    cmd = SubmitTISSCommand(
        tenant_id=current_user.tenant_id,
        patient_id=UUID(req.patient_id),
        provider_id=UUID(req.provider_id),
        insurance_provider_id=UUID(req.insurance_provider_id),
        treatment_plan_id=UUID(req.treatment_plan_id) if req.treatment_plan_id else None,
        items=[
            TISSItemInput(
                tuss_code=item.tuss_code,
                description=item.description,
                tooth_number=item.tooth_number,
                quantity=item.quantity,
            )
            for item in req.items
        ],
    )
    try:
        tiss_request = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _tiss_to_response(tiss_request)


@router.get(
    "/tiss-requests",
    response_model=TISSRequestsListResponse,
)
async def list_tiss_requests(
    status: Optional[str] = Query(None),
    patient_id: Optional[UUID] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Lista guias TISS com filtros opcionais."""
    tiss_status = TISSStatus(status) if status else None
    query = ListTISSRequestsQuery(
        tenant_id=current_user.tenant_id,
        status=tiss_status,
        patient_id=patient_id,
    )
    requests = await query.execute(repo)
    return TISSRequestsListResponse(
        requests=[_tiss_to_summary(r) for r in requests],
        total=len(requests),
    )


@router.get(
    "/tiss-requests/{request_id}",
    response_model=TISSRequestResponse,
)
async def get_tiss_request(
    request_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Obtem guia TISS por ID."""
    tiss_request = await repo.get_by_id(request_id)
    if not tiss_request or tiss_request.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Guia TISS nao encontrada")
    return _tiss_to_response(tiss_request)


@router.patch(
    "/tiss-requests/{request_id}/authorize",
    response_model=TISSRequestResponse,
)
async def authorize_tiss_request(
    request_id: UUID,
    req: AuthorizeTISSRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Autoriza guia TISS."""
    cmd = AuthorizeTISSCommand(
        request_id=request_id,
        authorization_number=req.authorization_number,
    )
    try:
        tiss_request = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Guia TISS nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _tiss_to_response(tiss_request)


@router.patch(
    "/tiss-requests/{request_id}/deny",
    response_model=TISSRequestResponse,
)
async def deny_tiss_request(
    request_id: UUID,
    req: DenyTISSRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Nega guia TISS."""
    cmd = DenyTISSCommand(
        request_id=request_id,
        reason=req.reason,
    )
    try:
        tiss_request = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Guia TISS nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _tiss_to_response(tiss_request)


@router.patch(
    "/tiss-requests/{request_id}/bill",
    response_model=TISSRequestResponse,
)
async def bill_tiss_request(
    request_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Fatura guia TISS."""
    cmd = BillTISSCommand(request_id=request_id)
    try:
        tiss_request = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Guia TISS nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _tiss_to_response(tiss_request)


@router.patch(
    "/tiss-requests/{request_id}/payment",
    response_model=TISSRequestResponse,
)
async def record_tiss_payment(
    request_id: UUID,
    req: RecordTISSPaymentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_tiss_request_repo),
):
    """Registra pagamento de guia TISS."""
    cmd = RecordTISSPaymentCommand(
        request_id=request_id,
        paid_amount_centavos=req.paid_amount_centavos,
        glosa_amount_centavos=req.glosa_amount_centavos,
        glosa_reason=req.glosa_reason,
    )
    try:
        tiss_request = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Guia TISS nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _tiss_to_response(tiss_request)
