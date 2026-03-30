"""API Router: Analytics endpoints."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from odontoflow.api.deps import (
    get_analytics_aggregator,
    get_current_user,
)
from odontoflow.api.schemas.analytics import (
    ClinicReportResponse,
    DashboardKPIsResponse,
    KPIResponse,
)
from odontoflow.shared.auth import CurrentUser

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


@router.get("/dashboard", response_model=DashboardKPIsResponse)
async def dashboard_kpis(
    current_user: CurrentUser = Depends(get_current_user),
    aggregator=Depends(get_analytics_aggregator),
):
    """Retorna KPIs do dashboard (hoje)."""
    kpis = await aggregator.get_dashboard_kpis(current_user.tenant_id)
    return DashboardKPIsResponse(
        kpis=[KPIResponse(**kpi) for kpi in kpis]
    )


@router.get("/report", response_model=ClinicReportResponse)
async def period_report(
    start: str = Query(..., description="Data inicio (YYYY-MM-DD)"),
    end: str = Query(..., description="Data fim (YYYY-MM-DD)"),
    current_user: CurrentUser = Depends(get_current_user),
    aggregator=Depends(get_analytics_aggregator),
):
    """Relatorio detalhado por periodo."""
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
    except ValueError:
        raise HTTPException(422, "Datas invalidas. Use formato YYYY-MM-DD")

    if start_date > end_date:
        raise HTTPException(422, "Data inicio deve ser anterior a data fim")

    report = await aggregator.get_period_report(
        current_user.tenant_id, start_date, end_date
    )

    return ClinicReportResponse(
        tenant_id=str(report.tenant_id),
        period_start=report.period_start.isoformat(),
        period_end=report.period_end.isoformat(),
        kpis=[
            KPIResponse(
                kpi_type=k.kpi_type.value,
                value=k.value,
                label=k.label,
                formatted_value=k.formatted_value,
                trend=k.trend,
            )
            for k in report.kpis
        ],
        generated_at=report.generated_at.isoformat(),
    )
