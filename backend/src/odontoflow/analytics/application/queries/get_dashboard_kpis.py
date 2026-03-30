"""Query — Dashboard KPIs (agregados de todos os repositorios)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from uuid import UUID

from odontoflow.analytics.domain.models import KPIType, KPIValue


def _format_currency(centavos: int) -> str:
    return f"R$ {centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _format_percentage(value: float) -> str:
    return f"{value:.1f}%"


@dataclass
class GetDashboardKPIsQuery:
    """Agrega KPIs de multiplos repositorios."""

    tenant_id: UUID

    async def execute(
        self,
        patient_repo,
        appointment_repo,
        invoice_repo,
    ) -> list[dict]:
        """Calcula KPIs do dashboard a partir dos repos disponíveis."""
        today = date.today()

        # Pacientes ativos
        all_patients = await patient_repo.get_all()
        active_patients = [
            p for p in all_patients
            if getattr(p, "tenant_id", None) == self.tenant_id
        ]
        active_count = len(active_patients)

        # Pacientes novos no mes
        month_start = today.replace(day=1)
        new_patients = [
            p for p in active_patients
            if hasattr(p, "created_at") and p.created_at.date() >= month_start
        ]
        new_patients_count = len(new_patients)

        # Consultas hoje
        all_appointments = await appointment_repo.get_all()
        tenant_appts = [
            a for a in all_appointments
            if getattr(a, "tenant_id", None) == self.tenant_id
        ]
        today_appts = [
            a for a in tenant_appts
            if a.time_slot and a.time_slot.start.date() == today
        ]
        appts_today = len(today_appts)

        # Taxa de comparecimento (ultimos 30 dias)
        from datetime import timedelta
        thirty_days_ago = today - timedelta(days=30)
        recent_appts = [
            a for a in tenant_appts
            if a.time_slot and a.time_slot.start.date() >= thirty_days_ago
        ]
        from odontoflow.shared.domain.types import AppointmentStatus
        completed = len([a for a in recent_appts if a.status == AppointmentStatus.COMPLETED])
        total_past = len([
            a for a in recent_appts
            if a.status in (
                AppointmentStatus.COMPLETED,
                AppointmentStatus.NO_SHOW,
                AppointmentStatus.CANCELLED,
            )
        ])
        attendance_rate = (completed / total_past * 100) if total_past > 0 else 0.0

        # Taxa de cancelamento
        cancelled = len([a for a in recent_appts if a.status == AppointmentStatus.CANCELLED])
        total_scheduled = len(recent_appts)
        cancellation_rate = (cancelled / total_scheduled * 100) if total_scheduled > 0 else 0.0

        # Faturamento do mes
        dashboard_data = await invoice_repo.get_dashboard_data()
        revenue_month = dashboard_data.get("receita_centavos", 0)

        # Ticket medio
        paid_count = dashboard_data.get("total_faturas", 0)
        avg_ticket = revenue_month // paid_count if paid_count > 0 else 0

        # Taxa de aceitacao de tratamento (placeholder — precisa treatment repo)
        treatment_acceptance = 0.0

        kpis = [
            {
                "kpi_type": KPIType.PATIENTS_ACTIVE.value,
                "value": active_count,
                "label": "Pacientes Ativos",
                "formatted_value": str(active_count),
                "trend": None,
            },
            {
                "kpi_type": KPIType.APPOINTMENTS_TODAY.value,
                "value": appts_today,
                "label": "Consultas Hoje",
                "formatted_value": str(appts_today),
                "trend": None,
            },
            {
                "kpi_type": KPIType.REVENUE_MONTH.value,
                "value": revenue_month,
                "label": "Faturamento Mensal",
                "formatted_value": _format_currency(revenue_month),
                "trend": None,
            },
            {
                "kpi_type": KPIType.ATTENDANCE_RATE.value,
                "value": attendance_rate,
                "label": "Taxa de Comparecimento",
                "formatted_value": _format_percentage(attendance_rate),
                "trend": None,
            },
            {
                "kpi_type": KPIType.TREATMENT_ACCEPTANCE.value,
                "value": treatment_acceptance,
                "label": "Aceitacao de Tratamento",
                "formatted_value": _format_percentage(treatment_acceptance),
                "trend": None,
            },
            {
                "kpi_type": KPIType.AVG_TICKET.value,
                "value": avg_ticket,
                "label": "Ticket Medio",
                "formatted_value": _format_currency(avg_ticket),
                "trend": None,
            },
            {
                "kpi_type": KPIType.NEW_PATIENTS_MONTH.value,
                "value": new_patients_count,
                "label": "Novos Pacientes (Mes)",
                "formatted_value": str(new_patients_count),
                "trend": None,
            },
            {
                "kpi_type": KPIType.CANCELLATION_RATE.value,
                "value": cancellation_rate,
                "label": "Taxa de Cancelamento",
                "formatted_value": _format_percentage(cancellation_rate),
                "trend": None,
            },
        ]

        return kpis
