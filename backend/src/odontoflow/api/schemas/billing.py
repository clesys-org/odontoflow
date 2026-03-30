"""Pydantic v2 schemas for Billing endpoints."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------


class InstallmentRequest(BaseModel):
    number: int = Field(ge=1)
    due_date: str  # ISO date YYYY-MM-DD
    amount_centavos: int = Field(ge=1)


class CreateInvoiceRequest(BaseModel):
    treatment_plan_id: Optional[str] = None
    description: str = Field(min_length=2, max_length=500)
    total_centavos: int = Field(ge=1)
    installments: list[InstallmentRequest] = []


class PayInstallmentRequest(BaseModel):
    installment_number: int = Field(ge=1)
    payment_method: str = "PIX"  # PaymentMethod enum value


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class InstallmentResponse(BaseModel):
    id: str
    number: int
    due_date: Optional[str] = None
    amount_centavos: int
    payment_method: Optional[str] = None
    status: str
    paid_at: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: str
    patient_id: str
    treatment_plan_id: Optional[str] = None
    description: str
    total_centavos: int
    status: str
    installments: list[InstallmentResponse]
    amount_paid_centavos: int
    amount_remaining_centavos: int
    created_at: str


class InvoiceSummaryResponse(BaseModel):
    id: str
    patient_id: str
    description: str
    total_centavos: int
    status: str
    amount_paid_centavos: int
    installments_count: int
    created_at: str


class InvoicesListResponse(BaseModel):
    invoices: list[InvoiceSummaryResponse]
    total: int


class FinanceDashboardResponse(BaseModel):
    receita_centavos: int
    a_receber_centavos: int
    total_faturas: int
