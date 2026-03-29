"""Pydantic v2 schemas for Patient endpoints."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class AddressRequest(BaseModel):
    street: str = ""
    number: str = ""
    complement: str = ""
    neighborhood: str = ""
    city: str = ""
    state: str = Field("", max_length=2)
    zip_code: str = Field("", pattern=r"^\d{8}$")


class ResponsibleRequest(BaseModel):
    name: str
    cpf: str
    relationship: str
    phone: str


class InsuranceInfoRequest(BaseModel):
    provider_name: str
    plan_name: str = ""
    card_number: str = ""
    valid_until: Optional[date] = None


class CreatePatientRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=255)
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$")
    birth_date: Optional[date] = None
    gender: str = "NOT_INFORMED"
    marital_status: Optional[str] = None
    profession: Optional[str] = None
    phone: Optional[str] = Field(None, pattern=r"^\d{10,11}$")
    whatsapp: Optional[str] = Field(None, pattern=r"^\d{10,11}$")
    email: Optional[str] = None
    preferred_channel: str = "WHATSAPP"
    address: Optional[AddressRequest] = None
    responsible: Optional[ResponsibleRequest] = None
    insurance_info: Optional[InsuranceInfoRequest] = None
    referral_source: Optional[str] = None
    tags: list[str] = []
    notes: Optional[str] = None


class UpdatePatientRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$")
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    profession: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    preferred_channel: Optional[str] = None
    address: Optional[AddressRequest] = None
    responsible: Optional[ResponsibleRequest] = None
    insurance_info: Optional[InsuranceInfoRequest] = None
    referral_source: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class PatientResponse(BaseModel):
    id: str
    full_name: str
    cpf: Optional[str] = None
    cpf_formatted: Optional[str] = None
    birth_date: Optional[str] = None
    age: Optional[int] = None
    gender: str
    marital_status: Optional[str] = None
    profession: Optional[str] = None
    phone: Optional[str] = None
    phone_formatted: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    preferred_channel: str
    address: Optional[dict] = None
    responsible: Optional[dict] = None
    insurance_info: Optional[dict] = None
    referral_source: Optional[str] = None
    tags: list[str] = []
    notes: Optional[str] = None
    status: str
    is_minor: bool = False
    created_at: str
    updated_at: str


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AddressFromCEPResponse(BaseModel):
    street: str
    neighborhood: str
    city: str
    state: str
    zip_code: str
