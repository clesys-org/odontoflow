"""Analytics Bounded Context — Domain Models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID

from odontoflow.shared.domain.entity import AggregateRoot


class KPIType(str, Enum):
    PATIENTS_ACTIVE = "PATIENTS_ACTIVE"
    APPOINTMENTS_TODAY = "APPOINTMENTS_TODAY"
    REVENUE_MONTH = "REVENUE_MONTH"
    ATTENDANCE_RATE = "ATTENDANCE_RATE"
    TREATMENT_ACCEPTANCE = "TREATMENT_ACCEPTANCE"
    AVG_TICKET = "AVG_TICKET"
    NEW_PATIENTS_MONTH = "NEW_PATIENTS_MONTH"
    CANCELLATION_RATE = "CANCELLATION_RATE"


@dataclass(frozen=True)
class KPIValue:
    """Value Object — valor de um KPI."""

    kpi_type: KPIType = KPIType.PATIENTS_ACTIVE
    value: float = 0.0
    label: str = ""
    formatted_value: str = ""
    trend: Optional[str] = None  # "up", "down", "stable"


@dataclass
class ClinicReport(AggregateRoot):
    """Aggregate Root — relatorio da clinica para um periodo."""

    tenant_id: UUID = field(default=None)
    period_start: date = field(default=None)
    period_end: date = field(default=None)
    kpis: list[KPIValue] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_kpi(self, kpi_type: KPIType) -> Optional[KPIValue]:
        """Retorna KPI especifico pelo tipo."""
        for kpi in self.kpis:
            if kpi.kpi_type == kpi_type:
                return kpi
        return None
