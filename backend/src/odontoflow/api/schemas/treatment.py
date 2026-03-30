"""Pydantic v2 schemas for Treatment endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class TreatmentItemRequest(BaseModel):
    phase_number: int = 1
    phase_name: str = ""
    procedure_id: Optional[str] = None
    tuss_code: str = ""
    description: str = Field(min_length=1, max_length=500)
    tooth_number: Optional[int] = None
    surface: Optional[str] = None
    quantity: int = Field(default=1, ge=1)
    unit_price_centavos: int = Field(default=0, ge=0)
    sort_order: int = 0


class CreateTreatmentPlanRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    items: list[TreatmentItemRequest] = []
    discount_centavos: int = Field(default=0, ge=0)


class ApprovePlanRequest(BaseModel):
    approved_by: str = Field(min_length=1, max_length=255)


class ExecuteItemRequest(BaseModel):
    executed_by: str = Field(min_length=1, max_length=255)


class AddProcedureRequest(BaseModel):
    tuss_code: str = Field(min_length=1, max_length=20)
    description: str = Field(min_length=2, max_length=500)
    category: str = Field(default="", max_length=100)
    default_price_centavos: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TreatmentItemResponse(BaseModel):
    id: str
    phase_number: int
    phase_name: str
    procedure_id: Optional[str] = None
    tuss_code: str
    description: str
    tooth_number: Optional[int] = None
    surface: Optional[str] = None
    quantity: int
    unit_price_centavos: int
    status: str
    executed_at: Optional[str] = None
    executed_by: Optional[str] = None
    sort_order: int


class TreatmentPlanResponse(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    title: str
    status: str
    items: list[TreatmentItemResponse]
    total_value_centavos: int
    discount_centavos: int
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: str


class TreatmentPlanSummaryResponse(BaseModel):
    id: str
    patient_id: str
    title: str
    status: str
    items_count: int
    total_value_centavos: int
    created_at: str


class TreatmentPlansListResponse(BaseModel):
    plans: list[TreatmentPlanSummaryResponse]
    total: int


class ProcedureCatalogResponse(BaseModel):
    id: str
    tuss_code: str
    description: str
    category: str
    default_price_centavos: int
    active: bool


class ProceduresListResponse(BaseModel):
    procedures: list[ProcedureCatalogResponse]
    total: int
