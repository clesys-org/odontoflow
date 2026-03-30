"""Pydantic v2 schemas for Insurance (TISS) endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class TISSItemRequest(BaseModel):
    tuss_code: str = Field(min_length=1)
    description: str = Field(min_length=2, max_length=500)
    tooth_number: Optional[int] = None
    quantity: int = Field(ge=1, default=1)


class CreateInsuranceProviderRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    ans_code: str = Field(min_length=1, max_length=20)


class SubmitTISSRequest(BaseModel):
    patient_id: str
    provider_id: str
    insurance_provider_id: str
    treatment_plan_id: Optional[str] = None
    items: list[TISSItemRequest] = Field(min_length=1)


class AuthorizeTISSRequest(BaseModel):
    authorization_number: str = Field(min_length=1, max_length=50)


class DenyTISSRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=500)


class BillTISSRequest(BaseModel):
    pass  # No body needed


class RecordTISSPaymentRequest(BaseModel):
    paid_amount_centavos: int = Field(ge=0)
    glosa_amount_centavos: int = Field(ge=0, default=0)
    glosa_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class TISSItemResponse(BaseModel):
    tuss_code: str
    description: str
    tooth_number: Optional[int] = None
    quantity: int
    authorized_quantity: Optional[int] = None


class InsuranceProviderResponse(BaseModel):
    id: str
    name: str
    ans_code: str
    active: bool


class InsuranceProvidersListResponse(BaseModel):
    providers: list[InsuranceProviderResponse]
    total: int


class TISSRequestResponse(BaseModel):
    id: str
    patient_id: str
    provider_id: str
    insurance_provider_id: str
    treatment_plan_id: Optional[str] = None
    items: list[TISSItemResponse]
    status: str
    authorization_number: Optional[str] = None
    submitted_at: Optional[str] = None
    authorized_at: Optional[str] = None
    denied_reason: Optional[str] = None
    billed_at: Optional[str] = None
    paid_at: Optional[str] = None
    paid_amount_centavos: int
    glosa_amount_centavos: int
    glosa_reason: Optional[str] = None
    created_at: str


class TISSRequestSummaryResponse(BaseModel):
    id: str
    patient_id: str
    insurance_provider_id: str
    status: str
    items_count: int
    paid_amount_centavos: int
    glosa_amount_centavos: int
    created_at: str


class TISSRequestsListResponse(BaseModel):
    requests: list[TISSRequestSummaryResponse]
    total: int
