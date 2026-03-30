"""Pydantic v2 schemas for Analytics endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class KPIResponse(BaseModel):
    kpi_type: str
    value: float
    label: str
    formatted_value: str
    trend: Optional[str] = None


class DashboardKPIsResponse(BaseModel):
    kpis: list[KPIResponse]


class ClinicReportResponse(BaseModel):
    tenant_id: str
    period_start: str
    period_end: str
    kpis: list[KPIResponse]
    generated_at: str
