"""Infrastructure — Agregador de analytics que combina dados de multiplos repos."""
from __future__ import annotations

from datetime import date
from uuid import UUID

from odontoflow.analytics.application.queries.get_dashboard_kpis import GetDashboardKPIsQuery
from odontoflow.analytics.application.queries.get_period_report import GetPeriodReportQuery
from odontoflow.analytics.domain.models import ClinicReport


class AnalyticsAggregator:
    """Fachada que injeta todos os repos necessarios para analytics."""

    def __init__(
        self,
        patient_repo,
        appointment_repo,
        invoice_repo,
    ):
        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo
        self.invoice_repo = invoice_repo

    async def get_dashboard_kpis(self, tenant_id: UUID) -> list[dict]:
        query = GetDashboardKPIsQuery(tenant_id=tenant_id)
        return await query.execute(
            self.patient_repo,
            self.appointment_repo,
            self.invoice_repo,
        )

    async def get_period_report(
        self,
        tenant_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ClinicReport:
        query = GetPeriodReportQuery(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )
        return await query.execute(
            self.patient_repo,
            self.appointment_repo,
            self.invoice_repo,
        )
