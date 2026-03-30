"""Query — Relatorio por periodo."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from odontoflow.analytics.domain.models import ClinicReport, KPIType, KPIValue


@dataclass
class GetPeriodReportQuery:
    """Gera relatorio detalhado para um intervalo de datas."""

    tenant_id: UUID
    start_date: date
    end_date: date

    async def execute(
        self,
        patient_repo,
        appointment_repo,
        invoice_repo,
    ) -> ClinicReport:
        from odontoflow.shared.domain.types import AppointmentStatus

        # Pacientes no periodo
        all_patients = await patient_repo.get_all()
        tenant_patients = [
            p for p in all_patients
            if getattr(p, "tenant_id", None) == self.tenant_id
        ]

        new_in_period = [
            p for p in tenant_patients
            if hasattr(p, "created_at")
            and self.start_date <= p.created_at.date() <= self.end_date
        ]

        # Consultas no periodo
        all_appts = await appointment_repo.get_all()
        period_appts = [
            a for a in all_appts
            if getattr(a, "tenant_id", None) == self.tenant_id
            and a.time_slot
            and self.start_date <= a.time_slot.start.date() <= self.end_date
        ]

        completed = len([a for a in period_appts if a.status == AppointmentStatus.COMPLETED])
        cancelled = len([a for a in period_appts if a.status == AppointmentStatus.CANCELLED])
        no_show = len([a for a in period_appts if a.status == AppointmentStatus.NO_SHOW])
        total_resolved = completed + cancelled + no_show

        attendance_rate = (completed / total_resolved * 100) if total_resolved > 0 else 0.0
        cancellation_rate = (cancelled / len(period_appts) * 100) if period_appts else 0.0

        # Financeiro
        dashboard_data = await invoice_repo.get_dashboard_data()
        revenue = dashboard_data.get("receita_centavos", 0)
        total_invoices = dashboard_data.get("total_faturas", 0)
        avg_ticket = revenue // total_invoices if total_invoices > 0 else 0

        def _fmt_currency(c: int) -> str:
            return f"R$ {c / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        def _fmt_pct(v: float) -> str:
            return f"{v:.1f}%"

        kpis = [
            KPIValue(KPIType.PATIENTS_ACTIVE, len(tenant_patients), "Pacientes Ativos", str(len(tenant_patients))),
            KPIValue(KPIType.NEW_PATIENTS_MONTH, len(new_in_period), "Novos Pacientes", str(len(new_in_period))),
            KPIValue(KPIType.REVENUE_MONTH, revenue, "Faturamento", _fmt_currency(revenue)),
            KPIValue(KPIType.AVG_TICKET, avg_ticket, "Ticket Medio", _fmt_currency(avg_ticket)),
            KPIValue(KPIType.ATTENDANCE_RATE, attendance_rate, "Taxa de Comparecimento", _fmt_pct(attendance_rate)),
            KPIValue(KPIType.CANCELLATION_RATE, cancellation_rate, "Taxa de Cancelamento", _fmt_pct(cancellation_rate)),
            KPIValue(KPIType.APPOINTMENTS_TODAY, len(period_appts), "Total Consultas", str(len(period_appts))),
        ]

        return ClinicReport(
            tenant_id=self.tenant_id,
            period_start=self.start_date,
            period_end=self.end_date,
            kpis=kpis,
        )
