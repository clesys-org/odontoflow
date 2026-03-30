"""Pydantic v2 schemas for Staff endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class CommissionRuleRequest(BaseModel):
    procedure_category: Optional[str] = None
    commission_type: str = "PERCENTAGE"
    value: int = Field(ge=0)


class CreateStaffRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    commission_rules: list[CommissionRuleRequest] = []


class UpdateStaffRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    active: Optional[bool] = None
    commission_rules: Optional[list[CommissionRuleRequest]] = None


class RecordProductionRequest(BaseModel):
    procedure_description: str = Field(min_length=2, max_length=500)
    revenue_centavos: int = Field(ge=0)
    patient_name: str = Field(min_length=2, max_length=200)
    date: str  # ISO date YYYY-MM-DD
    treatment_item_id: Optional[str] = None
    procedure_category: Optional[str] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class CommissionRuleResponse(BaseModel):
    procedure_category: Optional[str] = None
    commission_type: str
    value: int


class StaffResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    full_name: str
    cro_number: Optional[str] = None
    specialty: Optional[str] = None
    commission_rules: list[CommissionRuleResponse]
    active: bool
    created_at: str


class StaffListResponse(BaseModel):
    staff: list[StaffResponse]
    total: int


class ProductionEntryResponse(BaseModel):
    id: str
    staff_id: str
    procedure_description: str
    revenue_centavos: int
    commission_centavos: int
    patient_name: str
    date: str
    created_at: str


class ProductionReportResponse(BaseModel):
    staff_id: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_revenue_centavos: int
    total_commission_centavos: int
    entries_count: int
    entries: list[ProductionEntryResponse]
