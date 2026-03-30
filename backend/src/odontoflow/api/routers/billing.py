"""API Router: Billing & Finance endpoints."""
from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import get_current_user, get_event_bus, get_invoice_repo
from odontoflow.api.schemas.billing import (
    CreateInvoiceRequest,
    FinanceDashboardResponse,
    InstallmentResponse,
    InvoiceResponse,
    InvoiceSummaryResponse,
    InvoicesListResponse,
    PayInstallmentRequest,
)
from odontoflow.billing.application.commands.cancel_invoice import CancelInvoiceCommand
from odontoflow.billing.application.commands.create_invoice import (
    CreateInvoiceCommand,
    InstallmentInput,
)
from odontoflow.billing.application.commands.pay_installment import PayInstallmentCommand
from odontoflow.billing.application.queries.finance_dashboard import FinanceDashboardQuery
from odontoflow.billing.application.queries.get_invoice import GetInvoiceQuery
from odontoflow.billing.application.queries.list_invoices import ListInvoicesQuery
from odontoflow.shared.auth import CurrentUser
from odontoflow.shared.domain.errors import NotFoundError, ValidationError
from odontoflow.shared.domain.types import InvoiceStatus, PaymentMethod
from odontoflow.shared.event_bus import EventBus

router = APIRouter(
    prefix="/api/v1/billing",
    tags=["billing"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _installment_to_response(inst) -> InstallmentResponse:
    return InstallmentResponse(
        id=str(inst.id),
        number=inst.number,
        due_date=inst.due_date.isoformat() if inst.due_date else None,
        amount_centavos=inst.amount_centavos,
        payment_method=inst.payment_method.value if inst.payment_method else None,
        status=inst.status.value,
        paid_at=inst.paid_at.isoformat() if inst.paid_at else None,
    )


def _invoice_to_response(inv) -> InvoiceResponse:
    return InvoiceResponse(
        id=str(inv.id),
        patient_id=str(inv.patient_id),
        treatment_plan_id=str(inv.treatment_plan_id) if inv.treatment_plan_id else None,
        description=inv.description,
        total_centavos=inv.total_centavos,
        status=inv.status.value,
        installments=[_installment_to_response(i) for i in inv.installments],
        amount_paid_centavos=inv.amount_paid_centavos,
        amount_remaining_centavos=inv.amount_remaining_centavos,
        created_at=inv.created_at.isoformat(),
    )


def _invoice_to_summary(inv) -> InvoiceSummaryResponse:
    return InvoiceSummaryResponse(
        id=str(inv.id),
        patient_id=str(inv.patient_id),
        description=inv.description,
        total_centavos=inv.total_centavos,
        status=inv.status.value,
        amount_paid_centavos=inv.amount_paid_centavos,
        installments_count=len(inv.installments),
        created_at=inv.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/invoices", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    req: CreateInvoiceRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
):
    """Cria fatura (a partir de plano de tratamento ou manual)."""
    installments = [
        InstallmentInput(
            number=i.number,
            due_date=date.fromisoformat(i.due_date),
            amount_centavos=i.amount_centavos,
        )
        for i in req.installments
    ]

    cmd = CreateInvoiceCommand(
        patient_id=current_user.user_id,  # sera substituido pelo patient_id real
        tenant_id=current_user.tenant_id,
        treatment_plan_id=UUID(req.treatment_plan_id) if req.treatment_plan_id else None,
        description=req.description,
        total_centavos=req.total_centavos,
        installments=installments,
    )
    try:
        invoice = await cmd.execute(repo)
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _invoice_to_response(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
):
    """Obtem fatura por ID."""
    query = GetInvoiceQuery(invoice_id=invoice_id)
    invoice = await query.execute(repo)
    if not invoice or invoice.tenant_id != current_user.tenant_id:
        raise HTTPException(404, "Fatura nao encontrada")
    return _invoice_to_response(invoice)


@router.get("/invoices", response_model=InvoicesListResponse)
async def list_invoices(
    patient_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
):
    """Lista faturas com filtros opcionais."""
    invoice_status = InvoiceStatus(status) if status else None
    query = ListInvoicesQuery(
        patient_id=patient_id,
        status=invoice_status,
    )
    invoices = await query.execute(repo)
    invoices = [inv for inv in invoices if inv.tenant_id == current_user.tenant_id]
    return InvoicesListResponse(
        invoices=[_invoice_to_summary(inv) for inv in invoices],
        total=len(invoices),
    )


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceResponse)
async def pay_installment(
    invoice_id: UUID,
    req: PayInstallmentRequest,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
    event_bus: EventBus = Depends(get_event_bus),
):
    """Registra pagamento de parcela."""
    cmd = PayInstallmentCommand(
        invoice_id=invoice_id,
        installment_number=req.installment_number,
        payment_method=PaymentMethod(req.payment_method),
    )
    try:
        invoice = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Fatura nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    for evt in invoice.collect_events():
        await event_bus.publish(evt)

    return _invoice_to_response(invoice)


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    invoice_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
):
    """Cancela fatura."""
    cmd = CancelInvoiceCommand(invoice_id=invoice_id)
    try:
        invoice = await cmd.execute(repo)
    except NotFoundError:
        raise HTTPException(404, "Fatura nao encontrada")
    except ValidationError as e:
        raise HTTPException(422, e.message)

    return _invoice_to_response(invoice)


@router.get("/dashboard", response_model=FinanceDashboardResponse)
async def finance_dashboard(
    current_user: CurrentUser = Depends(get_current_user),
    repo=Depends(get_invoice_repo),
):
    """Retorna totais financeiros (receita, a receber)."""
    query = FinanceDashboardQuery()
    data = await query.execute(repo)
    return FinanceDashboardResponse(**data)
